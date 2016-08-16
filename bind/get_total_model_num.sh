#!/bin/bash

eval `tail -n +2 ../GLOBAL_CONFIG`
function mongocmd(){
    echo "`echo $1|mongo ${MONGO_IP}:${MONGO_PORT}/${MONGO_DATABASE} --quiet --shell 2>/dev/null`"
}
num=`mongocmd "db.${MONGO_FIRM_COLLECTION_NAME}.distinct(\"ProductModel\")"|wc -l`
((num--))
((num--))
((num--))
echo $num

