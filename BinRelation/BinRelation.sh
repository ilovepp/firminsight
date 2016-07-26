#!/bin/bash

eval `tail -n +2 ../GLOBAL_CONFIG`
eval `tail -n +2 ../BinGather/CONFIG`

mongo_cmd="db.${MONGO_FIRM_COLLECTION_NAME}.count({BinFileCount:{\$gt:0}});"
firmnum=$(echo "$mongo_cmd"|mongo ${MONGO_IP}:${MONGO_PORT}/${MONGO_DATABASE} --quiet --shell 2>/dev/null|tail -1)
((firmnum--))
for index in `seq 0 $firmnum`
do
	echo "***********************************************"
	mongo_cmd="db.${MONGO_FIRM_COLLECTION_NAME}.find({BinFileCount:{\$gt:0}},{Manufacturer:1,FirmID:1,FirmName:1,BinFileCount:1,BinFiles:1,_id:0}).limit(1).skip(${index}).toArray();"
	mongo_return=$(echo "$mongo_cmd"|mongo ${MONGO_IP}:${MONGO_PORT}/${MONGO_DATABASE} --quiet --shell 2>/dev/null|grep -E "\"BinName\" :|\"ssdeep\" :|\"Manufacturer\" :|\"FirmID\" :|\"FirmName\" :|\"BinFileCount\" :")

	FirmID=$(echo $mongo_return|awk -F, '{print $1}'|awk -F: '{print $2}'|sed -e 's/^[ \t]*//g' -e 's/[ \t]*$//g')
	echo "FirmID:$FirmID"

	FirmName=$(echo $mongo_return|awk -F, '{print $2}'|awk -F: '{print $2}'|sed -e 's/^[ \t]*//g' -e 's/[ \t]*$//g')
	echo "FirmName:$FirmName"

	Manufacturer=$(echo $mongo_return|awk -F, '{print $3}'|awk -F: '{print $2}'|sed -e 's/^[ \t]*//g' -e 's/[ \t]*$//g')
	echo "Manufacturer:$Manufacturer"
	
	BinFileCount=$(echo $mongo_return|awk -F, '{print $4}'|awk -F: '{print $2}'|sed -e 's/^[ \t]*//g' -e 's/[ \t]*$//g')
	echo "BinFileCount:$BinFileCount"
	
	unset bin_name_list
	unset ssdeep_list
	declare -a bin_name_list
	declare -a ssdeep_list
	bin_index=0
	ssdeep_index=0
	
	echo $mongo_return|sed -e 's/, /\n/g' -e 's/ \"BinName\"/\n\"BinName\"/g'|grep "\"BinName\""|awk -F: '{print $2}'|sed -e 's/^[ \t]*//g' -e 's/[ \t]*$//g'| while read line;do bin_name_list[$bin_index]="$line";((bin_index++));done
	#echo $mongo_return|sed -e 's/, /\n/g' -e 's/ \"BinName\"/\n\"BinName\"/g'|grep "\"ssdeep\""|awk -F " : " '{print $2}'|sed -e 's/\\\"/\"/g' -e 's/\"$//g' -e 's/^\"//g'| while read line;do echo $line;done
	echo ${bin_name_list[0]}
	#echo ${bin_name_list[@]}
	#echo ${ssdeep_list[@]}

done
			
	
			
	
	
	
