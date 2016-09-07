#!/bin/bash

eval `tail -n +2 ../GLOBAL_CONFIG`
eval `tail -n +2 CONFIG`

function mongocmd(){
	echo "`echo "$1"|mongo ${MONGO_IP}:${MONGO_PORT}/${MONGO_DATABASE} --quiet --shell 2>/dev/null`"
}

if [ $# != 3 ];then
    echo "USAGE:$0 search_firm_id search_bin_name vul_id"
    exit 1
fi

search_firm_id="$1"
search_bin_name="$2"
vul_id="$3"

search_firm_name=$(mongocmd "db.${MONGO_FIRM_COLLECTION_NAME}.find({FirmID:${search_firm_id}}).toArray()"|grep FirmName|awk -F\" '{print $4}')
search_save_bin=$(mongocmd "db.${MONGO_FIRM_COLLECTION_NAME}.find({FirmID:${search_firm_id}},{_id:0,BinFiles:{\$elemMatch:{BinName:\"${search_bin_name}\"}}})"|sed -e 's/, /\n/g'|grep BinSave|awk -F\" '{print $4}')
target_save_bin=$(mongocmd "db.${MONGO_VUL_COLLECTION_NAME}.find({VulID:${vul_id}}).toArray()"|grep BinSave|awk -F\" '{print $4}')
search_instset=$(mongocmd "db.${MONGO_FIRM_COLLECTION_NAME}.find({FirmID:${search_firm_id}},{_id:0,BinFiles:{\$elemMatch:{BinName:\"${search_bin_name}\"}}})"|sed -e 's/, /\n/g'|grep BinInstSet|awk -F\" '{print $4}')
target_instset=$(mongocmd "db.${MONGO_VUL_COLLECTION_NAME}.find({VulID:${vul_id}}).toArray()"|grep BinInstSet|awk -F\" '{print $4}')
target_fun_name=$(mongocmd "db.${MONGO_VUL_COLLECTION_NAME}.find({VulID:${vul_id}}).toArray()"|grep FuncName|awk -F\" '{print $4}')

[ -z "$search_save_bin" -o -z "$target_save_bin" ] && echo "binary not in the database!" && exit
[ -z "$target_fun_name" ] && echo "function not in the binary" && exit
BinMD5=`md5sum "$BINARY_STORE_PATH/$search_save_bin"|awk '{print $1}'`
[ $(mongocmd "db.${MONGO_RELATION_COLLECTION_NAME}.findOne({VulID:${vul_id},BinMD5:\"${BinMD5}\"});"|tail -1) != "null" ] && echo "relation result already in database" && mongocmd "db.${MONGO_RELATION_COLLECTION_NAME}.findOne({VulID:${vul_id},BinMD5:\"${BinMD5}\"},{_id:0,Result:1});" && exit
if [ -n "`file "$BINARY_STORE_PATH/$search_save_bin"|grep ELF`" ];then
    $IDA_PATH -B -o$DECOMPRESS_TEMP_PATH/search.i64 "$BINARY_STORE_PATH/$search_save_bin"
else
    echo $search_instset
    if [ "$search_instset" = "PowerPC-Big" ];then
        $IDA_PATH -B -pppc -o$DECOMPRESS_TEMP_PATH/search.i64 "$BINARY_STORE_PATH/$search_save_bin"
        $IDA_PATH -A -Sfix_ppcbig_fun.idc $DECOMPRESS_TEMP_PATH/search.i64
    elif [ "$search_instset" = "ARM-Little" ];then
        $IDA_PATH -B -parm -o$DECOMPRESS_TEMP_PATH/search.i64 "$BINARY_STORE_PATH/$search_save_bin"
        $IDA_PATH -A -Sfix_armlittle_fun.idc $DECOMPRESS_TEMP_PATH/search.i64
    fi
fi
if [ ! -f "$VUL_BINARY_STORE_PATH/$target_save_bin.i64"  ];then
    if [ -n "`file "$VUL_BINARY_STORE_PATH/$target_save_bin"|grep ELF`" ];then
        $IDA_PATH -B -o$VUL_BINARY_STORE_PATH/$target_save_bin.i64 "$VUL_BINARY_STORE_PATH/$target_save_bin"
    else
        if [ "$target_instset" = "PowerPC-Big" ];then
            $IDA_PATH -B -pppc -o$VUL_BINARY_STORE_PATH/$target_save_bin.i64 "$VUL_BINARY_STORE_PATH/$target_save_bin"
            $IDA_PATH -A -Sfix_ppcbig_fun.idc $VUL_BINARY_STORE_PATH/$target_save_bin.i64
        elif [ "$target_instset" = "ARM-Little" ];then
            $IDA_PATH -B -parm -o$VUL_BINARY_STORE_PATH/$target_save_bin.i64 "$VUL_BINARY_STORE_PATH/$target_save_bin"
            $IDA_PATH -A -Sfix_armlittle_fun.idc $VUL_BINARY_STORE_PATH/$target_save_bin.i64
        fi
    fi
fi
[ ! -f $VUL_BINARY_STORE_PATH/$target_save_bin.i64 -o ! -f $DECOMPRESS_TEMP_PATH/search.i64 ] && echo "ida can't produce i64 file" && exit

python Core/bugSearch.py $DECOMPRESS_TEMP_PATH/search.i64 $VUL_BINARY_STORE_PATH/$target_save_bin.i64 $target_fun_name

rm $DECOMPRESS_TEMP_PATH/search.* 

[ ! -s  result.json -o "`cat result.json`" = "{}" ] && echo "no matched function" && exit

cat result.json
Time=`date`
Result=`cat result.json|sed "s/\"//g"`
mongocmd "db.${MONGO_RELATION_COLLECTION_NAME}.insert({VulID:${vul_id},FirmID:${search_firm_id},FirmName:\"${search_firm_name}\",BinName:\"${search_save_bin}\",BinMD5:\"${BinMD5}\",Time:\"${Time}\",Result:\"${Result}\"});"

#./FunRelation.sh 1671 vxWorks_bmx1000.bin 7
./FunRelation.sh 1628 1 6
