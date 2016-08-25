#!/bin/bash

eval `tail -n +2 ../GLOBAL_CONFIG`
function mongocmd(){
	echo "`echo $1|mongo ${MONGO_IP}:${MONGO_PORT}/${MONGO_DATABASE} --quiet --shell 2>/dev/null`"
}

mongocmd "db.${MONGO_FIRM_COLLECTION_NAME}.count()"|tail -1
