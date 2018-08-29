#-*- coding:utf-8 -*-
#
import os
import random

class SplitClass():
	def __init__(self, data_path, train_output_path, test_output_path):
		self.data_path = data_path
		self.train_output_path = train_output_path
		self.test_output_path = test_output_path

	def doSplit(self):
		data_file_list = os.listdir(self.data_path)
		good_data_dict = {}

		for data_name in data_file_list:
			user_id = int(data_name.split('_')[0])
			f = open(self.data_path + data_name , 'r', encoding = 'utf-8')
			lines = f.readlines()
			f.close()
			if len(lines) >= 15:
				if user_id not in good_data_dict:
					good_data_dict[user_id] = []
				good_data_dict[user_id].append(data_name)

		print(good_data_dict)

		#划分数据集
		for key in good_data_dict:
			data_name_list = good_data_dict[key]
			for item in data_name_list:
				#print(item)
				f = open(self.data_path + item , 'r', encoding = 'utf-8')
				data = f.read()

				f.close()
				if random.randint(0,99) > 20:
					f = open(self.train_output_path + item, 'w', encoding = 'utf-8')
				else:
					f = open(self.test_output_path + item, 'w', encoding = 'utf-8')
				f.write(data) #复制
				#print(data)
				#print(self.test_output_path + item)
				f.close()





if __name__ == '__main__':
	a = SplitClass("../Data/taxi_mapmatching_split2user/","../Train/Taxi/","../Test/Taxi/")
	a.doSplit()