#!/bin/bash
eval `tail -n +2 ../GLOBAL_CONFIG`
eval `tail -n +2 CONFIG`
target_firm_id=$1
target_bin="$2"
#echo "serach similar binarys of FirmID:${target_firm_id}'s BinName:${target_bin}"
mongo_cmd="db.${MONGO_FIRM_COLLECTION_NAME}.find({FirmID:${target_firm_id},\"BinFiles.BinName\":\"${target_bin}\"},{BinFiles:1,_id:0}).toArray();"
mongo_return=$(echo "$mongo_cmd"|mongo ${MONGO_IP}:${MONGO_PORT}/${MONGO_DATABASE} --quiet --shell 2>/dev/null|grep -E "\"BinName\" :|\"ssdeep\" :")
[ -z "$mongo_return" ] && echo "FirmID:${target_firm_id}'s BinName:${target_bin} not in the database!" && exit
bin_list_content=$(echo $mongo_return|sed -e 's/, /\n/g' -e 's/ \"BinName\"/\n\"BinName\"/g'|grep "\"BinName\""|awk -F: '{print $2}'|sed -e 's/^[ \t]*//g' -e 's/[ \t]*$//g' -e 's/ /\@_\@/g')
ssdeep_list_content=$(echo $mongo_return|sed -e 's/, /\n/g' -e 's/ \"BinName\"/\n\"BinName\"/g'|grep "\"ssdeep\""|awk -F " : " '{print $2}'|sed -e 's/\\\"/\"/g' -e 's/\"$//g' -e 's/^\"//g' -e 's/ /\@_\@/g')
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
#{$or:[{Manufacturer:"Abb"},{Manufacturer:"Rockwell"}],BinFileCount:{$gt:0}}
for manufacturer in ${MANUFACTURER_LIST[@]};do
TEMP="{Manufacturer:\"$manufacturer\"},$TEMP"	
done
#TEMP="{Manufacturer:\"Abb\"},{Manufacturer:\"Rockwell\"}"
#echo $TEMP
CONDITION="{\$or:[$TEMP],BinFileCount:{\$gt:0}}"
mongo_cmd="db.${MONGO_FIRM_COLLECTION_NAME}.count(${CONDITION});"
firmnum=$(echo "$mongo_cmd"|mongo ${MONGO_IP}:${MONGO_PORT}/${MONGO_DATABASE} --quiet --shell 2>/dev/null|tail -1)
((firmnum--))
for index in `seq 0 $firmnum`
do
#echo "***********************************************"
mongo_cmd="db.${MONGO_FIRM_COLLECTION_NAME}.find(${CONDITION},{Manufacturer:1,FirmID:1,FirmName:1,BinFileCount:1,BinFiles:1,_id:0}).limit(1).skip(${index}).toArray();"
mongo_return=$(echo "$mongo_cmd"|mongo ${MONGO_IP}:${MONGO_PORT}/${MONGO_DATABASE} --quiet --shell 2>/dev/null|grep -E "\"BinName\" :|\"ssdeep\" :|\"Manufacturer\" :|\"FirmID\" :|\"FirmName\" :|\"BinFileCount\" :")
#echo "$mongo_return"
FirmName=$(echo "$mongo_return"|grep "\"FirmName\""|awk -F\" '{print $4}')
FirmID=$(echo "$mongo_return"|grep "\"FirmID\""|awk -F: '{print $2}'|sed -e 's/ //g' -e 's/,//g')
Manufacturer=$(echo "$mongo_return"|grep "\"Manufacturer\""|awk -F\" '{print $4}')
BinFileCount=$(echo "$mongo_return"|grep "\"BinFileCount\""|awk -F: '{print $2}'|sed -e 's/ //g' -e 's/,//g')
#echo "FirmID:$FirmID"
#echo "target_firm_id:$target_firm_id"
#echo $FirmID
[ "$FirmID" -eq "$target_firm_id" ] && continue
#echo "FirmName:$FirmName"
#echo "Manufacturer:$Manufacturer"
#echo "BinFileCount:$BinFileCount"
unset bin_name_list
unset ssdeep_list
declare -a bin_name_list
declare -a ssdeep_list
bin_index=0
ssdeep_index=0
bin_list_content=$(echo $mongo_return|sed -e 's/, /\n/g' -e 's/ \"BinName\"/\n\"BinName\"/g'|grep "\"BinName\""|awk -F: '{print $2}'|sed -e 's/^[ \t]*//g' -e 's/[ \t]*$//g' -e 's/ /\@_\@/g')
ssdeep_list_content=$(echo $mongo_return|sed -e 's/, /\n/g' -e 's/ \"BinName\"/\n\"BinName\"/g'|grep "\"ssdeep\""|awk -F " : " '{print $2}'|sed -e 's/\\\"/\"/g' -e 's/\"$//g' -e 's/^\"//g' -e 's/ /\@_\@/g')
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
echo "${ssdeep_list[i]}"|sed 's/\@_\@/\n/g' > ${DECOMPRESS_TEMP_PATH}/${temp_bin}.ssdeep
similarity=`ssdeep -s -a -x ${DECOMPRESS_TEMP_PATH}/${target_bin}.ssdeep ${DECOMPRESS_TEMP_PATH}/${temp_bin}.ssdeep 2>>/dev/null |head -1|grep -oP '(?<=\()[^\)>]+'`
rm ${DECOMPRESS_TEMP_PATH}/${temp_bin}.ssdeep
[ ${similarity}0 -ge ${THRESHOLD}0 ] && echo "${FirmID}:${Manufacturer}:${FirmName}:${bin_name_list[i]}:${similarity}"
done
done
rm ${DECOMPRESS_TEMP_PATH}/${target_bin}.ssdeep
