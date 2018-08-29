# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models
#from mapmatching.function import CalDirection
import json
from math import *


class BeijingWay(models.Model):
    source_id = models.BigIntegerField(blank=True, null=True)
    target_id = models.BigIntegerField(blank=True, null=True)
    length = models.FloatField(blank=True, null=True)
    foot = models.IntegerField(blank=True, null=True)
    car = models.IntegerField(blank=True, null=True)
    bike = models.IntegerField(blank=True, null=True)
    street_name = models.CharField(max_length=255, blank=True, null=True)
    highway = models.CharField(max_length=255, blank=True, null=True)
    way_id = models.BigIntegerField(blank=True, null=True)
    wkt = models.TextField(blank=True, null=True)
    graphhopper_id = models.CharField(max_length=255, blank=True, null=True)

    #将wkt转换为tuple对
    def wkt2list(self):
        wkt_tuple_list = []
        wkt_list = self.wkt.split(',')
        #print(wkt_list)
        for item in wkt_list:
            #print(item)
            if item[0] == " ":
                #去掉第一位的空格
                item = item[1:]

            wkt_tuple_list.append((float(item.split()[0]) , float(item.split()[1])))

        return wkt_tuple_list

    #把source_id或target_id转为 node表中的id
    def nodeId2id(self , which_one = 'source'):
        if which_one == 'source':
            return(BeijingNode.objects.get(node_id = self.source_id).id)
        else:
            return(BeijingNode.objects.get(node_id = self.target_id).id)

    #返回路径的初始方向
    def direction(self):
        wkt_tuple_list = self.wkt2list()
        geo_one = wkt_tuple_list[0]
        geo_two = wkt_tuple_list[1]

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
        


    class Meta:
        managed = False
        db_table = 'beijing_way'




class BeijingNode(models.Model):
    lon = models.CharField(max_length=255, blank=True, null=True)
    lat = models.CharField(max_length=255, blank=True, null=True)
    gaode_lon = models.CharField(max_length=255, blank=True, null=True)
    gaode_lat = models.CharField(max_length=255, blank=True, null=True)
    node_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'beijing_node'




class Trajectory(models.Model):
    date = models.CharField(max_length=255, blank=True, null=True)
    lon = models.CharField(max_length=255, blank=True, null=True)
    lat = models.CharField(max_length=255, blank=True, null=True)
    user_id = models.IntegerField(blank=True, null=True)
    gaode_lon = models.CharField(max_length=255, blank=True, null=True)
    gaode_lat = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'trajectory'

    def toJSON(self):
        return json.dumps(dict([(attr, getattr(self, attr)) for attr in [f.name for f in self._meta.fields]]))

class BeijingWayGraphhopper(models.Model):
    edge_id = models.IntegerField(blank=True, null=True)
    from_node_id = models.IntegerField(blank=True, null=True)
    target_node_id = models.IntegerField(blank=True, null=True)
    length = models.FloatField(blank=True, null=True)
    street_name_one = models.CharField(max_length=255, blank=True, null=True)
    street_name_two = models.CharField(max_length=255, blank=True, null=True)
    wkt = models.TextField(blank=True, null=True)
    wkt_gaode = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'beijing_way_graphhopper'

    #将wkt转换为tuple对 flag = 1表示普通坐标系 flag = 2表示高德坐标系
    def wkt2list(self, flag = 1):
        wkt_tuple_list = []
        if flag == 1:
            wkt_list = self.wkt.split(',')
        else:
            wkt_list = self.wkt_gaode.split(',')
        #print(wkt_list)
        for item in wkt_list:
            #print(item)
            if item[0] == " ":
                #去掉第一位的空格
                item = item[1:]

            wkt_tuple_list.append((float(item.split()[0]) , float(item.split()[1])))

        return wkt_tuple_list

class ChengduWayGraphhopper(models.Model):
    edge_id = models.IntegerField(blank=True, null=True)
    from_node_id = models.IntegerField(blank=True, null=True)
    target_node_id = models.IntegerField(blank=True, null=True)
    length = models.FloatField(blank=True, null=True)
    street_name_one = models.CharField(max_length=255, blank=True, null=True)
    street_name_two = models.CharField(max_length=255, blank=True, null=True)
    wkt = models.TextField(blank=True, null=True)
    wkt_gaode = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'chengdu_way_graphhopper'

    #将wkt转换为tuple对 flag = 1表示普通坐标系 flag = 2表示高德坐标系
    def wkt2list(self, flag = 1):
        wkt_tuple_list = []
        if flag == 1:
            wkt_list = self.wkt.split(',')
        else:
            wkt_list = self.wkt_gaode.split(',')
        #print(wkt_list)
        for item in wkt_list:
            #print(item)
            if item[0] == " ":
                #去掉第一位的空格
                item = item[1:]

            wkt_tuple_list.append((float(item.split()[0]) , float(item.split()[1])))

        return wkt_tuple_list

class Eggs(models.Model):
    category = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    imgsrc1 = models.TextField(blank=True, null=True)
    imgsrc2 = models.TextField(blank=True, null=True)
    imgsrc3 = models.TextField(blank=True, null=True)
    answer = models.TextField(blank=True, null=True)
    title = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'eggs'

class BeijingRouteGraphhopper(models.Model):
    from_node_id = models.IntegerField(blank=True, null=True)
    target_node_id = models.IntegerField(blank=True, null=True)
    length = models.FloatField(blank=True, null=True)
    node_list = models.TextField(blank=True, null=True)
    way_list = models.TextField(blank=True, null=True)
    transfer_times = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'beijing_route_graphhopper'

class BeijingNodeGraphhopper(models.Model):
    node_id = models.IntegerField(blank=True, null=True)
    lat = models.TextField(blank=True, null=True)
    lon = models.TextField(blank=True, null=True)
    gaode_lat = models.TextField(blank=True, null=True)
    gaode_lon = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'beijing_node_graphhopper'

class ChengduNodeGraphhopper(models.Model):
    node_id = models.IntegerField(blank=True, null=True)
    lat = models.TextField(blank=True, null=True)
    lon = models.TextField(blank=True, null=True)
    gaode_lat = models.TextField(blank=True, null=True)
    gaode_lon = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'chengdu_node_graphhopper'


class ChengduRouteGraphhopper(models.Model):
    from_node_id = models.IntegerField(blank=True, null=True)
    target_node_id = models.IntegerField(blank=True, null=True)
    length = models.FloatField(blank=True, null=True)
    node_list = models.TextField(blank=True, null=True)
    way_list = models.TextField(blank=True, null=True)
    transfer_times = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'chengdu_route_graphhopper'

class Semantic(models.Model):
    user_id = models.IntegerField(blank=True, null=True)
    arrive = models.TextField(blank=True, null=True)
    departure = models.TextField(blank=True, null=True)
    location = models.TextField(blank=True, null=True)
    label = models.CharField(max_length=255, blank=True, null=True)
    restaurant = models.IntegerField(blank=True, null=True)
    market = models.IntegerField(blank=True, null=True)
    life = models.IntegerField(blank=True, null=True)
    school = models.IntegerField(blank=True, null=True)
    industry = models.IntegerField(blank=True, null=True)
    company = models.IntegerField(blank=True, null=True)
    residence = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'semantic'