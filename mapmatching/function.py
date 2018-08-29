from mapmatching.models import *
#from mapmatching.models import BeijingWay
from django.db.models import Q
import numpy as np
import scipy.sparse as ss
import time
from math import *

#根据轨迹查找相应的节点和路径
def findWaysAndNodes(street_name_list , distance_list, interval_list , points_list):
    node_list = []
    way_list = []
    #print(street_name_list)
    way_map = {} #找到每一个边的后继边 防止走入死路


    for i in range(len(street_name_list)):
        #滤掉距离为0的点
        if int(distance_list[i]) == 0:
            continue

        #以有名字的路为起始
        street_name = street_name_list[i]
        if len(way_list) == 0 and street_name == "":
            continue
        #print(street_name)

        start_index = int(interval_list[i][0])
        end_index = int(interval_list[i][1])
        selected_points_list = (points_list[start_index:end_index+1] \
            if end_index < len(points_list) else points_list[start_index:])

        if len(selected_points_list) == 1:
            continue

        #有路径名则规定待搜索路径集
        if street_name != "":

            #查找全轨迹的第一条路径
            if len(way_list) == 0:
                edges = BeijingWay.objects.filter(Q(street_name = street_name))
                
                #有查到指定的路径集
                if len(edges) != 0:
                    #遍历指定的points
                    result_node, result_way = findNodesFromEdges2(selected_points_list, street_name, node_list , way_list , 0, distance_list[i])
                    node_list.extend(result_node)
                    way_list.extend(result_way)

            #当前的边需要接在前面的边上
            else:
                edges = BeijingWay.objects.filter(Q(street_name = street_name) & Q(source_id = node_list[-1]))
                
                #有查到指定的路径集
                if len(edges) != 0:
                    #遍历指定的points
                    result_node, result_way = findNodesFromEdges2(selected_points_list, street_name, node_list, way_list , 1 , distance_list[i])
                    node_list.extend(result_node)
                    way_list.extend(result_way)
                else:
                    result_node, result_way = findNodesFromEdges2(selected_points_list, "", node_list, way_list, 1, distance_list[i])
                    node_list.extend(result_node)
                    way_list.extend(result_way)
        #没有路径名
        elif len(node_list) > 0:
            #没有路径名的路段前面有路段
            result_node, result_way = findNodesFromEdges2(selected_points_list, "", node_list, way_list , 1, distance_list[i])
            node_list.extend(result_node)
            way_list.extend(result_way)

        else:
            #没有路径名的路段前面没有路段
            pass

        print(way_list)

    return node_list, way_list

#在指定的边中找到距离最小的匹配点
def findNodesFromEdges(points_list, street_name, node_list, pass_edges , style, total_distance):
    result_node = [] #node_id 
    result_way = [] #way id

    nodes_set = set()
    copy_node_list = node_list[:]
    add_way_distance = 0

    for i in range(len(points_list) - 1):
        min_distance = 99999999
        min_edge = None #最符合的edge
        lng = points_list[i][0]
        lat = points_list[i][1]

        direction = CalDirection(\
            (float(points_list[i][0]),float(points_list[i][1])),\
            (float(points_list[i+1][0]),float(points_list[i+1][1])))

        if style == 0 and len(result_way) == 0:
            #寻找全路径的第一条边
            #当前行驶方向
            print(1)
            #print((float(points_list[0][0]),float(points_list[0][1])))
            #print((float(points_list[1][0]),float(points_list[1][1])))
            #print(direction)
            #print("##########")
            edges = BeijingWay.objects.filter(Q(street_name = street_name))
            for edge in edges:
                #滤掉夹角过大的边
                
                #print(edge.direction())
                #print(compute_angle(direction , edge.direction()))
                #print("##########")

                if compute_angle(direction , edge.direction()) < 30:
                    #过滤掉差距过大的点
                    wkt_tuple_list = edge.wkt2list()
                    for wkt_point in wkt_tuple_list:
                        distance = haversine(float(lng),float(lat), \
                            wkt_point[0],wkt_point[1])
                        if distance < min_distance:
                            min_distance = distance
                            min_edge = edge

            print(min_distance)

            result_way.append(min_edge.id)
            result_node.append(min_edge.source_id)
            result_node.append(min_edge.target_id)
            copy_node_list = result_node[:]
            add_way_distance += min_edge.length
            if add_way_distance > total_distance:
                break
            else:
                continue


        #前面还有点
        if len(copy_node_list) != 0 :
            #查找的点需要与前面的点一致或相接
            print(2)
            the_last_node = copy_node_list[-1]
            new_nodes_set = set()

            if street_name != "":
                #有名字的路
                new_edges = BeijingWay.objects.filter(Q(source_id = the_last_node) & Q(street_name = street_name))
                print(3)
                if len(new_edges) == 0:
                    print(4)
                    break
                    #new_edges = BeijingWay.objects.filter(Q(source_id = the_last_node))
                    #print(4)
                #print(111)
                #print(the_last_node)
                #print(len(new_edges))
            else:
                #没名字的路
                new_edges = BeijingWay.objects.filter(Q(source_id = the_last_node))
                print(5)


            for edge in new_edges:
                #滤掉夹角过大的边
                if compute_angle(direction , edge.direction()) < 90:
                    #过滤掉差距过大的点
                    wkt_tuple_list = edge.wkt2list()
                    for wkt_point in wkt_tuple_list:
                        distance = haversine(float(lng),float(lat), \
                            wkt_point[0],wkt_point[1])
                        if distance < min_distance:
                            min_distance = distance
                            min_edge = edge
            #检验上一次的最后一条边：这个点可能仍然在上一条边中
            if len(pass_edges)  == 0:
                last_edge_id = result_way[-1]
                print(6)
            else:
                last_edge_id = pass_edges[-1]

            last_edge = BeijingWay.objects.get(id = last_edge_id)
            wkt_tuple_list = last_edge.wkt2list()
            for wkt_point in wkt_tuple_list:
                distance = haversine(float(lng),float(lat), \
                    wkt_point[0],wkt_point[1])
                if distance < min_distance:
                    min_distance = distance
                    min_edge = last_edge

        print(min_distance)
        if min_edge != None:
            if min_edge.id not in result_way:
                result_way.append(min_edge.id)
                result_node.append(min_edge.target_id)
                copy_node_list.append(min_edge.target_id)

                add_way_distance += min_edge.length
                if add_way_distance > total_distance:
                    break

                if street_name == "":
                    #没名字的路最多接一段
                    break

    #print(result_way)
    #print(result_node)

    return result_node, result_way

#在指定的边中找到距离最小的匹配点 每次最多只能接一段
def findNodesFromEdges2(points_list, street_name, node_list, pass_edges , style, total_distance):
    result_node = [] #node_id 
    result_way = [] #way id

    nodes_set = set()
    copy_node_list = node_list[:]
    add_way_distance = 0

    vote_edge = {} #投票
    distance_edge = {} #距离 如果票数相等 距离小的当选

    for i in range(len(points_list) - 1):
        min_distance = 6000
        min_edge = None #最符合的edge
        lng = points_list[i][0]
        lat = points_list[i][1]

        direction = CalDirection(\
            (float(points_list[i][0]),float(points_list[i][1])),\
            (float(points_list[i+1][0]),float(points_list[i+1][1])))

        if style == 0 and len(result_way) == 0:
            #寻找全路径的第一条边
            #当前行驶方向
            print(1)
            #print((float(points_list[0][0]),float(points_list[0][1])))
            #print((float(points_list[1][0]),float(points_list[1][1])))
            #print(direction)
            #print("##########")
            edges = BeijingWay.objects.filter(Q(street_name = street_name))
            for edge in edges:
                #滤掉夹角过大的边
                
                #print(edge.direction())
                #print(compute_angle(direction , edge.direction()))
                #print("##########")

                if compute_angle(direction , edge.direction()) < 30:
                    #过滤掉差距过大的点
                    wkt_tuple_list = edge.wkt2list()
                    for wkt_point in wkt_tuple_list:
                        distance = haversine(float(lng),float(lat), \
                            wkt_point[0],wkt_point[1])
                        if distance < min_distance:
                            min_distance = distance
                            min_edge = edge

                    if min_edge.id in vote_edge:
                        vote_edge[min_edge.id] += 1
                        distance_edge[min_edge.id] = min([distance_edge[min_edge.id],min_distance])
                    else:
                        vote_edge[min_edge.id] = 1
                        distance_edge[min_edge.id] = min_distance


        #前面还有点
        if len(copy_node_list) != 0 :
            #查找的点需要与前面的点一致或相接
            print(2)
            the_last_node = copy_node_list[-1]
            new_nodes_set = set()

            if street_name != "":
                #有名字的路
                new_edges = BeijingWay.objects.filter(Q(source_id = the_last_node) & Q(street_name = street_name))
                print(3)
                if len(new_edges) == 0:
                    print(4)
                    break
                    #new_edges = BeijingWay.objects.filter(Q(source_id = the_last_node))
                    #print(4)
                #print(111)
                #print(the_last_node)
                #print(len(new_edges))
            else:
                #没名字的路
                new_edges = BeijingWay.objects.filter(Q(source_id = the_last_node))
                print(5)


            for edge in new_edges:
                #滤掉夹角过大的边
                if compute_angle(direction , edge.direction()) < 90:
                    #过滤掉差距过大的点
                    wkt_tuple_list = edge.wkt2list()
                    for wkt_point in wkt_tuple_list:
                        distance = haversine(float(lng),float(lat), \
                            wkt_point[0],wkt_point[1])
                        if distance < min_distance:
                            min_distance = distance
                            min_edge = edge

                    if min_edge.id in vote_edge:
                        vote_edge[min_edge.id] += 1
                        distance_edge[min_edge.id] = min([distance_edge[min_edge.id],min_distance])
                    else:
                        vote_edge[min_edge.id] = 1
                        distance_edge[min_edge.id] = min_distance
            #检验上一次的最后一条边：这个点可能仍然在上一条边中
            if len(pass_edges)  == 0:
                last_edge_id = result_way[-1]
                print(6)
            else:
                last_edge_id = pass_edges[-1]

            last_edge = BeijingWay.objects.get(id = last_edge_id)
            wkt_tuple_list = last_edge.wkt2list()
            for wkt_point in wkt_tuple_list:
                distance = haversine(float(lng),float(lat), \
                    wkt_point[0],wkt_point[1])
                if distance < min_distance:
                    min_distance = distance
                    min_edge = last_edge

            if min_edge.id in vote_edge:
                vote_edge[min_edge.id] += 1
                distance_edge[min_edge.id] = min([distance_edge[min_edge.id],min_distance])
            else:
                vote_edge[min_edge.id] = 1
                distance_edge[min_edge.id] = min_distance

        
        result_id = vote(vote_edge,distance_edge)
        if result_id not in result_way:
            result_way.append(result_id)
            min_edge = BeijingWay.objects.get(id = result_id)
            result_node.append(min_edge.target_id)


    #print(result_way)
    #print(result_node)

    return result_node, result_way


def haversine(lon1, lat1, lon2, lat2): # 经度1，纬度1，经度2，纬度2 （十进制度数）  
    """ 
    Calculate the great circle distance between two points  
    on the earth (specified in decimal degrees) 
    """  
    # 将十进制度数转化为弧度  
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])  
  
    # haversine公式  
    dlon = lon2 - lon1   
    dlat = lat2 - lat1   
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2  
    c = 2 * asin(sqrt(a))   
    r = 6371 # 地球平均半径，单位为公里  
    return c * r * 1000  

#将"2011-09-28 1:00:01 PM"转化为24小时制
def change_AM_PM(time_string):
    if time_string.split()[-1] == "PM":
        #将"2011-09-28 1:00:01 PM"转化为时间戳
        if int(time_string.split()[1].split(":")[0]) == 12 :
            new_time_string = time_string.split()[0] + " " + "00:" + time_string.split()[1].split(":")[1] +":" \
                + time_string.split()[1].split(":")[2]
            return new_time_string
        
        else:
            new_time_string = time_string.split()[0] + " " + str(int(time_string.split()[1].split(":")[0]) + 12) + ":" \
                + time_string.split()[1].split(":")[1] + ":" + time_string.split()[1].split(":")[2]
            return new_time_string
    
    if time_string.split()[-1] == "AM":
        new_time_string = time_string.split()[0] +" "+ time_string.split()[1]
        return  new_time_string

def CalDirection(geo_one, geo_two):
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
                return atan(slope) # 由于角度是跟y轴的夹角，所以需要90-
            else:   #3象限
                return atan(slope) + 180

        else: # 分子分母一正一负 二四象限
            if geo_two[0] > geo_one[0]: #四象限
                return 360 + atan(slope)
            else: #二象限
                return 90 + atan(slope)

#a,b都是360度制的角度 返回他们俩的夹角 0 - 180
def compute_angle(a , b):
    if abs(a - b) > 180:
        return abs(abs(a - b) - 360)
    else:
        return abs(a - b)

#去掉多余绕路的点
def cutUselessNodes(nodes):
    result = []
    for node in nodes:
        if node not in result:
            result.append(node)
        else:
            position = result.index(node)
            #删除该位置之后所有的点
            result = result[:position+1]
    return result

def vote(vote_dict , distance_dict):
    result_id = 0
    max_vote_num = 0
    min_distance = 0

    for key in vote_dict:
        if vote_dict[key] > max_vote_num:
            max_vote_num = vote_dict[key]
            result_id = key
            min_distance = distance_dict[key]
        elif vote_dict[key] == max_vote_num:
            if distance_dict[key] <= distance_dict[result_id]:
                max_vote_num = vote_dict[key]
                result_id = key
                min_distance = distance_dict[key]

    return result_id

def format_time(time_string):
    # 3/9/2009 12:30:54 -> 1970-01-01T00:00:00+00:00
    year = time_string.split()[0].split("/")[2]
    month = time_string.split()[0].split("/")[0]
    day = time_string.split()[0].split("/")[1]
    time = time_string.split()[1]
    hour = time.split(":")[0]
    m = time.split(":")[1]
    s = time.split(":")[2]

    #if int(month) < 10 :
        #month = "0" + month
    if int(day) < 10 :
        day = "0" + day
    if int(hour) < 10 :
        hour = "0" + hour

    new_time_string = year + "-" + month + "-" + day + "T" + hour + ":" + m + ":" + s + "+00:00"
    return new_time_string

#将edge序列转换为gps的序列(高德)
def covert_edge_to_gps_list(edge_list):
    result_list = []

    for edge_id in edge_list:
        edge = BeijingWayGraphhopper.objects.get(edge_id = int(edge_id))
        wkt_gaode = edge.wkt_gaode
        wkt_gaode_list = wkt_gaode.split(",")
        for item in wkt_gaode_list:
            lon = float(item.split(" ")[0])
            lat = float(item.split(" ")[1])
            result_list.append((lon, lat))

    return result_list

#将node序列转换为gps的序列(高德)
def covert_node_to_gps_list(node_list):
    result_list = []

    for node_id in node_list:
        node = BeijingNodeGraphhopper.objects.get(node_id = node_id)
        result_list.append((float(node.gaode_lon), float(node.gaode_lat)))

    return result_list