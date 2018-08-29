import pickle
import numpy as np
import scipy.sparse as ss


f = open('../PaRE/Routes_table/node_distance_matrix_4.pkl', 'rb')
node_distance_matrix_1 = pickle.load(f)
f.close()

f = open('../PaRE/Routes_table/edge_matrix_4.pkl', 'rb')
edge_matrix_1 = pickle.load(f)
f.close()
#print(edge_index_value)


node_num = 80014+1

#print(edge_index_value)

#node_matrix_sparse_one = ss.coo_matrix((node_index_value, (node_index_row,node_index_col)), shape=(node_num,node_num))
#edge_matrix_sparse_one = ss.coo_matrix((edge_index_value, (node_index_row,node_index_col)), shape=(node_num,node_num))

for i in range(4,50,4):

	new_node_distance_matrix = {} #存每条路径对应的距离
	new_edge_matrix = {}


	#上一级的转移矩阵
	f = open('../PaRE/Routes_table/node_distance_matrix_'+str(i)+'.pkl', 'rb')
	node_distance_matrix_pre = pickle.load(f)
	f.close()

	f = open('../PaRE/Routes_table/edge_matrix_'+str(i)+'.pkl', 'rb')
	edge_matrix_pre = pickle.load(f)
	f.close()

	f = open('../PaRE/Routes_table/total_distance_martix_'+str(i)+'.pkl', 'rb')
	total_distance_martix = pickle.load(f)
	f.close()
	#用稀疏矩阵查找是否有可以到达的路径
	node_index_row_1 = np.load("../PaRE/Routes_table/index_list_row2_4.npy")
	node_index_col_1 = np.load("../PaRE/Routes_table/index_list_col2_4.npy")
	node_index_value_1 = np.load("../PaRE/Routes_table/node_index_value2_4.npy")

	node_index_row_new = []
	node_index_col_new = []
	node_index_value_new = []

	node_num = 80014+1
	node_matrix_sparse_one = ss.coo_matrix((node_index_value_1, (node_index_row_1,node_index_col_1)), shape=(node_num,node_num))

	now = 0
	total = len(node_distance_matrix_pre)

	for key in node_distance_matrix_pre:
		now += 1
		print("now transfer_times = " + str(i) + ":" + str(now) + '/' + str(total))

		source_node_id = key[0]
		old_target_node_id = key[1]

		# source_node_id -> old_target_node_id 的元素
		old_edge_list = edge_matrix_pre[key]
		old_distance_list = node_distance_matrix_pre[key]

		#拼接第 old_target_node_id 行的元素
		next_edge_row_index = old_target_node_id
		next_edge_col_index_list = node_matrix_sparse_one.getrow(next_edge_row_index).indices

		# source_node_id -> old_target_node_id + old_target_node_id -> new_target_node_id
		for new_target_node_id in next_edge_col_index_list:

			#去掉自己
			if new_target_node_id == source_node_id:
				continue

			next_distance_list = node_distance_matrix_1[(next_edge_row_index,new_target_node_id)] #一位矩阵
			next_edge_list = edge_matrix_1[(next_edge_row_index,new_target_node_id)] #二维矩阵
			#print(next_edge_list)
			#print(old_edge_list)
			for j in range(len(next_distance_list)):
				for k in range(len(old_distance_list)):
					new_distance = next_distance_list[j] + old_distance_list[k]

					#路径中不能出现重复的边 以免形成环路
					if next_edge_list[j][0] in old_edge_list[k]:
						continue

					#print(new_distance)
					new_edge_list = []
					new_edge_list.extend(old_edge_list[k])
					new_edge_list.extend(next_edge_list[j])
					#print(str(source_node_id) + "->" + str(new_target_node_id))
					#print(new_edge_list)

					if (source_node_id,new_target_node_id) not in new_node_distance_matrix:
						new_node_distance_matrix[(source_node_id,new_target_node_id)] = []
						new_node_distance_matrix[(source_node_id,new_target_node_id)].append(new_distance)
						new_edge_matrix[(source_node_id,new_target_node_id)] = []
						new_edge_matrix[(source_node_id,new_target_node_id)].append(new_edge_list)

					else:
						#限制路径长度 # new_distance !> 2min(source_node_id -> new_target_node_id)
						if new_distance > 100 \
							and new_distance > 2 * min(total_distance_martix[(source_node_id,new_target_node_id)]):
							continue
						new_node_distance_matrix[(source_node_id,new_target_node_id)].append(new_distance)
						new_edge_matrix[(source_node_id,new_target_node_id)].append(new_edge_list)
					
					if (source_node_id,new_target_node_id) not in total_distance_martix:
						total_distance_martix[(source_node_id,new_target_node_id)] = []
						total_distance_martix[(source_node_id,new_target_node_id)].append(new_distance) 
					else:
						total_distance_martix[(source_node_id,new_target_node_id)].append(new_distance) 




	for key in new_node_distance_matrix:
		node_index_row_new.append(key[0])
		node_index_col_new.append(key[1])
		node_index_value_new.append(1)

	np.save("../PaRE/Routes_table/index_list_row2_"+str(i+4)+".npy",np.array(node_index_row_new))
	np.save("../PaRE/Routes_table/index_list_col2_"+str(i+4)+".npy",np.array(node_index_col_new))
	np.save("../PaRE/Routes_table/node_index_value2_"+str(i+4)+".npy",np.array(node_index_value_new))
	output = open('../PaRE/Routes_table/node_distance_matrix_'+str(i+4)+'.pkl', 'wb')
	pickle.dump(new_node_distance_matrix, output)
	output.close()

	output = open('../PaRE/Routes_table/edge_matrix_'+str(i+4)+'.pkl', 'wb')
	pickle.dump(new_edge_matrix, output)
	output.close()

	output = open('../PaRE/Routes_table/total_distance_martix_'+str(i+4)+'.pkl', 'wb')
	pickle.dump(total_distance_martix, output)
	output.close()