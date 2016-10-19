#!/bin/bash

eval `tail -n +2 ../GLOBAL_CONFIG`
eval `tail -n +2 CONFIG`

OLD_IFS="$IFS"
IFS=" "
plugins=("`ls Plugin`")
IFS="$OLD_IFS"

mongo_cmd="db.${MONGO_FIRM_COLLECTION_NAME}.count();"
firmnum=$(echo "$mongo_cmd"|mongo ${MONGO_IP}:${MONGO_PORT}/${MONGO_DATABASE} --quiet --shell 2>/dev/null|tail -1)
((firmnum--))
for index in `seq 0 $firmnum`
do
	mongo_cmd="db.${MONGO_FIRM_COLLECTION_NAME}.find({},{manufacturer:1,firmID:1,firmName:1,binFileCount:1,binFiles:1,_id:0}).limit(1).skip(${index}).toArray();"
	mongo_return=$(echo "$mongo_cmd"|mongo ${MONGO_IP}:${MONGO_PORT}/${MONGO_DATABASE} --quiet --shell 2>/dev/null|grep -E "\"binName\" :|\"binSave\" :|\"manufacturer\" :|\"firmID\" :|\"firmName\" :|\"binFileCount\" :")

    firmName=$(echo "$mongo_return"|grep "\"firmName\""|awk -F\" '{print $4}')
    firmID=$(echo "$mongo_return"|grep "\"firmID\""|awk -F: '{print $2}'|sed -e 's/ //g' -e 's/,//g')
    manufacturer=$(echo "$mongo_return"|grep "\"manufacturer\""|awk -F\" '{print $4}')
    binFileCount=$(echo "$mongo_return"|grep "\"binFileCount\""|awk -F: '{print $2}'|sed -e 's/ //g' -e 's/,//g')
    echo $index:"$firmName"
	unset bin_name_list
	unset bin_save_list
	declare -a bin_name_list
	declare -a bin_save_list
	bin_index=0
	save_index=0
	#bin_list_content=$(echo $mongo_return|sed -e 's/, /\n/g' -e 's/ \"binName\"/\n\"binName\"/g'|grep "\"binName\""|awk -F: '{print $2}'|sed -e 's/^[ \t]*//g' -e 's/[ \t]*$//g' -e 's/ /\@_\@/g')
	#bin_save_content=$(echo $mongo_return|sed -e 's/, /\n/g' -e 's/ \"binSave\"/\n\"binSave\"/g'|grep "\"binSave\""|awk -F: '{print $2}'|sed -e 's/^[ \t]*//g' -e 's/[ \t]*$//g' -e 's/ /\@_\@/g')
    bin_list_content=$(echo $mongo_return|sed -e 's/, /\n/g' -e 's/ \"binName\"/\n\"binName\"/g'|grep "\"binName\""|awk -F\" '{print $4}')
    bin_save_content=$(echo $mongo_return|sed -e 's/, /\n/g' -e 's/ \"binSave\"/\n\"binSave\"/g'|grep "\"binSave\""|awk -F\" '{print $4}')
    
	for line in `echo "$bin_list_content"`
	do
		bin_name_list[$bin_index]=$line
		((bin_index++))
	done
	
	for line in `echo "$bin_save_content"`
	do
		bin_save_list[$save_index]=$line
		((save_index++))
	done

	for ((i=0;i<${#bin_name_list[@]};i++))
	do
		for plugin in ${plugins[@]}
		do
            BinPath=${BINARY_STORE_PATH}/${bin_save_list[i]}
			content=$(Plugin/$plugin "$BinPath")
			[ -z "$content" ] && continue
			mongo_cmd="db.firmwares.update({firmID:${firmID},\"binFiles.binName\":\"${bin_name_list[i]}\"},{\$set:{\"binFiles.$.${plugin}\":'${content}'}})"
			echo "$mongo_cmd"|mongo ${MONGO_IP}:${MONGO_PORT}/${MONGO_DATABASE} --quiet --shell >/dev/null 2>&1						
		done
	done
done


