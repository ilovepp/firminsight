#!/bin/bash
eval `tail -n +2 ../GLOBAL_CONFIG`

function mongocmd(){
	echo "`echo $1|mongo ${MONGO_IP}:${MONGO_PORT}/${MONGO_DATABASE} --quiet --shell 2>/dev/null`"
}

function mongo_update(){
    mongo_cmd="db.${MONGO_FIRM_COLLECTION_NAME}.update({FirmName:\"$1\"},{\$set:{$2:\"$3\"}});"
    echo $mongo_cmd
    echo "$mongo_cmd"|mongo ${MONGO_IP}:${MONGO_PORT}/${MONGO_DATABASE} --quiet --shell >/dev/null 2>&1			
}

firmnum="`mongocmd "db.${MONGO_FIRM_COLLECTION_NAME}.count()"|tail -1`"
echo $firmnum
((firmnum--))
for index in `seq 0 $firmnum`
do
	
	mongo_cmd="db.${MONGO_FIRM_COLLECTION_NAME}.find({},{FirmName:1,_id:0}).limit(1).skip(${index}).toArray();"
	mongo_return=$(echo "$mongo_cmd"|mongo ${MONGO_IP}:${MONGO_PORT}/${MONGO_DATABASE} --quiet --shell 2>/dev/null|grep "\"FirmName\"")
	FirmName=$(echo $mongo_return|awk -F\" '{print $4}')
    echo $FirmName
    mongo_cmd="db.${MONGO_SCRAPY_COLLECTION_NAME}.find({FirmwareName:\"$FirmName\"},{URL:1,PackedTime:1,Description:1,ProductModel:1,ScrapyTime:1,ProductVersion:1,PublishTime:1,_id:0}).toArray();"
	mongo_return="`echo "$mongo_cmd"|mongo ${MONGO_IP}:${MONGO_PORT}/${MONGO_DATABASE} --quiet --shell 2>/dev/null`"
    URL=$(echo "$mongo_return"|grep "\"URL\""|awk -F\" '{print $4}')
    PackedTime=$(echo "$mongo_return"|grep "\"PackedTime\""|awk -F\" '{print $4}')
    Description=$(echo "$mongo_return"|grep "\"Description\""|awk -F\" '{print $4}')
    ProductModel=$(echo "$mongo_return"|grep "\"ProductModel\""|awk -F\" '{print $4}')
    ScrapyTime=$(echo "$mongo_return"|grep "\"ScrapyTime\""|awk -F\" '{print $4}')
    ProductVersion=$(echo "$mongo_return"|grep "\"ProductVersion\""|awk -F\" '{print $4}')
    PublishTime=$(echo "$mongo_return"|grep "\"PublishTime\""|awk -F\" '{print $4}')
    [ -n "$URL" ] &&  echo "URL:$URL" && mongo_update "$FirmName" "URL" "$URL"
    [ -n "$Description" ] &&  echo "Description:$Description" && mongo_update "$FirmName" "Description" "$Description"
    [ -n "$ProductModel" ] &&  echo "ProductModel:$ProductModel" && mongo_update "$FirmName" "ProductModel" "$ProductModel"
    [ -n "$ProductVersion" ] &&  echo "ProductVersion:$ProductVersion" && mongo_update "$FirmName" "ProductVersion" "$ProductVersion"
    [ -n "$PublishTime" ] &&  echo "PublishTime:$PublishTime" && mongo_update "$FirmName" "PublishTime"  "$PublishTime"
    [ -n "$PackedTime" ] &&  echo "PackedTime:$PackedTime"  && mongo_update "$FirmName" "PackedTime" "$PackedTime"
    [ -n "$ScrapyTime" ] &&  echo "ScrapyTime:$ScrapyTime" && mongo_update "$FirmName" "ScrapyTime" "$ScrapyTime"
done

