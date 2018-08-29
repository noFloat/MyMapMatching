#-*- coding:utf-8 -*-
#
from mapmatching.models import *
from django.db.models import Q
import random
import os
import copy
import time
import numpy as np

#对路径进行总结
class RouteUpdate():

    #edge_list : edge_id组成的list 
    #familiarity_dict : edge_id -> familiarity 的字典 所有的边都有其对应的熟悉度
    def __init__(self, edge_list, node_list, familiarity_dict, familiarity_path, user_id):
        self.edge_list = edge_list
        self.node_set = node_list
        self.familiarity_dict = familiarity_dict
        self.familiarity_path = familiarity_path
        self.user_id = user_id
        self.edge_object_list = []
        self.T = []
        n = len(self.node_set)
        self.reach_mat = np.zeros([n,n]) #可到达的邻接表

        segments = []
        for i in range(len(edge_list)):
            segments.append([edge_list[i]])

        for i in range(n):
            if i == 0:
                self.T.append([[],-2000,0,0])
            elif i == n - 1:
                self.T.append([segments,-2000,0,0])
            else:
                self.T.append([segments[:i],-2000,0,0])
            for j in range(i+1,n):
                query = BeijingWayGraphhopper.objects.filter(Q(from_node_id = int(self.node_set[i])) \
                    & Q(target_node_id = int(self.node_set[j])))
                if len(query) > 0:
                    self.reach_mat[i][j] = 1

        #print(self.T)
        #input()

    def doUpdate(self):
        self.createAllEdgesFamiliarityDict() #生成全路径熟悉度
        n = len(self.node_set)

        all_query_time = 0
        start_time = time.time()

        for i in range(1 , n):
            #print(str(i) + '/' + str(n))
            max_from_node_id = 0
            for j in range(0 , i):
                if self.reach_mat[j][i] == 0:
                    continue
                not_choose_node_set = self.node_set[:i]
                not_choose_node_set.remove(self.node_set[j])
                #print('doUpdate ',j,"->",i,', not_choose_node_set:',not_choose_node_set, '0 ->', j, ':', self.T[j][0])
                #print(0,':',self.T[0][0])
                #input()
                now_best_segments, new_q, total_length, total_familiarity, total_query_time = self.optimalRoute(self.node_set[j], self.node_set[i] , self.T[j][0], not_choose_node_set)
                all_query_time += total_query_time
                #print("now_best_segments:",now_best_segments)
                #print(0,"->",i,':',new_q,' now best segments:',now_best_segments)
                #print(0,"->",i,':',new_q)
                if now_best_segments == None or len(now_best_segments) == 0:
                    continue
                #print("i:" + str(i) + " - " + "j:" + str(j))
                #print(R_best)

                #print(R_best)
                #new_RS = T[j][0]
                #print(T[j-1][0])
                #print(new_RS)
                #new_q, total_length, segments_num, \
                #query_time_2, total_familiarity = self.computeRouteQuality(new_RS , familiarity_unit_path)

                #print(new_q)
                #print(new_RS)

                if self.T[i][1] < new_q:
                    self.T[i][0] = now_best_segments
                    #print(T[i-1][0])
                    self.T[i][1] = new_q
                    self.T[i][2] = total_length
                    self.T[i][3] = total_familiarity
                    #max_from_node_id = j
            #print("T",i,' final:',self.T[i][0])
            #input()
        print(len(self.T[-1][0]))

        final_time = time.time() - start_time - all_query_time
        #print(time.time() - start_time)
        #print(all_query_time)
        return self.T[-1][0], len(self.T[-1][0]), final_time, n
        #print(self.T)


    #计算道路的质量分数 edges_id_list:新加的路径id segments:原来的路径分段
    def computeRouteQuality(self, edges_id_list, origin_segments):
        #print("computeRouteQuality")
        #print("compute1?T1:",self.T[1][0])

        quality_score = 0
        segments = copy.deepcopy(origin_segments) #深拷贝
        #print(segments)
        #print("compute2?T1:",self.T[1][0])
        total_length = 0
        lambd = 1 #lambda
        varepsilon = 0.00 #varepsilon 用作距离衰减
        total_familiarity = 0

        street_name_1_list = [] #用第一个路径名来区分segment
        street_name_2_list = [] #用第二个路径名来区分segment #不为空才进行计算
        know_now_segment_flag = 0 #是否熟悉当前segment (1)如果当前segment的开端就有路径是熟悉的 则整个segment都可以简化

        if len(segments) == 0 :
            now_segment_edge_list = [] #每次迭代求出的segment的成员
        else:
            now_segment_edge_list = copy.deepcopy(segments[-1])
            segments.pop()
            #print("Debug",now_segment_edge_list)
            #print("Debug",segments)

        query_time = 0
        query_time_1 = 0
        query_time_2 = 0
        query_time_3 = 0
        query_time_4 = 0
        query_time_5 = 0
        #print("compute3?T1:",self.T[1][0])
        self.edge_object_list = []
        for i in range(len(edges_id_list)):
            quality_score += self.familiarity_dict[int(edges_id_list[i])]
            total_familiarity += self.familiarity_dict[int(edges_id_list[i])]
            #统计segments的个数
            query_time_1_start = time.time()
            edge = BeijingWayGraphhopper.objects.filter(edge_id = int(edges_id_list[i]))[0]
            query_time_1 = time.time() - query_time_1_start

            self.edge_object_list.append(edge)

            street_name_one = edge.street_name_one
            street_name_two = edge.street_name_two
            street_name_1_list.append(street_name_one)
            street_name_2_list.append(street_name_two)
            #print("street_name_1_list:",street_name_1_list)
            total_length += float(edge.length)

            if i == 0 and len(now_segment_edge_list) > 0:
                query_time_2_start = time.time()
                last_edge = BeijingWayGraphhopper.objects.filter(edge_id = now_segment_edge_list[-1])[0]
                query_time_2 = time.time() - query_time_2_start

                if last_edge.street_name_one == edge.street_name_one:
                    now_segment_edge_list.append(int(edges_id_list[i]))
                    #print("compute5?T1:",self.T[1][0])
                else:
                    is_same_direction = self.angleOfTwoEdges(last_edge, edge)
                    if is_same_direction != 1:
                        #角度不同
                        #是否有其他路可以走 、 如果当前道路只有一个出口 则接上上一段
                        query_time_3_start = time.time()
                        common_node = self.findCommonNode(last_edge, self.edge_object_list[i])
                        connect_flag = self.isNoWayOut(common_node)
                        query_time_3 = time.time() - query_time_3_start

                        if connect_flag == 1:
                            now_segment_edge_list.append(int(edges_id_list[i]))
                        else:
                            segments.append(now_segment_edge_list)
                            now_segment_edge_list = []
                            now_segment_edge_list.append(int(edges_id_list[i]))
                        #print("compute6?T1:",self.T[1][0])
                    else:
                        #角度相同
                        now_segment_edge_list.append(int(edges_id_list[i]))
                        #print("compute7?T1:",self.T[1][0])
                
            elif i == 0 and len(now_segment_edge_list) == 0:
                now_segment_edge_list.append(int(edges_id_list[i]))
                #print("compute8?T1:",self.T[1][0])

            elif i > 0:
                if street_name_1_list[i] != "":
                    #有名字
                    if street_name_1_list[i] != street_name_1_list[i-1]:
                        #与前一段名字不一样
                        #计算角度
                        is_same_direction = self.angleOfTwoEdges(self.edge_object_list[i-1], self.edge_object_list[i])
                        if is_same_direction != 1:
                            #角度不同
                            #是否有其他路可以走 、 如果当前道路只有一个出口 则接上上一段
                            query_time_4_start = time.time()
                            common_node = self.findCommonNode(self.edge_object_list[i-1], self.edge_object_list[i])
                            connect_flag = self.isNoWayOut(common_node)
                            query_time_4 = time.time() - query_time_4_start

                            if connect_flag == 1:
                                now_segment_edge_list.append(int(edges_id_list[i]))
                            else:
                                segments.append(now_segment_edge_list)
                                now_segment_edge_list = []
                                now_segment_edge_list.append(int(edges_id_list[i]))
                                #print("compute9?T1:",self.T[1][0])
                        else:
                            #角度相同
                            now_segment_edge_list.append(int(edges_id_list[i]))
                            #print("compute10?T1:",self.T[1][0])
                    else:
                        #与前一段名字一样
                        now_segment_edge_list.append(int(edges_id_list[i]))
                else:
                    #没名字 
                    is_same_direction = self.angleOfTwoEdges(self.edge_object_list[i-1], self.edge_object_list[i])
                    if is_same_direction != 1:
                        #角度不同
                        #是否有其他路可以走 、 如果当前道路只有一个出口 则接上上一段
                        query_time_5_start = time.time()
                        common_node = self.findCommonNode(self.edge_object_list[i-1], self.edge_object_list[i])
                        connect_flag = self.isNoWayOut(common_node)
                        query_time_5 = time.time() - query_time_5_start

                        if connect_flag == 1:
                            now_segment_edge_list.append(int(edges_id_list[i]))
                        else:
                            segments.append(now_segment_edge_list)
                            now_segment_edge_list = []
                            now_segment_edge_list.append(int(edges_id_list[i]))
                        #print("compute11?T1:",self.T[1][0])
                    else:
                        #角度相同
                        now_segment_edge_list.append(int(edges_id_list[i]))
                        #print("compute12?T1:",self.T[1][0])
            query_time += query_time_1 + query_time_2 + query_time_3 + query_time_4 + query_time_5

        segments.append(now_segment_edge_list) #特殊情况 把原来的边加回去
        #print("compute13?T1:",self.T[1][0])

        quality_score -= lambd * len(segments)
        quality_score -= varepsilon * total_length
        #print("compute:", segments)
        #print("compute4?T1:",self.T[1][0])
        return quality_score, total_length, segments, total_familiarity, query_time


    #计算两个边的夹角是否小于多少度
    def angleOfTwoEdges(self, edge_one, edge_two):
        min_angle = 20

        wkt_tuple_list_one = edge_one.wkt2list(2)
        wkt_tuple_list_two = edge_two.wkt2list(2)

        direction_one = self.calDirection(wkt_tuple_list_one[-2],wkt_tuple_list_one[-1])
        direction_two = self.calDirection(wkt_tuple_list_two[-2],wkt_tuple_list_two[-1])

        direction_one_change = (direction_one + 180) % 360 #翻转180度 因为wkt里没有标记道路的方向
        direction_two_change = (direction_two + 180) % 360 #
        #print(edge_one.edge_id, direction_one)
        #print(edge_two.edge_id, direction_two)
        #print("angle:", edge_one.edge_id, edge_two.edge_id)
        #print(direction_one, direction_one_change)
        #print(direction_two, direction_two_change)
        #print(wkt_tuple_list_one)
        #print(wkt_tuple_list_two)

        if abs(direction_one - direction_two) <= min_angle or \
            abs(direction_one - direction_two_change) <= min_angle or \
            abs(direction_one_change - direction_two) <= min_angle or \
            abs(direction_one_change - direction_two_change) <= min_angle:
            return 1
        else:
            return 0

    #根据一条边最后两个GPS组成的连线的方向来计算夹角
    def calDirection(self, geo_one, geo_two):
        if geo_two[1] == geo_one[1]:
            if geo_two[0] > geo_one[0]:
                return float(0)
            else:
                return float(180)
        elif geo_two[0] == geo_one[0]:
            if geo_two[1] > geo_one[1]:
                return float(90)
            else:
                return float(270)

        else:
            slope = (geo_two[1] - geo_one[1]) / (geo_two[0] - geo_one[0])
            if slope > 0:
                #分子分母都是正数 或 都是负数 一三象限
                if geo_two[0] > geo_one[0]: # 1象限
                    return atan(slope) * 180 / pi
                else:   #3象限
                    return atan(slope) * 180 / pi + 180

            else: # 分子分母一正一负 二四象限
                if geo_two[0] > geo_one[0]: #四象限
                    return 360 + atan(slope) * 180 / pi
                else: #二象限
                    return 180 - abs(atan(slope) * 180 / pi)

    #根据熟练度生成全路径字典
    def createAllEdgesFamiliarityDict(self):
        file_list = os.listdir(self.familiarity_path)
        if str(self.user_id) + '.txt' in file_list:
            f = open(self.familiarity_path + str(self.user_id) + '.txt', 'r', encoding = 'utf-8')
            self.familiarity_dict = {}
            for line in f.readlines():
                content = line.strip('\n').split(":")
                self.familiarity_dict[int(content[0])] = float(content[1])
            f.close()
        else:
            edges = BeijingWayGraphhopper.objects.all()
            i = 0
            for edge in edges:
                print(i)
                i += 1
                if edge.edge_id not in self.familiarity_dict:
                    score = random.uniform(0, 0.1)  
                    #查找直接与他相连的边
                    
                    connected_edges = BeijingWayGraphhopper.objects.filter((Q(from_node_id = edge.from_node_id) | Q(target_node_id = edge.from_node_id) & ~Q(edge_id = edge.edge_id)) | \
                        (Q(from_node_id = edge.target_node_id) | Q(target_node_id = edge.target_node_id) & ~Q(edge_id = edge.edge_id)) \
                        )
                    for connected_edge in connected_edges:
                        if connected_edge.edge_id in self.familiarity_dict:
                            if score <= 0.1:
                                score = self.familiarity_dict[connected_edge.edge_id] * 0.5
                            elif score > self.familiarity_dict[connected_edge.edge_id] * 0.5:
                                score = self.familiarity_dict[connected_edge.edge_id] * 0.5
                    
                    self.familiarity_dict[edge.edge_id] = score

            f = open(self.familiarity_path + str(self.user_id) + '.txt', 'w', encoding = 'utf-8')
            w_string = ""
            for key in self.familiarity_dict:
                w_string += str(key) + ":" + str(self.familiarity_dict[key]) + '\n'
            f.write(w_string)
            f.close()




    #从j到i中找一条最优的路径
    def optimalRoute(self, node_j, node_i, last_segments, not_choose_node_set):
        #print("optimalRoute")
        #计算查询时间
        #query_time_1_start = time.time()
        routes_list = BeijingRouteGraphhopper.objects.filter(\
            Q(from_node_id = node_j) & Q(target_node_id = node_i))
        #query_time_1_end = time.time()
        #query_time_1 = query_time_1_end - query_time_1_start

        #限制长度：
        if len(routes_list) == 0:
            return None,0,0,0,0

        max_s = -10000
        s = -10000
        now_segments = []

        #计算时间
        #compute_time = 0
        #print("optimalRoute1?T1:",self.T[1][0])
        total_query_time = 0
        if len(routes_list) > 0:
            compute_time_start = time.time()
            for route in routes_list:
                edges_path = route.way_list.split(' ')
                nodes_path = route.node_list.split(' ')
                #print("route")
                flag = 0 #判断是否有非法路径

                #判断里面的点node在不在生成树里
                for item in nodes_path:
                    if item != '' and int(item) in not_choose_node_set:
                        flag = 1
                        break

                if flag == 1:
                    continue

                #if len(edges_path) + 1 == len(nodes_path):
                #不缺项
                #
                edges_id_list = []
                for edge_id in edges_path:
                    if edge_id != "":
                        edges_id_list.append(int(edge_id))

                #print('optimalRouteDebug1',edges_id_list,last_segments)
                s, total_length, segments, total_familiarity, query_time = self.computeRouteQuality(edges_id_list, last_segments)
                #print('optimalRouteDebug2',segments,s)
                #input()
                if s >= max_s:
                    max_s = s
                    now_segments = segments

                total_query_time += query_time

            if s == -10000:
                return None,0,0,0,0
            #print('optimalRouteDebug3',now_segments)
            return now_segments, s, total_length, total_familiarity, total_query_time

        else:

            return None,0,0,0,0

    #查询当前节点是否只有一个出口 一个入口
    def isNoWayOut(self, common_node):
        if len(BeijingWayGraphhopper.objects.filter(from_node_id = common_node)) == 1:
            return 1
        else:
            return 0

    #查找两个edge的公共结点
    def findCommonNode(self, edge_one, edge_two):
        common_node_list = []
        common_node = 0 #找他们的公共点
        common_node_list.append(edge_one.from_node_id)
        common_node_list.append(edge_one.target_node_id)
        if edge_two.from_node_id in common_node_list:
            common_node = edge_two.from_node_id
        else:
            common_node = edge_two.target_node_id

        return common_node