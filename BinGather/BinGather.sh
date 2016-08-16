#!/bin/bash

eval `tail -n +2 ../GLOBAL_CONFIG`
eval `tail -n +2 CONFIG`

echo "------------------current config--------------------------"
echo "ITERATIVE_DEPPTH=$ITERATIVE_DEPPTH"
echo "DECOMPRESS_TIMEOUT=$DECOMPRESS_TIMEOUT"
echo "FILE_RETURN_BLACKLIST=${FILE_RETURN_BLACKLIST[@]}"
echo "FILE_RETURN_WHITELIST=${FILE_RETURN_WHITELIST[@]}"
echo "EXTENSION_BLACKLIST=${EXTENSION_BLACKLIST[@]}"
echo "EXTENSION_WHITELIST=${EXTENSION_WHITELIST[@]}"
echo "INSTRUCTION_SET_DETECT_METHOD_SELECT=${INSTRUCTION_SET_DETECT_METHOD_SELECT[@]}"
echo "MONGO_IP=$MONGO_IP"
echo "MONGO_PORT=$MONGO_PORT"
echo "MONGO_DATABASE=$MONGO_DATABASE"
echo "MONGO_FIRM_COLLECTION_NAME=$MONGO_FIRM_COLLECTION_NAME"
echo "FIRMWARE_STORE_PATH=$FIRMWARE_STORE_PATH"
echo "DECOMPRESS_TEMP_PATH=$DECOMPRESS_TEMP_PATH"
echo "BINARY_STORE_PATH=$BINARY_STORE_PATH"
echo "----------------current config end------------------------"

ExtensionBlacklist=`echo "${EXTENSION_BLACKLIST[@]}"|sed "s/ /|/g"`
FileReturnBlacklist=`echo "${FILE_RETURN_BLACKLIST[@]}"|sed "s/ /|/g"`


ExtensionWhitelist=`echo "${EXTENSION_WHITELIST[@]}"|sed "s/ /|/g"`
FileReturnWhitelist=`echo "${FILE_RETURN_WHITELIST[@]}"|sed "s/ /|/g"`


ManufacturerPathPos=`echo $FIRMWARE_STORE_PATH|awk -F/ '{print NF+1}'`
IFS=$(echo -e "\n\b")

UNIX_DIRS=(bin etc dev home lib mnt opt root run sbin tmp usr var)
UNIX_THRESHOLD=4

fileid=$(ls $BINARY_STORE_PATH |awk -F_ '{print $1}'|sort -n|tail -1)

firmcount=0
for item in `find "$FIRMWARE_STORE_PATH"`
do
	[ -f $item ] && ((firmcount++))
done
manucount=0
for item in `ls "$FIRMWARE_STORE_PATH"`
do
	[ -d $FIRMWARE_STORE_PATH/$item ] && ((manucount++))

done
echo "find $manucount manufacturer $firmcount firmwares in $FIRMWARE_STORE_PATH"

echo "load plugins:$(ls Plugin)"

OLD_IFS="$IFS"
IFS=" "
plugins=("`ls Plugin`")
IFS="$OLD_IFS"

mongo_cmd="db.${MONGO_FIRM_COLLECTION_NAME}.find({},{FirmID:1,_id:0}).sort({FirmID:-1}).limit(1);"
FirmID=$(echo "$mongo_cmd"|mongo ${MONGO_IP}:${MONGO_PORT}/${MONGO_DATABASE} --quiet --shell 2>/dev/null|awk '{print $4}'|tail -1)

function mongo_update(){
    mongo_cmd="db.${MONGO_FIRM_COLLECTION_NAME}.update({FirmName:\"$1\"},{\$set:{$2:\"$3\"}});"
    #echo $mongo_cmd
    echo "$mongo_cmd"|mongo ${MONGO_IP}:${MONGO_PORT}/${MONGO_DATABASE} --quiet --shell >/dev/null 2>&1			
}

function process_one_firm(){  #arg1:path arg2:manufacturer arg3:class arg4:modle arg4:discrition
    FirmPath="$1"
    [ ! -f "$FirmPath" ] && return
	FirmMD5=$(md5sum "$FirmPath"|awk '{print $1}')	
	mongo_cmd="db.${MONGO_FIRM_COLLECTION_NAME}.findOne({FirmMD5:\"${FirmMD5}\"});"
	[ $(echo "$mongo_cmd"|mongo ${MONGO_IP}:${MONGO_PORT}/${MONGO_DATABASE} --quiet --shell 2>/dev/null|tail -1) != "null" ] && echo "${FirmPath} has already in database" && return 

	((FirmID++))
	FirmName="${FirmPath##*/}"
    if [ -z "$2" ];then
	    Manufacturer=$(echo "$FirmPath"|cut -d "/" -f $ManufacturerPathPos)
    else
        Manufacturer="$2"
    fi
	FirmSize=$(ls -l "$FirmPath"|awk '{print $5}')
    ProcessTime=`date`
    mongo_cmd="db.${MONGO_FIRM_COLLECTION_NAME}.insert({FirmID:${FirmID},FirmName:\"${FirmName}\",Manufacturer:\"${Manufacturer}\",FirmSize:${FirmSize},FirmMD5:\"${FirmMD5}\",FirmPath:\"${FirmPath}\",ProcessTime:\"${ProcessTime}\",OS:[],InstuctionSet:[],BinFileCount:0,BinFiles:[]});"
	echo "$mongo_cmd"|mongo ${MONGO_IP}:${MONGO_PORT}/${MONGO_DATABASE} --quiet --shell >/dev/null 2>&1
    #process_one_firm(){  #arg1:path arg2:manufacturer arg3:class arg4:modle arg5:discrition
    [ -n "$3" ] && mongo_update "$FirmName" "ProductClass" "$3"
    [ -n "$4" ] && mongo_update "$FirmName" "ProductModel" "$4"
    [ -n "$5" ] && mongo_update "$FirmName" "Description" "$5"
	echo "************************************************************"	
	echo "decompressing:${FirmPath}"
	echo "************************************************************"
	binwalk  -e -M -q --depth=10 "$FirmPath" -C $DECOMPRESS_TEMP_PATH >/dev/null 2>&1 &
	commandpid=$!
	(sleep $DECOMPRESS_TIMEOUT;kill -9 $commandpid >/dev/null 2>&1;echo binwalk take too much time!!!) &
	watchdogpid=$!
	sleeppid=`ps $PPID $watchdogpid | awk '{print $1}'`
	wait $commandpid

	kill $sleeppid >/dev/null 2>&1
	echo ">>decompress complete."
	
	if [ -d "${DECOMPRESS_TEMP_PATH}/_${FirmName}.extracted" ];then
		unset md5list
		declare -a md5list
		visitID=0
		UNIX_PATH_MATCH=0
		for BinPath in `find "${DECOMPRESS_TEMP_PATH}/_${FirmName}.extracted"`
		do
			echo "------------------------------------------------------"
			BinName=${BinPath##*/}
			echo "analysis: $BinName"

			for dirname in ${UNIX_DIRS[@]};do
				if [ -d "$BinPath" -a  "${BinPath##*/}" == $dirname ];then
					((UNIX_PATH_MATCH++))
					break						
				fi				
			done

			[ -f "$BinPath" ] && BinMd5=$(md5sum "$BinPath"|awk '{print $1}')
			visited_flag=0
			for md5value in ${md5list[@]};do
				[ "$BinMd5" = "$md5value" ] && visited_flag=1 && break				
			done
			[ "$visited_flag" = 1 ] && echo ">>has the same md5!!!" && continue
			md5list[$visitID]=$BinMd5
			((visitID++))		

			BinSuffix="" && [ "${BinName##*.}" != "$BinName" ] && BinSuffix="${BinName##*.}"

			if [ -z "$ExtensionWhitelist" -o -z "`file "$BinSuffix"|grep -E "$ExtensionWhitelist"`" ] && [ -z "$FileReturnWhitelist" -o -z "`file "$BinPath"|grep -E "$FileReturnWhitelist"`" ] ;then
				[ -d "$BinPath" ] && echo ">>this is a directory!!!" && continue
				[ ! -f "$BinPath" ] && echo ">>this is not a normal file!!!" && continue
				[ -L "$BinPath" ] && echo ">>this is a symbolic link to other file!!!" && continue
				[ -n "`file "$BinSuffix"|grep -E "$ExtensionBlacklist"`" ] && echo ">>in the suffix blacklist!!!" && continue
				[ -n "`file "$BinPath"|grep -E "$FileReturnBlacklist"`" ] && echo ">>in the file return blacklist!!!" && continue			
			fi
			BinInstSet="unknown"
			if [ "$INSTRUCTION_SET_DETECT_METHOD_SELECT" -eq 0 ];then
				./isdetect.py "$BinPath" >>/dev/null
				case $? in
					0) BinInstSet="unknown";;			
					1) BinInstSet="MIPS-Little";;
					2) BinInstSet="MIPS-Big";;
					3) BinInstSet="ARM-Little";;
					4) BinInstSet="ARM-Big";;
					5) BinInstSet="PowerPC-Big";;
					6) BinInstSet="PowerPC-Little";;
				esac		
				echo ">>>>find ${BinInstSet} by instruction detect arithmetic"		
			fi
			if [ "$INSTRUCTION_SET_DETECT_METHOD_SELECT" -eq 1 ] && [ "$BinInstSet" = "unknown" ] && [ -n "`file "$BinPath"|grep ELF`" ];then
				temp=0
				if [ -n "`file "$BinPath"|grep MIPS`" ];then
					temp=1
					[ -n "`file "$BinPath"|grep MSB`" ] && temp=2
				elif [ -n "`file "$BinPath"|grep ARM`" ];then
					temp=3
					[ -n "`file "$BinPath"|grep MSB`" ] && temp=4
				elif [ -n "`file "$BinPath"|grep -E "ppc|PowerPC"`" ];then
					temp=5
					[ -n "`file "$BinPath"|grep LSB`" ] && temp=6
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
				echo ">>>>find ${BinInstSet} by elf header"
			fi
			BinSize=$(ls -l "$BinPath"|awk '{print $5}')
			if [ "$BinInstSet" != "unknown" ] || [ -n "$ExtensionWhitelist" -a -n "`file "$BinSuffix"|grep -E "$ExtensionWhitelist"`" ] || [ -n "$FileReturnWhitelist" -a -n "`file "$BinPath"|grep -E "$FileReturnWhitelist"`" ] ;then
				((fileid++))
				echo ">>store bin"
				BinSave=${fileid}_${BinName}_${BinInstSet}
				cp "$BinPath" "${BINARY_STORE_PATH}/${BinSave}"
				mongo_cmd="db.${MONGO_FIRM_COLLECTION_NAME}.update({FirmID:${FirmID}},{\$push:{BinFiles:
{BinName:\"${BinName}\",BinSize:\"${BinSize}\",BinMD5:\"${BinMd5}\",BinInstSet:\"${BinInstSet}\",BinSave:\"${BinSave}\"} }});"
				echo "$mongo_cmd"|mongo ${MONGO_IP}:${MONGO_PORT}/${MONGO_DATABASE} --quiet --shell >/dev/null 2>&1	
				for plugin in ${plugins[@]}
				do
					content=$(Plugin/$plugin "$BinPath")
					[ -z "$content" ] && continue
					mongo_cmd="db.firmwares.update({FirmID:${FirmID},\"BinFiles.BinMD5\":\"${BinMd5}\"},{\$set:{\"BinFiles.$.${plugin}\":'${content}'}})"
					echo "$mongo_cmd"|mongo ${MONGO_IP}:${MONGO_PORT}/${MONGO_DATABASE} --quiet --shell >/dev/null 2>&1						
				done
				
				mongo_cmd="db.${MONGO_FIRM_COLLECTION_NAME}.update({FirmID:${FirmID}},{\$inc:{BinFileCount:1}});"
				echo "$mongo_cmd"|mongo ${MONGO_IP}:${MONGO_PORT}/${MONGO_DATABASE} --quiet --shell >/dev/null 2>&1			

				mongo_cmd="db.${MONGO_FIRM_COLLECTION_NAME}.update({FirmID:${FirmID}},{\$addToSet:{InstuctionSet:\"${BinInstSet}\"}});"
				echo "$mongo_cmd"|mongo ${MONGO_IP}:${MONGO_PORT}/${MONGO_DATABASE} --quiet --shell >/dev/null 2>&1			

				if [ -n "`binwalk "$BinPath"|grep Linux`" ];then
					OS="Linux"
					mongo_cmd="db.${MONGO_FIRM_COLLECTION_NAME}.update({FirmID:${FirmID}},{\$addToSet:{OS:\"${OS}\"}});"
					echo "$mongo_cmd"|mongo ${MONGO_IP}:${MONGO_PORT}/${MONGO_DATABASE} --quiet --shell >/dev/null 2>&1			
				fi
				if [ -n "`binwalk "$BinPath"|grep VxWorks`" ];then
					OS="VxWorks"
					mongo_cmd="db.${MONGO_FIRM_COLLECTION_NAME}.update({FirmID:${FirmID}},{\$addToSet:{OS:\"${OS}\"}});"
					echo "$mongo_cmd"|mongo ${MONGO_IP}:${MONGO_PORT}/${MONGO_DATABASE} --quiet --shell >/dev/null 2>&1			
				fi
				if [ -n "`file "$BinPath"|grep "Windows CE"`" ];then
					OS="Windows CE"
					mongo_cmd="db.${MONGO_FIRM_COLLECTION_NAME}.update({FirmID:${FirmID}},{\$addToSet:{OS:\"${OS}\"}});"
					echo "$mongo_cmd"|mongo ${MONGO_IP}:${MONGO_PORT}/${MONGO_DATABASE} --quiet --shell >/dev/null 2>&1			
				fi
			fi
		done
		[ $UNIX_PATH_MATCH -ge $UNIX_THRESHOLD  ] && OS="Linux" && mongo_cmd="db.${MONGO_FIRM_COLLECTION_NAME}.update({FirmID:${FirmID}},{\$addToSet:{OS:\"${OS}\"}});" && echo "$mongo_cmd"|mongo ${MONGO_IP}:${MONGO_PORT}/${MONGO_DATABASE} --quiet --shell >/dev/null 2>&1	
		rm -rf "${DECOMPRESS_TEMP_PATH}/_${FirmName}.extracted"
		echo ">>remove ${DECOMPRESS_TEMP_PATH}/_${FirmName}.extracted"		
	else
		echo ">>binwalk can't extracted any file!!!"
	fi
}

if [ -z "$1" ];then
    for item in `find "$FIRMWARE_STORE_PATH"`
    do
        process_one_firm $item   
    done
else
    process_one_firm "$1" "$2" "$3" "$4" "$5"
fi

