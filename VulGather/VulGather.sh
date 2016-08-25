#!/bin/bash

eval `tail -n +2 ../GLOBAL_CONFIG`

function mongocmd(){
	echo "`echo $1|mongo ${MONGO_IP}:${MONGO_PORT}/${MONGO_DATABASE} --quiet --shell 2>/dev/null`"
}

function mongo_update(){
    mongo_cmd="db.${MONGO_VUL_COLLECTION_NAME}.update({BinMD5:\"$1\"},{\$set:{$2:\"$3\"}});"
    #echo $mongo_cmd
    echo "$mongo_cmd"|mongo ${MONGO_IP}:${MONGO_PORT}/${MONGO_DATABASE} --quiet --shell >/dev/null 2>&1			
}

if [ $# != 2 ] || [ ! -f "$1"  ] || [ ! -f "$2"  ];then
    echo "USAGE:$0 vul_bin_path vul_info_path "
    exit 1
fi

declare -i fileid=$(ls $VUL_BINARY_STORE_PATH |awk -F_ '{print $1}'|sort -n|tail -1)

declare -i VulID=`mongocmd "db.${MONGO_VUL_COLLECTION_NAME}.find({},{VulID:1,_id:0}).sort({VulID:-1}).limit(1);"|awk '{print $4}'|tail -1`

BinName="${1##*/}"

BinMD5=$(md5sum "$1"|awk '{print $1}')	
[ `mongocmd "db.${MONGO_VUL_COLLECTION_NAME}.findOne({BinMD5:\"${BinMD5}\"});"|tail -1` != "null" ] && echo "${BinName} has already in database" && exit 1


BinInstSet="unknown"
../BinGather/isdetect.py "$1" >>/dev/null
case $? in
	0) BinInstSet="unknown";;			
	1) BinInstSet="MIPS-Little";;
	2) BinInstSet="MIPS-Big";;
	3) BinInstSet="ARM-Little";;
	4) BinInstSet="ARM-Big";;
	5) BinInstSet="PowerPC-Big";;
	6) BinInstSet="PowerPC-Little";;
esac		

if [ "$BinInstSet" = "unknown" ] && [ -n "`file "$1"|grep ELF`" ];then
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
        0) BinInstSet="unknown";;			
	    1) BinInstSet="MIPS-Little";;
	    2) BinInstSet="MIPS-Big";;
	    3) BinInstSet="ARM-Little";;
	    4) BinInstSet="ARM-Big";;
	    5) BinInstSet="PowerPC-Big";;
	    6) BinInstSet="PowerPC-Little";;
    esac
fi
echo $BinInstSet
((VulID++))
mongocmd "db.${MONGO_VUL_COLLECTION_NAME}.insert({VulID:${VulID},BinName:\"${BinName}\",BinMD5:\"${BinMD5}\"})"
((fileid++))
cp "$1"  ${VUL_BINARY_STORE_PATH}/${fileid}_${BinName}

mongo_update $BinMD5 "BinSave" "${fileid}_${BinName}"

OLD_IFS="$IFS"
IFS=$(echo -e "\n\b")
for line in $(cat $2)
do
    eval "mongo_update $BinMD5 $line"
done
IFS="$OLD_IFS"

mongo_update $BinMD5 BinInstSet $BinInstSet







