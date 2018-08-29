#-*- coding:utf-8 -*-

import os
import pymysql
import urllib3
from bs4 import BeautifulSoup

f = open("../beijing_china.osm.data/edges.csv", 'r' , encoding='utf-8')
contents = f.readlines()[1:]	#去掉第一行的非数据行

db = pymysql.connect("localhost" , "root" , "" , "mapmatching" , charset="utf8")
cursor = db.cursor()
http = urllib3.PoolManager()
i = 0

for line in contents:

	linelist = line.strip('\n').split(',')
	#print(linelist)
	#获取道路名和道路的等级

	url = "http://www.openstreetmap.org/api/0.6/way/" + linelist[0]
	#print(url)
	i += 1

	highway = ''
	street_name = ''
	try:
		r = http.request('GET',url , timeout = 5 , retries=5)
		soup = BeautifulSoup(r.data.decode('utf-8') , 'html5lib')
		all_tag = soup.find_all('tag')
		for tag in all_tag:
			if tag.get('k') == 'highway':
				highway = tag.get('v')
			if tag.get('k') == 'name':
				street_name = tag.get('v')
		car_forward = int(linelist[5])
		car_backward = int(linelist[6])

		wkt = line.strip('\n').split('"')[1]
		#print(wkt)

		if car_forward != 0:
			sql = "INSERT INTO beijing_way (source_id , target_id , length , foot , " + \
				"car , bike, " + \
				"street_name , highway , way_id, wkt)" + \
				" VALUES ('"+ linelist[1] +"','" + linelist[2] +"',"+ linelist[3] +"," + linelist[4] + "," + \
				str(car_forward) +","+ linelist[7] + \
				",'"+ street_name +"','" + highway + "','" + linelist[0] + "', '" +wkt + "') ;"
		if car_backward != 0:
			sql += "INSERT INTO beijing_way (source_id , target_id , length , foot , " + \
				"car, bike , " + \
				"street_name , highway , way_id, wkt)" + \
				" VALUES ('"+ linelist[2] +"','" + linelist[1] +"',"+ linelist[3] +"," + linelist[4] + "," + \
				str(car_backward) +"," + linelist[8] + \
				",'"+ street_name +"','" + highway + "','" + linelist[0] + "', '" +wkt + "') ;"
		print(sql)

		cursor.execute(sql)
		db.commit()
		print("Done " + str(i) + " of " + str(len(contents)))
		
	except Exception as e:
		print("there is a error in " + str(i))
		print(e)
		continue
	
f.close()
db.close()