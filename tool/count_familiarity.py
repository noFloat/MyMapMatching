#-*- coding:utf-8 -*-
#
#
import os

if __name__ == '__main__':
	file_path = 'F:/Project/GIS/MyMapMatching/Train/Taxi/'
	write_path = 'F:/Project/GIS/MyMapMatching/Train/Taxi_familiarity/'
	file_name_list = os.listdir(file_path)

	familiarity_dict = {}
	for filename in file_name_list:
		user_id = int(filename.split("_")[0])
		f = open(file_path + filename, 'r', encoding = 'utf-8')
		lines = f.readlines()
		f.close()
		for line in lines:
			edge_id = int(line.strip('\n'))
			if user_id not in familiarity_dict:
				familiarity_dict[user_id] = {}
			if edge_id not in familiarity_dict[user_id]:
				familiarity_dict[user_id][edge_id] = 1
			else:
				familiarity_dict[user_id][edge_id] += 1
				if familiarity_dict[user_id][edge_id] >= 10:
					familiarity_dict[user_id][edge_id] = 10

	for user_id in familiarity_dict:
		w_string = ""
		f = open(write_path + str(user_id) + '.txt', 'w', encoding = "utf-8")
		for edge_id in familiarity_dict[user_id]:
			w_string += str(edge_id) + ':' + str(familiarity_dict[user_id][edge_id]) + '\n'

		f.write(w_string)
		f.close()

