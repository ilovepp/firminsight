#!/bin/bash

eval `tail -n +2 ../GLOBAL_CONFIG`

function mongocmd(){
	echo "`echo $1|mongo ${MONGO_IP}:${MONGO_PORT}/${MONGO_DATABASE} --quiet --shell 2>/dev/null`"
}

function mongo_update(){
    mongo_cmd="db.${MONGO_FIRM_COLLECTION_NAME}.update({BinMD5:\"$1\"},{\$set:{$2:\"$3\"}});"
    #echo $mongo_cmd
    echo "$mongo_cmd"|mongo ${MONGO_IP}:${MONGO_PORT}/${MONGO_DATABASE} --quiet --shell >/dev/null 2>&1			
}

declare -i fileid=$(ls $VUL_BINARY_STORE_PATH |awk -F_ '{print $1}'|sort -n|tail -1)

echo $fileid

declare -i VulID=`mongocmd "db.${MONGO_VUL_COLLECTION_NAME}.find({},{VulID:1,_id:0}).sort({VulID:-1}).limit(1);"|awk '{print $4}'|tail -1`

echo $VulID

BinName="${1##*/}"

BinMD5=$(md5sum "$1"|awk '{print $1}')	
echo $BinMD5
#mongo_cmd="db.${MONGO_FIRM_COLLECTION_NAME}.findOne({FirmMD5:\"${FirmMD5}\"});"
#[ $(echo "$mongo_cmd"|mongo ${MONGO_IP}:${MONGO_PORT}/${MONGO_DATABASE} --quiet --shell 2>/dev/null|tail -1) != "null" ] && echo "${FirmPath} has already in database" && return 




