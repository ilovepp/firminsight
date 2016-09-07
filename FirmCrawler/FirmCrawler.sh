#!/bin/bash

for crawl in `ls mycrawler/spiders|grep py$|grep -v "__init__"`
do
	scrapy crawl ${crawl%S*}  
done

python siemensdownload.py 
python download.py

