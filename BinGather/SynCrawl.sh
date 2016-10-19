#!/bin/bash
eval `tail -n +2 ../GLOBAL_CONFIG`

function mongocmd(){
	echo "`echo $1|mongo ${MONGO_IP}:${MONGO_PORT}/${MONGO_DATABASE} --quiet --shell 2>/dev/null`"
}

function mongo_update(){
    mongo_cmd="db.${MONGO_FIRM_COLLECTION_NAME}.update({firmName:\"$1\"},{\$set:{$2:\"$3\"}});"
    #echo $mongo_cmd
    echo "$mongo_cmd"|mongo ${MONGO_IP}:${MONGO_PORT}/${MONGO_DATABASE} --quiet --shell >/dev/null 2>&1			
}

firmnum=`mongocmd "db.${MONGO_FIRM_COLLECTION_NAME}.count()"|tail -1`
echo $firmnum
((firmnum--))
for index in `seq 0 $firmnum`
do
	
    mongo_cmd="db.${MONGO_FIRM_COLLECTION_NAME}.find({},{firmName:1,_id:0}).limit(1).skip(${index}).toArray();"
	mongo_return=`echo "$mongo_cmd"|mongo ${MONGO_IP}:${MONGO_PORT}/${MONGO_DATABASE} --quiet --shell 2>/dev/null`
    firmName=$(echo "$mongo_return"|grep "\"firmName\""|awk -F\" '{print $4}')
    echo $index $firmName
    mongo_cmd="db.${MONGO_SCRAPY_COLLECTION_NAME}.find({firmwareName:\"$firmName\"},{uRL:1,packedTime:1,description:1,productModel:1,scrapyTime:1,productVersion:1,publishTime:1,productClass:1,_id:0}).toArray();"
	mongo_return="`echo "$mongo_cmd"|mongo ${MONGO_IP}:${MONGO_PORT}/${MONGO_DATABASE} --quiet --shell 2>/dev/null`"
    uRL=$(echo "$mongo_return"|grep "\"uRL\""|awk -F\" '{print $4}')
    packedTime=$(echo "$mongo_return"|grep "\"packedTime\""|awk -F\" '{print $4}')
    description=$(echo "$mongo_return"|grep "\"description\""|awk -F\" '{print $4}')
    productModel=$(echo "$mongo_return"|grep "\"productModel\""|awk -F\" '{print $4}')
    scrapyTime=$(echo "$mongo_return"|grep "\"scrapyTime\""|awk -F\" '{print $4}')
    productVersion=$(echo "$mongo_return"|grep "\"productVersion\""|awk -F\" '{print $4}')
    publishTime=$(echo "$mongo_return"|grep "\"publishTime\""|awk -F\" '{print $4}')
    productClass=$(echo "$mongo_return"|grep "\"productClass\""|awk -F\" '{print $4}')
    [ -n "$uRL" ] && mongo_update "$firmName" "uRL" "$uRL"
    [ -n "$description" ] && mongo_update "$firmName" "description" "$description"
    [ -n "$productModel" ] && mongo_update "$firmName" "productModel" "$productModel"
    [ -n "$productVersion" ] && mongo_update "$firmName" "productVersion" "$productVersion"
    [ -n "$publishTime" ] && mongo_update "$firmName" "publishTime"  "$publishTime"
    [ -n "$packedTime" ] &&mongo_update "$firmName" "packedTime" "$packedTime"
    [ -n "$scrapyTime" ] && mongo_update "$firmName" "scrapyTime" "$scrapyTime"
    [ -n "$productClass" ] && mongo_update "$firmName" "productClass" "$productClass"
done

