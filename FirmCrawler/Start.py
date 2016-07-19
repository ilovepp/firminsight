import os

rootdir = "/home/byfeelus/project/Druid/mycrawler/mycrawler/spiders"

a = os.listdir(rootdir)

args = []

for x in a:
    if x.split(".")[-1] == "py":
        x = x.replace("." + x.split(".")[-1],"")
        if "Spider" in x:
            x = x.replace("Spider","")
            print x
            args.append(x)
print args

def run_spider(s):
	for arg in s:
		os.popen("gnome-terminal -x bash -c 'scrapy crawl %s'" % arg)
run_spider(args)
