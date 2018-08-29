#-*- coding:utf-8 -*-

import os
import pymysql


filelist = os.listdir("./primary-data")
i = 100
j = 0
db = pymysql.connect("localhost" , "root" , "" , "pare")
cursor = db.cursor()

for file in filelist:
	f = open("./primary-data/" + file , 'r' , encoding='utf-8')
	i += 1
	for line in f.readlines():
		j += 1
		linelist = line.split(',')
		sql = "INSERT INTO trajectory VALUES ("+ str(j) +",'" + linelist[0] +"','"+ linelist[2] +"','" + linelist[1] + "'," + str(int(i/100)) + ") "
		#print(sql)
		cursor.execute(sql)
		db.commit()
	print("Done " + str(i-100) + " of " + str(len(filelist)))

db.close()