import math

class Converter(object):

    def __init__(self):
        self.a = 6378245.0
        self.pi = 3.14159265358979324
        self.ee = 0.0066934216229659432

    #转高德坐标系
    def toGCJ02(self , lon , lat):
        dLon, dLat = self.calDev(lon , lat)
        retLat = lat + dLat
        retLon = lon + dLon
        return retLon , retLat

    #GCJ-02 to WGS-84
    def toWGS84(self , lon , lat):
        dLon, dLat = self.calDev(lon, lat)
        retLat = lat - dLat
        retLon = lon - dLon
        dLon, dLat = self.calDev(retLon, retLat)
        retLat = lat - dLat
        retLon = lon - dLon
        return retLon , retLat
    

    def calDev(self , lon , lat):
        dLat = self.calLat(lon - 105.0, lat - 35.0)
        dLon = self.calLon(lon - 105.0, lat - 35.0)
        radLat = lat / 180.0 * self.pi
        magic = math.sin(radLat)
        magic = 1 - self.ee * magic * magic
        sqrtMagic = math.sqrt(magic)
        dLat = (dLat * 180.0) / ((self.a * (1 - self.ee)) / (magic * sqrtMagic) * self.pi)
        dLon = (dLon * 180.0) / (self.a / sqrtMagic * math.cos(radLat) * self.pi)
        return dLon, dLat

    def calLat(self , x , y):
        ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 \
                * math.sqrt(abs(x))
        ret += (20.0 * math.sin(6.0 * x * self.pi) + 20.0 * math.sin(2.0 * x * self.pi)) * 2.0 / 3.0
        ret += (20.0 * math.sin(y * self.pi) + 40.0 * math.sin(y / 3.0 * self.pi)) * 2.0 / 3.0
        ret += (160.0 * math.sin(y / 12.0 * self.pi) + 320 * math.sin(y * self.pi / 30.0)) * 2.0 / 3.0
        return ret

    def calLon(self , x , y):
        ret = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * math.sqrt(abs(x))
        ret += (20.0 * math.sin(6.0 * x * self.pi) + 20.0 * math.sin(2.0 * x * self.pi)) * 2.0 / 3.0
        ret += (20.0 * math.sin(x * self.pi) + 40.0 * math.sin(x / 3.0 * self.pi)) * 2.0 / 3.0
        ret += (150.0 * math.sin(x / 12.0 * self.pi) + 300.0 * math.sin(x / 30.0 * self.pi)) * 2.0 / 3.0
        return ret