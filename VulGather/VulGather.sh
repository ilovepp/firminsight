#!/bin/bash

eval `tail -n +2 ../GLOBAL_CONFIG`

function mongocmd(){
	echo "`echo $1|mongo ${MONGO_IP}:${MONGO_PORT}/${MONGO_DATABASE} --quiet --shell 2>/dev/null`"
}

function mongo_update(){
    mongo_cmd="db.${MONGO_VUL_COLLECTION_NAME}.update({binMD5:\"$1\"},{\$set:{$2:\"$3\"}});"
    #echo $mongo_cmd
    echo "$mongo_cmd"|mongo ${MONGO_IP}:${MONGO_PORT}/${MONGO_DATABASE} --quiet --shell >/dev/null 2>&1			
}

if [ $# != 2 ] || [ ! -f "$1"  ] || [ ! -f "$2"  ];then
    echo "USAGE:$0 vul_bin_path vul_info_path "
    exit 1
fi

declare -i fileid=$(ls $VUL_BINARY_STORE_PATH |awk -F_ '{print $1}'|sort -n|tail -1)

declare -i vulID=`mongocmd "db.${MONGO_VUL_COLLECTION_NAME}.find({},{vulID:1,_id:0}).sort({vulID:-1}).limit(1);"|awk '{print $4}'|tail -1`

binName="${1##*/}"

binMD5=$(md5sum "$1"|awk '{print $1}')	
[ `mongocmd "db.${MONGO_VUL_COLLECTION_NAME}.findOne({binMD5:\"${binMD5}\"});"|tail -1` != "null" ] && echo "${binName} has already in database" && exit 1


binInstSet="unknown"
../BinGather/isdetect.py "$1" >>/dev/null
case $? in
	0) binInstSet="unknown";;			
	1) binInstSet="MIPS-Little";;
	2) binInstSet="MIPS-Big";;
	3) binInstSet="ARM-Little";;
	4) binInstSet="ARM-Big";;
	5) binInstSet="PowerPC-Big";;
	6) binInstSet="PowerPC-Little";;
esac		

if [ "$binInstSet" = "unknown" ] && [ -n "`file "$1"|grep ELF`" ];then
	temp=0
	if [ -n "`file "$1"|grep MIPS`" ];then
		temp=1
		[ -n "`file "$1"|grep MSB`" ] && temp=2
	elif [ -n "`file "$1"|grep ARM`" ];then
		temp=3
    	[ -n "`file "$1"|grep MSB`" ] && temp=4
	elif [ -n "`file "$1"|grep -E "ppc|PowerPC"`" ];then
		temp=5
		[ -n "`file "$1"|grep LSB`" ] && temp=6
    fi
    case $temp in
        0) binInstSet="unknown";;			
	    1) binInstSet="MIPS-Little";;
	    2) binInstSet="MIPS-Big";;
	    3) binInstSet="ARM-Little";;
	    4) binInstSet="ARM-Big";;
	    5) binInstSet="PowerPC-Big";;
	    6) binInstSet="PowerPC-Little";;
    esac
fi
echo $binInstSet
((vulID++))
vulID=3
mongocmd "db.${MONGO_VUL_COLLECTION_NAME}.insert({vulID:${vulID},binName:\"${binName}\",binMD5:\"${binMD5}\"})"
((fileid++))
cp "$1"  ${VUL_BINARY_STORE_PATH}/${fileid}_${binName}

mongo_update $binMD5 "binSave" "${fileid}_${binName}"

OLD_IFS="$IFS"
IFS=$(echo -e "\n\b")
for line in $(cat $2)
do
    eval "mongo_update $binMD5 $line"
done
IFS="$OLD_IFS"

mongo_update $binMD5 binInstSet $binInstSet







