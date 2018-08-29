#-*- coding:utf-8 -*-

import os
import pymysql
import urllib3
import json

f = open("../beijing_china.osm.data/nodes.csv", 'r' , encoding='utf-8')
contents = f.readlines()[1:]	#去掉第一行的非数据行

db = pymysql.connect("localhost" , "root" , "" , "pare" , charset="utf8")
cursor = db.cursor()
http = urllib3.PoolManager()
i = 0

for line in contents:
	linelist = line.strip('\n').split(',')
	#print(linelist)
	i += 1
	values = {}
	values['locations'] = linelist[1] + ',' + linelist[2]
	values['coordsys'] = 'gps'
	values['key'] = 'f4ed1201a3bfed05e6223abd80e1e047'

	url = "http://restapi.amap.com/v3/assistant/coordinate/convert"

	try:
		r = http.request('GET',url , fields=values)
		json_result = json.loads(r.data.decode('utf-8'))
		locations = json_result['locations'].split(',')

		gaode_lon = locations[0]
		gaode_lat = locations[1]

		sql = "INSERT INTO nodes (lon , lat , gaode_lon , gaode_lat , " + \
			"node_id)" + \
			" VALUES ('"+ linelist[1] +"','" + linelist[2] +"','"+ gaode_lon +"','" + gaode_lat + "','" + \
			linelist[0] + "') "
		#print(sql)
		cursor.execute(sql)
		db.commit()
		print("Done " + str(i) + " of " + str(len(contents)))
		
	except Exception as e:
		print("there is a error in " + str(i))
		print(e)
		continue
	
f.close()
db.close()