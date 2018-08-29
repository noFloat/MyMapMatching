# coding=utf-8
from django.shortcuts import render
from django.http import HttpResponse
from mapmatching.models import *
from django.db.models import Q
import json
import copy
# Create your views here.
from django.views.decorators.csrf import csrf_exempt
import random
from mapmatching.function import *
import time
import urllib
import scipy.sparse as ss
import os
import pickle 
from mapmatching.convert import *
from mapmatching.RouteUpdate import *

# Create your views here.
def getGraphhopperSplitTrajectory(request):
    trajectorys = Trajectory.objects.all()

    length = len(trajectorys)
    index_list = []
    flag = 0 #判断一条路径是不是全部添加进了index_list

    for i in range(length):

        from_trajectory = trajectorys[i]
        target_trajectory = trajectorys[i+1]


        user_id_from = from_trajectory.user_id
        user_id_target = target_trajectory.user_id

        #计算时间间隔，判断两个轨迹是否是相邻的
        new_time_data1 = change_AM_PM(from_trajectory.date)
        new_time_data2 = change_AM_PM(target_trajectory.date)
        time_dis = time.mktime(time.strptime(new_time_data2,'%m/%d/%Y %H:%M:%S')) - \
                    time.mktime(time.strptime(new_time_data1,'%m/%d/%Y %H:%M:%S'))

        
        if time_dis > 10 * 60 or time_dis < 0:
            flag = 1

        index_list.append(i)

        if flag == 1:
            #数据字典  
            data = {}  
            #data['type'] = 'gpx'
            data['vehicle'] ='car'
            data['points_encoded'] ='false'
            data['key'] = '06a93e69-ff59-4807-87b5-7568326d2106'
            data['debug'] = 'true'
            url_values = urllib.parse.urlencode(data)  
            #拼接url
            #url = "https://graphhopper.com/api/1/route?point="+from_trajectory.lat+','+from_trajectory.lon + \
                #'&point=' + target_trajectory.lat+','+target_trajectory.lon + '&'
            #url = "https://graphhopper.com/api/1/route?point=39.92276,116.417478&point=39.910351,116.40668&"
            url = "http://localhost:8989/route?"
            for item in index_list:
                url += 'point='+trajectorys[item].lat+','+trajectorys[item].lon + '&'\
                
            full_url = url + url_values  
            #发起HTTP请求
            response = urllib.request.urlopen(full_url).read()  
            result = response.decode('UTF-8')
            #print(result)
            
            #解析JSON
            decode_data = json.loads(result)
            #print(decode_data)
            #print(decode_data['paths'][0])
            
            instructions = decode_data['paths'][0]['instructions']

            interval_list = []
            street_name_list = []
            distance_list = []
            #sign_list = []
            #print(instructions)
            for j in range(len(instructions)-1):
                distance = float(instructions[j]['distance'])
                interval = instructions[j]['interval']
                street_name = instructions[j]['street_name']
                #sign = instructions[j]['sign']

                interval_list.append(interval)
                street_name_list.append(street_name)
                distance_list.append(distance)
                #sign_list.append(int(sign))

            points_list = decode_data['paths'][0]['points']['coordinates']

            node_list, way_list = findWaysAndNodes(street_name_list , distance_list, interval_list , points_list)
            way_list = cutUselessNodes(way_list)
            
            #开始计算下面一条路径
            flag = 0
            index_list = []
            print(way_list)

    return HttpResponse('OK')

def getShowRoute(request):

    node_set = []
    draw_set = []

    f = open("./Correct/000_car_20081023040807.txt", 'r')
    way_id_list = []
    for line in f.readlines():
        way_id_list.append(int(line.strip('\n')))
    f.close()

    for i in range(len(way_id_list)):
        edge = BeijingWayGraphhopper.objects.filter(edge_id = int(way_id_list[i]))[0]
        wkt_tuple_list = edge.wkt2list(2)
        for j in range(len(wkt_tuple_list) - 1):
            dict_temp = {}
            dict_temp['start_node_lon'] = wkt_tuple_list[j][0]
            dict_temp['start_node_lat'] = wkt_tuple_list[j][1]
            dict_temp['end_node_lon'] = wkt_tuple_list[j+1][0]
            dict_temp['end_node_lat'] = wkt_tuple_list[j+1][1]
            draw_set.append(dict_temp)

    return render(request , 'getShowRoute.html' , {'draw_set' : draw_set})

#将graphhopper的way id转换为本地数据库中对应的记录
def getMatchGraphhopperID2MyID(request):
    f = open("./map_data/beijing_graphhopper.txt" , 'r', encoding = "utf-8")
    i = 0
    min_id = 0
    data_lines = f.readlines()
    while i < len(data_lines):
        print(str(i) + "/" + str(len(data_lines)))
        #第一行是路径描述
        
        data_list = data_lines[i].split(',')
        graphhopper_id = int(data_list[0])
        print("graphhopper_id:"+str(graphhopper_id))
        way_length = float(data_list[3])
        print(way_length)
        street_name = (data_list[-1].strip() if data_list[-1].strip() != '#' else "")

        #第二行是GPS的点对
        gps_list = data_lines[i+1].split(', ')
        gps_num = len(gps_list)
        gps_first = gps_list[0]
        #把"(39.906189737607306,116.38945675766745)"转成数字
        lat = float(gps_first.split(',')[0].split('(')[1])
        lon = float(gps_first.split(',')[1].split(')')[0])

        print("min_id:" + str(min_id))
        #距离误差正负5
        edges = BeijingWay.objects.filter( \
                    Q(street_name = street_name) &  \
                    Q(length__gte = way_length - 5) & \
                    Q(length__lte = way_length + 5) &
                    Q(id__gte = min_id) &\
                    Q(id__lte = min_id + 15)
                )

        if len(edges) == 0:
            #有可能几条路合成的一条路
            edges = BeijingWay.objects.filter( \
                    Q(street_name = street_name) &  \
                    Q(id__gt = min_id) &\
                    Q(id__lte = min_id + 15)
                )
            candidate_id = []
            distance = 0

            

            if len(edges) == 0:
                edges = BeijingWay.objects.filter( \
                    Q(street_name = street_name) &  \
                    Q(length__gte = way_length - 5) & \
                    Q(length__lte = way_length + 5) &
                    Q(id__gte = min_id - 10) &\
                    Q(id__lte = min_id + 5)
                )
                #回溯一下
                
                if len(edges) != 0:
                    old_distance = 0

                    for edge in edges:
                        wkt_tuple = edge.wkt2list() #路径的gps标号

                        print(edge.id)
                        print(abs(lat - wkt_tuple[0][1])) 
                        print(abs(lon - wkt_tuple[0][0])) 
                        #print(len(wkt_tuple) == gps_num)
                        print(abs(lat - wkt_tuple[0][1]) <= 0.01 \
                                    and abs(lon - wkt_tuple[0][0]) <= 0.01)
                        print((abs(lat - wkt_tuple[0][1]) <= 0.01 \
                                    and abs(lon - wkt_tuple[0][0]) <= 0.01))


                        if  old_distance == 0 and (\
                                (abs(lat - wkt_tuple[0][1]) <= 0.01 \
                                and abs(lon - wkt_tuple[0][0]) <= 0.01) \
                                or (abs(lat - wkt_tuple[0][1]) <= 0.01 \
                                and abs(lon - wkt_tuple[0][0]) <= 0.01)\
                                ) :

                            #滤掉不可靠的点
                            #if edge.id > min_id + 5:
                                #continue
                            old_distance = edge.length

                            print("update edge id :" + str(graphhopper_id) + " -> " + str(edge.id))
                            edge.graphhopper_id = str(graphhopper_id)
                            edge.save()

                            min_id = edge.id
                            continue

                        #添加双向边
                        if old_distance == edge.length:
                            print("update edge id :" + str(graphhopper_id) + " -> " + str(edge.id))
                            edge.graphhopper_id = str(graphhopper_id)
                            edge.save()

                            min_id = edge.id

                i += 2
                print("can not find match")
                continue

            last_distance_1 = 0 #寻找双向边

            if edges[0].length > way_length + 5:
                #有可能edge中的一条边是它的多条边
                graphhopper_id_string = ""
                graphhopper_id_string += str(graphhopper_id)

                edge = edges[0]
                total_lack_distance = edge.length - way_length
                old_street_name = street_name
                flag = 0
                last_distance_1 = edge.length

                while total_lack_distance > 5:
                    #k = input("Please input your name2:\n")

                    #读记录
                    i += 2

                    data_list = data_lines[i].split(',')
                    graphhopper_id = int(data_list[0])
                    print("2graphhopper_id:"+str(graphhopper_id))
                    way_length = float(data_list[3])
                    print(way_length)
                    street_name = (data_list[-1].strip() if data_list[-1].strip() != '#' else "")

                    #记录不匹配
                    if old_street_name != street_name:
                        flag = 1
                        break

                    graphhopper_id_string += ',' + str(graphhopper_id)
                    total_lack_distance -= way_length

                if flag == 0:
                    edge.graphhopper_id = graphhopper_id_string
                    edge.save()
                    min_id = edge.id

                    if len(edges) > 1:
                        for item in edges[1:]:
                            if item.length == last_distance_1:
                                item.graphhopper_id = graphhopper_id_string
                                item.save()
                                min_id = item.id

                    i += 2

                continue
                    
                
            
            last_distance = 0 #防止双向路误算成两条路
            for edge in edges:

                if last_distance == edge.length: #双向路
                    edge.graphhopper_id = str(graphhopper_id)
                    edge.save()
                    min_id = edge.id
                    continue

                if abs(distance - way_length) >= 5:
                    print("lack distance:" + str(abs(distance - way_length)))
                    distance += edge.length
                    edge.graphhopper_id = str(graphhopper_id)
                    edge.save()
                    min_id = edge.id
                    print("update edge id :" + str(graphhopper_id) + " -> " + str(edge.id))
                    last_distance = edge.length

                else:
                    break



        else:
            old_distance = 0

            for edge in edges:
                wkt_tuple = edge.wkt2list() #路径的gps标号

                print(edge.id)
                print(abs(lat - wkt_tuple[0][1])) 
                print(abs(lon - wkt_tuple[0][0])) 
                #print(len(wkt_tuple) == gps_num)
                print(abs(lat - wkt_tuple[0][1]) <= 0.01 \
                            and abs(lon - wkt_tuple[0][0]) <= 0.01)
                print((abs(lat - wkt_tuple[0][1]) <= 0.01 \
                            and abs(lon - wkt_tuple[0][0]) <= 0.01))


                if  old_distance == 0 and (\
                        (abs(lat - wkt_tuple[0][1]) <= 0.01 \
                        and abs(lon - wkt_tuple[0][0]) <= 0.01) \
                        or (abs(lat - wkt_tuple[0][1]) <= 0.01 \
                        and abs(lon - wkt_tuple[0][0]) <= 0.01)\
                        ) :

                    #滤掉不可靠的点
                    #if edge.id > min_id + 5:
                        #continue
                    old_distance = edge.length

                    print("update edge id :" + str(graphhopper_id) + " -> " + str(edge.id))
                    edge.graphhopper_id = str(graphhopper_id)
                    edge.save()

                    min_id = edge.id
                    continue

                #添加双向边
                if old_distance == edge.length:
                    print("update edge id :" + str(graphhopper_id) + " -> " + str(edge.id))
                    edge.graphhopper_id = str(graphhopper_id)
                    edge.save()

                    min_id = edge.id

                

        #k = input("Please input your name:\n")
        i += 2

    #(39.94764253380096,116.39196667206213), (39.94766488554325,116.39449912446362)
    #116.39196667206213 39.94764253380096
    #116.3944993 39.9476649, 116.3919667 39.9476426
    return HttpResponse('OK')

#把Grophhopper的数据存入数据库
def getConvertGrophhopperDataToDataBase(request):
    f = open("./map_data/beijing_graphhopper.txt" , 'r', encoding = "utf-8")

    i = 0
    data_lines = f.readlines()
    while i < len(data_lines):
        print(str(i) + "/" + str(len(data_lines)))
        #第一行是路径描述
        
        data_list = data_lines[i].split(',')
        graphhopper_id = int(data_list[0])
        from_node_id = int(data_list[1])
        to_node_id = int(data_list[2])
        #print("graphhopper_id:"+str(graphhopper_id))
        way_length = float(data_list[3])
        is_forward = float(data_list[4])
        is_backward = float(data_list[5])
        #print(way_length)
        if len(data_list) == 7:
            street_name_1 = (data_list[-1].strip() if data_list[-1].strip() != '#' else "")
            street_name_2 = ""
        else: #有两个路径名
            street_name_1 = (data_list[-2].strip() if data_list[-1].strip() != '#' else "")
            street_name_2 = (data_list[-1].strip() if data_list[-1].strip() != '#' else "")


        #第二行是GPS的点对
        gps_list = data_lines[i+1].split(', ')
        gps_string = ""
        gps_gaode_string = ""
        converter = Converter()

        for gps in gps_list:

            #把"(39.906189737607306,116.38945675766745)"转成数字
            lat = float(gps.split(',')[0].split('(')[1])
            lon = float(gps.split(',')[1].split(')')[0])
            gaode_lon, gaode_lat = converter.toGCJ02(lon,lat)

            if len(gps_string) > 0:
                gps_string += ',' + str(lon) + " " + str(lat)
                gps_gaode_string += ',' + str(gaode_lon) + " " + str(gaode_lat)
            else:
                gps_string += str(lon) + " " + str(lat)
                gps_gaode_string += str(gaode_lon) + " " + str(gaode_lat)

        if is_forward == 1:
            save_objects = BeijingWayGraphhopper()
            save_objects.edge_id = graphhopper_id
            save_objects.from_node_id = from_node_id
            save_objects.target_node_id = to_node_id
            save_objects.length = way_length
            save_objects.street_name_one = street_name_1
            save_objects.street_name_two = street_name_2
            save_objects.wkt = gps_string
            save_objects.wkt_gaode = gps_gaode_string
            save_objects.save()

        if is_backward == 1:

            save_objects = BeijingWayGraphhopper()
            save_objects.edge_id = graphhopper_id
            save_objects.from_node_id = to_node_id
            save_objects.target_node_id = from_node_id
            save_objects.length = way_length
            save_objects.street_name_one = street_name_1
            save_objects.street_name_two = street_name_2
            save_objects.wkt = gps_string
            save_objects.wkt_gaode = gps_gaode_string
            save_objects.save()


        i += 2

    return HttpResponse("OK")

def getConvertGPS(request):
    converter = Converter()
    lon, lat = converter.toGCJ02(116.417478,39.92276)
    print(lon , lat)
    lon, lat = converter.toWGS84(lon,lat)
    print(lon , lat)

    return HttpResponse("OK")

def getCollectRoute(request):

    return render(request , 'getCollectRoute.html')

@csrf_exempt
def getSaveGPX(request):
    data = json.loads(request.body.decode())
    output_path = "./user_data/"

    now_time = time.time()
    username = data['username']

    w_string = ""
    w_string += "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\" ?><gpx xmlns=\"http://www.topografix.com/GPX/1/1\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" creator=\"Graphhopper\" version=\"1.1\" xmlns:gh=\"https://graphhopper.com/public/schema/gpx/1.1\">\n";
    w_string += "<metadata><copyright author=\"OpenStreetMap contributors\"/><link href=\"http://graphhopper.com\"><text>GraphHopper GPX</text></link><time>1970-01-01T00:00:00+00:00</time></metadata>\n";
    w_string += "<trk><name>GraphHopper</name><trkseg>\n";

    converter = Converter()
    gps_list = data['gps']
    for i in range(len(gps_list)):
        #都是高德坐标系
        #{'O': 30.745026, 'M': 103.95263699999998, 'lng': 103.952637, 'lat': 30.745026}
        lat_gaode = gps_list[i]['lat']
        lng_gaode = gps_list[i]['lng']
        lon, lat = converter.toWGS84(lng_gaode,lat_gaode)

        time_local = time.localtime(now_time + 10 * i)
        # 3/9/2009 12:30:54 -> 1970-01-01T00:00:00+00:00
        time_string = time.strftime("%m/%d/%Y %H:%M:%S",time_local)
        #print(time_string)
        format_time_string = format_time(time_string)

        w_string += "<trkpt lat=\"" + str(lat) + "\" lon=\"" + str(lon) + "\"><time>"+format_time_string+"</time></trkpt>\n";
                
    w_string += "</trkseg></trk></gpx>"


    filename = username + "_" + str(now_time)
    target_file = open(output_path+filename+".gpx",'w',encoding='utf-8')
    target_file.write(w_string)
    target_file.close()

    egg_flag = random.randint(1, 4)

    if egg_flag == 3:
        max_size = len(Eggs.objects.all())
        egg_id = random.randint(1, max_size)
        egg = Eggs.objects.get(id = egg_id)

        egg_dict = {}
        egg_dict['category'] = egg.category
        egg_dict['description'] = egg.description
        egg_dict['imgsrc1'] = egg.imgsrc1
        egg_dict['imgsrc2'] = egg.imgsrc2
        egg_dict['imgsrc3'] = egg.imgsrc3
        egg_dict['answer'] = egg.answer
        egg_dict['title'] = egg.title

        return HttpResponse(json.dumps(egg_dict), content_type='application/json')

    return HttpResponse(json.dumps("ok"), content_type='application/json')


@csrf_exempt
def getSaveName(request):
    data = request.body.decode()
    print(data)
    f = open("./name.txt",'a',encoding="utf-8")
    f.write(str(data))
    f.write('\n')
    f.close()
    

    return HttpResponse(json.dumps("ok"), content_type='application/json')


def getCreateRouteTransfer(request):
    a = 1
    if a == 1:
        #取一个基于点的邻接矩阵
        result_dict = {}
        edges = ChengduWayGraphhopper.objects.all()
        for item in edges:
            temp_list = {}
            temp_list['target_node_id'] = item.target_node_id
            temp_list['length'] = item.length
            temp_list['edge_id'] = item.edge_id

            if item.from_node_id not in result_dict:
                result_dict[item.from_node_id] = []
            result_dict[item.from_node_id].append(temp_list)

        i = 0
        for k in result_dict:
            for item in result_dict[k]:
                route = ChengduRouteGraphhopper()
                route.from_node_id = k
                route.target_node_id = item['target_node_id']
                route.length = item['length']
                route.node_list = str(k) + " " + str(item['target_node_id'])
                route.way_list = item['edge_id']
                route.transfer_times = 1
                route.save()

            i += 1
            print(str(i) + "/" +str(len(result_dict)))

def getCreateNodesTable(request):
    f = open("./nodes.txt",'r',encoding="utf-8")
    data = f.readlines()
    f.close()

    converter = Converter()

    for line in data:
        node_id = int(line.strip('\n').split(':')[0])
        lat_lon = line.strip('\n').split(':')[1]
        lat = float(lat_lon.split(',')[0])
        lon = float(lat_lon.split(',')[1])
        lon_gaode, lat_gaode = converter.toGCJ02(lon, lat)
        node = ChengduNodeGraphhopper()
        node.node_id = node_id
        node.lat = str(lat)
        node.lon = str(lon)
        node.gaode_lat = str(lat_gaode)
        node.gaode_lon = str(lon_gaode)
        node.save()
    
    return HttpResponse("OK")


def getCollectPOI(request):

    nodes = BeijingNodeGraphhopper.objects.all()
    node_set = []

    for i in range(len(nodes)):

        dict_temp = {}
        dict_temp['node_id'] = nodes[i].node_id
        dict_temp['lat'] = float(nodes[i].gaode_lat)
        dict_temp['lon'] = float(nodes[i].gaode_lon)

        node_set.append(dict_temp)


    return render(request , 'getCollectPOI.html' , {'node_set' : json.dumps(node_set)})

@csrf_exempt
def getSavePOI(request):
    data = request.body.decode()

    f = open("./POI/Beijing/"+str(time.time())+'.txt', 'w', encoding='utf-8')
    f.write(data)
    f.close()


    return HttpResponse(json.dumps("ok"), content_type='application/json')

#利用测试数据生成起点到终点的结点对
def getCreateTestSource2DestinationPair(request):
    test_path = './Test/Taxi/'
    file_name_list = os.listdir(test_path)
    user_point_dict = {}

    for file_name in file_name_list:
        user_id = int(file_name.split("_")[0])

        f = open(test_path + file_name)
        lines = f.readlines()
        edge_id_begin = int(lines[0].strip('\n'))
        #print(lines[-1])
        edge_id_end = int(lines[-2].strip('\n'))

        f.close()
        try:
            source_node_id = BeijingWayGraphhopper.objects.filter(edge_id = edge_id_begin)[0].from_node_id
            target_node_id = BeijingWayGraphhopper.objects.filter(edge_id = edge_id_end)[0].target_node_id
        except:
            print(0)
        if user_id not in user_point_dict:
            user_point_dict[user_id] = set()

        user_point_dict[user_id].add(source_node_id)
        user_point_dict[user_id].add(target_node_id)

    for key in user_point_dict:
        f = open('./Test/Pair/Taxi/' + str(key) + '.txt', 'w', encoding='utf-8')
        w_string = ""
        for i in range(100):
            result = random.sample(user_point_dict[key],2)
            w_string += str(result[0]) + ' ' + str(result[1]) + '\n'

        f.write(w_string)
        f.close()

    return HttpResponse('ok')

def getDoRouteUpdate(request):
    FAMILIARITY_PATH = "./Train/Taxi_familiarity/"
    TEST_EDGE_PATH = "./Test/Edges/Taxi/"
    FAMILIARITY_ALL_PATH = "./Train/Taxi_familiarity_all/"
    RESULT_PATH = "./Test/Results/Taxi/"
    
    '''
    #user_id = 128
    user_id = request.GET.get('user_id')
    file_id = request.GET.get('file_id')
    #读取用户熟悉度
    f = open(FAMILIARITY_PATH + str(user_id) + '.txt', 'r')
    familiarity_dict = {}
    for line in f.readlines():
        content = line.strip('\n').split(":")
        familiarity_dict[int(content[0])] = int(content[1])
    f.close()
    #读取测试路径
    f = open(TEST_EDGE_PATH + str(user_id) + '_'+file_id+'.txt', 'r')
    origin_path = []
    lines = f.readlines()
    #print(lines[0].strip('\n').split("->"))
    from_node_id = int(lines[0].strip('\n').split("->")[0])
    target_node_id = int(lines[0].strip('\n').split("->")[1])
    for line in lines[1:]:
        content = line.strip('\n')
        origin_path.append(int(content))
    f.close()
    #将 edge id 序列 转化为 node id 序列
    node_set = []
    node_set.append(from_node_id)

    for i in range(len(origin_path)):
        edges = BeijingWayGraphhopper.objects.filter(Q(from_node_id = node_set[i]) & \
            Q(edge_id = origin_path[i]))
        print(str(node_set[i]) + "-|")
        print(origin_path[i])
        node_set.append(edges[0].target_node_id)

    ru = RouteUpdate(origin_path, node_set, familiarity_dict, FAMILIARITY_ALL_PATH, user_id)
    segments, length, compute_time, n = ru.doUpdate()
    f = open(RESULT_PATH + str(user_id) + 'TO' + str(user_id) + '_' + file_id+'.txt', 'w', encoding='utf-8')
    w_string = ""
    w_string += str(from_node_id) + '->' + str(target_node_id) + '\n'
    w_string += 'segment_length:' + str(length) + '\n'
    w_string += 'compute_time:' + str(compute_time) + '\n'
    for every_segment in segments:
        for item in every_segment:
            w_string += str(item) + ' '
        w_string += '\n'
    f.write(w_string)
    f.close()
    
    '''
    flie_list = os.listdir(FAMILIARITY_PATH)
    j = 0
    all_length = 0
    all_time = 0
    for user_familiarity_file in flie_list:
        user_id = int(user_familiarity_file.split('.')[0])
        
        ##########
        #if user_id != 1:
        #    continue
        ##########
        #print(user_id)
        #读取用户熟悉度
        f = open(FAMILIARITY_PATH + str(user_id) + '.txt', 'r')
        familiarity_dict = {}
        for line in f.readlines():
            content = line.strip('\n').split(":")
            familiarity_dict[int(content[0])] = int(content[1])
        f.close()
        #读取测试路径
        test_file_list = os.listdir(TEST_EDGE_PATH)
        for test_file in test_file_list:
            f = open(TEST_EDGE_PATH + test_file, 'r')
            ############
            #file_user_id = test_file.split("_")[0]
            
            #if file_user_id[0] != '1':
            #    continue
            ############
            print(test_file)
            origin_path = []
            lines = f.readlines()
            #print(lines[0].strip('\n').split("->"))
            from_node_id = int(lines[0].strip('\n').split("->")[0])
            target_node_id = int(lines[0].strip('\n').split("->")[1])
            for line in lines[1:]:
                content = line.strip('\n')
                origin_path.append(int(content))
            f.close()
            #将 edge id 序列 转化为 node id 序列
            node_set = []
            node_set.append(from_node_id)

            flag = 0
            for i in range(len(origin_path)):
                edges = BeijingWayGraphhopper.objects.filter(Q(from_node_id = node_set[i]) & \
                    Q(edge_id = origin_path[i]))
                if len(edges) == 0:
                    flag = 1
                    break
                #print(str(node_set[i]) + "-|")
                #print(origin_path[i])
                node_set.append(edges[0].target_node_id)

            if flag == 1:
                continue
            j += 1
            ru = RouteUpdate(origin_path, node_set, familiarity_dict, FAMILIARITY_ALL_PATH, user_id)
            segments, length, compute_time, n = ru.doUpdate()
            f = open(RESULT_PATH + str(user_id) + 'TO' + test_file, 'w', encoding='utf-8')
            w_string = ""
            w_string += str(from_node_id) + '->' + str(target_node_id) + '\n'
            w_string += 'segment_length:' + str(length) + '\n'
            w_string += 'compute_time:' + str(compute_time) + '\n'
            w_string += 'node num:' + str(n) + '\n'
            for every_segment in segments:
                for item in every_segment:
                    w_string += str(item) + ' '
                w_string += '\n'
            f.write(w_string)
            f.close()

            all_time += compute_time
            all_length += length
            print("average time:", all_time/j)
            print("average length:", all_length/j)





    return HttpResponse("OK")

def getShowUpdatedRoute(request):
    #读取测试路径
    TEST_EDGE_PATH = "./Test/Edges/Geolife/"
    RESULT_EDGE_PATH = "./Test/Results/Geolife/"

    draw_set = []
    draw_set_2 = []

    #updated_edge_list = [[27374, 27375], [38018, 70135, 48670, 48657], [48640, 48641, 48642, 48643, 48644, 48645, 48646], [27500, 27333, 27334, 2248, 2244, 2245, 2246, 59405, 27588, 27591, 21450, 21451, 27215, 27216, 27217, 21460, 21437, 31968, 27212, 28314], [21457, 6831, 21747, 21751, 31648, 31649, 31650, 6798, 39951, 59408, 3109, 29914, 29915, 32850, 32851, 23972, 23981, 51911, 51912, 34539, 30127, 30128, 47289, 6493, 30119, 6491, 6492, 99204, 30126, 99202, 99203, 34537, 6797, 520, 38133, 3573, 3574, 3575, 33665, 33666, 33667, 6822, 6823, 6824, 6825, 32887, 21878, 21856, 21865, 21869, 32885, 32886, 1701, 32863, 32864, 1704, 1705, 1751, 1752, 1747, 1744, 1745, 1746, 36518, 36532, 36533, 3108, 4010, 42433, 42440, 56534, 42431, 42439, 42384, 42416, 42417, 42418, 42419, 42393, 42414, 32101, 3111, 3112, 32234, 32211, 42395, 42409, 42410, 42411, 42412, 42413, 42375, 42379, 42380, 42381, 11913, 13293, 13294, 42351, 42348, 42349, 42350, 42204, 42193, 42205, 42195, 42200, 42196, 42208, 42197, 42183, 42180, 42181, 56741, 56738, 12007, 12008, 56767, 56770, 9045, 56782, 56783, 87932, 87934, 87935, 87936, 77841, 77842, 85848, 85849, 85850, 85851, 88107, 88106, 56254, 56256, 56257, 59679, 59678, 59675, 59685, 59677, 92026, 92027, 92028, 92024, 59672, 88930]]
    updated_edge_list = []
    updated_edge_list_2 = []
    #for item in updated_edge_list:
    #   for item2 in item:
    #       updated_edge_list_2.append(item2)


    user_id = request.GET.get('user_id')
    file_id = request.GET.get('file_id')
    #result####
    f = open(RESULT_EDGE_PATH + "0TO" + str(user_id) + '_' + file_id +'.txt', 'r')
    lines = f.readlines()
    for line in lines[4:]:
        edge_list = line.strip('\n').split(" ")
        edge_list = [int(item) for item in edge_list if item != ""]
        updated_edge_list.append(edge_list)
    #origin####
    #user_id = 128
    f = open(TEST_EDGE_PATH + str(user_id) + '_' + file_id +'.txt', 'r')
    origin_path = []
    lines = f.readlines()
    #print(lines[0].strip('\n').split("->"))
    from_node_id = int(lines[0].strip('\n').split("->")[0])
    target_node_id = int(lines[0].strip('\n').split("->")[1])
    for line in lines[1:]:
        content = line.strip('\n')
        origin_path.append(int(content))
    f.close()

    for i in range(len(origin_path)):
        edge = BeijingWayGraphhopper.objects.filter(edge_id = int(origin_path[i]))[0]
        wkt_tuple_list = edge.wkt2list(2)
        for j in range(len(wkt_tuple_list) - 1):
            dict_temp = {}
            dict_temp['start_node_lon'] = wkt_tuple_list[j][0]
            dict_temp['start_node_lat'] = wkt_tuple_list[j][1]
            dict_temp['end_node_lon'] = wkt_tuple_list[j+1][0]
            dict_temp['end_node_lat'] = wkt_tuple_list[j+1][1]
            draw_set.append(dict_temp)

    color_char = [0,1,2,3,4,5,6,7,8,9,'A','B','C','D','E','F'] #用于随机生成16进制数

    for i in range(len(updated_edge_list)):
        temp_list = []
        for item in updated_edge_list[i]:
            edge = BeijingWayGraphhopper.objects.filter(edge_id = int(item))[0]
            wkt_tuple_list = edge.wkt2list(2)
            for j in range(len(wkt_tuple_list) - 1):
                dict_temp = {}
                dict_temp['start_node_lon'] = wkt_tuple_list[j][0]
                dict_temp['start_node_lat'] = wkt_tuple_list[j][1]
                dict_temp['end_node_lon'] = wkt_tuple_list[j+1][0]
                dict_temp['end_node_lat'] = wkt_tuple_list[j+1][1]
                temp_list.append(dict_temp)
        draw_set_2.append({})
        draw_set_2[i]['road_gps_list'] = temp_list
        color_string = "#"
        for k in range(6):
            color_string += str(color_char[random.randint(0,15)])
        draw_set_2[i]['color'] = color_string

    return render(request , 'getShowUpdatedRoute.html' , {'draw_set' : draw_set, 'draw_set_2' : draw_set_2})

def getCollectSemanticLabel(request):
    semantic = Semantic.objects.filter(user_id = 1)
    result = {}
    if len(semantic) != 0:
        last_one = semantic[len(semantic)-1]
        result['info'] = 'success'
        result['lon'] = float(last_one.location.split(",")[0])
        result['lat'] = float(last_one.location.split(",")[1])
        result['departure'] = last_one.departure
        result['label'] = last_one.label
    else:
        result['info'] = 'no_data'

    return render(request , 'getCollectSemanticLabel.html', {'init':json.dumps(result)})

@csrf_exempt
def getSaveSemanticLabel(request):
    data = request.body.decode()
    print(data)
    print(1)
    obj = json.loads(data)

    se = Semantic()
    se.user_id = int(obj['user_id'])
    se.arrive = obj['arrive']
    se.departure = obj['departure']
    se.location = obj['location']
    se.label = obj['label']
    se.restaurant = int(obj['poi'][0])
    se.market = int(obj['poi'][1])
    se.life = int(obj['poi'][2])
    se.school = int(obj['poi'][3])
    se.industry = int(obj['poi'][4])
    se.company = int(obj['poi'][5])
    se.residence = int(obj['poi'][6])
    se.save()



    return HttpResponse(json.dumps("ok"), content_type='application/json')

#获取用户最近的数据
@csrf_exempt
def getUserNewLocation(request):
    user_id = int(request.GET.get('user_id'))
    semantic = Semantic.objects.filter(user_id = user_id)
    result = {}
    if len(semantic) != 0:
        last_one = semantic[len(semantic)-1]
        result['info'] = 'success'
        result['lon'] = float(last_one.location.split(",")[0])
        result['lat'] = float(last_one.location.split(",")[1])
        result['departure'] = last_one.departure
        result['label'] = last_one.label
    else:
        result['info'] = 'no_data'


    return HttpResponse(json.dumps(result), content_type='application/json')