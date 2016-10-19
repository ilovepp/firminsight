#!/bin/bash
eval `tail -n +2 ../GLOBAL_CONFIG`
eval `tail -n +2 CONFIG`
target_firm_id=$1
target_bin="$2"
target_firm_id_2=$3

if [ $# != 3 ];then
    echo "USAGE:$0 target_firm_id target_bin target_firm_id_2"
    exit 1
fi

mongo_cmd="db.${MONGO_FIRM_COLLECTION_NAME}.find({firmID:${target_firm_id},\"binFiles.binName\":\"${target_bin}\"},{binFiles:1,_id:0}).toArray();"
mongo_return=$(echo "$mongo_cmd"|mongo ${MONGO_IP}:${MONGO_PORT}/${MONGO_DATABASE} --quiet --shell 2>/dev/null|grep -E "\"binName\" :|\"ssdeep\" :")
[ -z "$mongo_return" ] && echo "firmID:${target_firm_id}'s binName:${target_bin} not in the database!" && exit
bin_list_content=$(echo $mongo_return|sed -e 's/, /\n/g' -e 's/ \"binName\"/\n\"binName\"/g'|grep "\"binName\""|awk -F: '{print $2}'|sed -e 's/^[ \t]*//g' -e 's/[ \t]*$//g' -e 's/ /\@_\@/g')
ssdeep_list_content=$(echo $mongo_return|sed -e 's/, /\n/g' -e 's/ \"binName\"/\n\"binName\"/g'|grep "\"ssdeep\""|awk -F " : " '{print $2}'|sed -e 's/\\\"/\"/g' -e 's/\"$//g' -e 's/^\"//g' -e 's/ /\@_\@/g')
for line in `echo "$bin_list_content"`
do
bin_name_list[$bin_index]=$line
((bin_index++))
done
for line in `echo "$ssdeep_list_content"`
do
ssdeep_list[$ssdeep_index]=$line
((ssdeep_index++))
done	
for ((i=0;i<${#bin_name_list[@]};i++))
do
[ "${bin_name_list[i]}" != "\"${target_bin}\"" ] && continue
echo "${ssdeep_list[i]}"|sed 's/\@_\@/\n/g' > ${DECOMPRESS_TEMP_PATH}/${target_bin}.ssdeep
break
done
#{$or:[{manufacturer:"Abb"},{manufacturer:"Rockwell"}],binFileCount:{$gt:0}}
#for manufacturer in ${manufacturer_LIST[@]};do
#TEMP="{manufacturer:\"$manufacturer\"},$TEMP"	
#done
#TEMP="{manufacturer:\"Abb\"},{manufacturer:\"Rockwell\"}"
#echo $TEMP
#CONDITION="{\$or:[$TEMP],binFileCount:{\$gt:0}}"
#mongo_cmd="db.${MONGO_FIRM_COLLECTION_NAME}.count(${CONDITION});"
#firmnum=$(echo "$mongo_cmd"|mongo ${MONGO_IP}:${MONGO_PORT}/${MONGO_DATABASE} --quiet --shell 2>/dev/null|tail -1)
#((firmnum--))
#for index in `seq 0 $firmnum`
#do
#echo "***********************************************"



mongo_cmd="db.${MONGO_FIRM_COLLECTION_NAME}.find({firmID:${target_firm_id_2}},{binFiles:1,_id:0}).toArray();"

mongo_return=$(echo "$mongo_cmd"|mongo ${MONGO_IP}:${MONGO_PORT}/${MONGO_DATABASE} --quiet --shell 2>/dev/null|grep -E "\"binName\" :|\"ssdeep\" :|\"manufacturer\" :|\"firmID\" :|\"firmName\" :|\"binFileCount\" :")
[ -z "$mongo_return" ] && echo "firmID:${target_firm_id_2} not in the database!" && exit
#echo "$mongo_return"
binFileCount=$(echo "$mongo_return"|grep "\"binFileCount\""|awk -F: '{print $2}'|sed -e 's/ //g' -e 's/,//g')
#echo "firmID:$firmID"
#echo "target_firm_id:$target_firm_id"
#echo $firmID
#echo "firmName:$firmName"
#echo "manufacturer:$manufacturer"
#echo "binFileCount:$binFileCount"
unset bin_name_list
unset ssdeep_list
declare -a bin_name_list
declare -a ssdeep_list
bin_index=0
ssdeep_index=0
bin_list_content=$(echo $mongo_return|sed -e 's/, /\n/g' -e 's/ \"binName\"/\n\"binName\"/g'|grep "\"binName\""|awk -F: '{print $2}'|sed -e 's/^[ \t]*//g' -e 's/[ \t]*$//g' -e 's/ /\@_\@/g')
ssdeep_list_content=$(echo $mongo_return|sed -e 's/, /\n/g' -e 's/ \"binName\"/\n\"binName\"/g'|grep "\"ssdeep\""|awk -F " : " '{print $2}'|sed -e 's/\\\"/\"/g' -e 's/\"$//g' -e 's/^\"//g' -e 's/ /\@_\@/g')
#echo "$bin_list_content"
#echo "$ssdeep_list_content"
for line in `echo "$bin_list_content"`
do
bin_name_list[$bin_index]=$line
((bin_index++))
done
for line in `echo "$ssdeep_list_content"`
do
ssdeep_list[$ssdeep_index]=$line
((ssdeep_index++))
done
for ((i=0;i<${#bin_name_list[@]};i++))
do
#echo "${bin_name_list[i]}"
echo "${ssdeep_list[i]}"|sed 's/\@_\@/\n/g' > ${DECOMPRESS_TEMP_PATH}/${temp_bin}.ssdeep
similarity=`ssdeep -s -a -x ${DECOMPRESS_TEMP_PATH}/${target_bin}.ssdeep ${DECOMPRESS_TEMP_PATH}/${temp_bin}.ssdeep 2>>/dev/null |head -1|grep -oP '(?<=\()[^\)>]+'`
rm ${DECOMPRESS_TEMP_PATH}/${temp_bin}.ssdeep
[ ${similarity}0 -ge ${THRESHOLD}0 ] && echo "${bin_name_list[i]}:${similarity}"
done
rm ${DECOMPRESS_TEMP_PATH}/${target_bin}.ssdeep



