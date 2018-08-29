# -*- coding:utf-8 -*-

#将 GPS坐标 转换为 高德地图坐标

import urllib3
import json
import pymysql

db = pymysql.connect("localhost" , "root" , "" , "pare")
cursor = db.cursor()
sql = "SELECT * FROM trajectory"
cursor.execute(sql)

result = cursor.fetchall()
#print(type(result[0]))
db.commit()

http = urllib3.PoolManager()

for row in result[197074:]:
	values = {}
	values['locations'] = row[2] + ',' + row[3]
	values['coordsys'] = 'gps'
	values['key'] = 'f4ed1201a3bfed05e6223abd80e1e047'

	url = "http://restapi.amap.com/v3/assistant/coordinate/convert"
	try:
		r = http.request('GET',url,fields=values, timeout = 5 , retries=5)

		json_result = json.loads(r.data.decode('utf-8'))
		locations = json_result['locations'].split(',')

		gaode_lon = locations[0]
		gaode_lat = locations[1]

		update_sql = "UPDATE trajectory SET gaode_lon = '" + gaode_lon + "' , gaode_lat = '" +\
			gaode_lat + "' WHERE id = " + str(row[0])

		cursor.execute(update_sql)
		db.commit()
	except:
		print("there is a error in " + str(row[0]))
		continue
	print("now finish " + str(row[0]) + " / " + str(len(result)))

db.close()