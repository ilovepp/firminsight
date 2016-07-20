#!/bin/bash

for crawl in `ls mycrawler/spiders`
do
	echo $crawl|grep py$|grep -v "__init__"
done 




