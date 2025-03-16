import csv
import numpy as np
import copy

class BusRoute:
    def __init__(self, routeId, routeName, busCnt, stopIdList):
        self.id = routeId
        self.name = routeName
        self.cnt = int(busCnt)
        self.stopIdList = list(map(int, stopIdList))

class BusStop:
    def __init__(self, stopId, stopName, latitude, longitude, region):
        self.id = int(stopId)
        self.name = stopName
        self.latitude = float(latitude)
        self.longitude = float(longitude)
        self.region= region
    
class BusData:

    busSpeed = 30 # km/h
    carSpeed = 30 # km/h
    walkSpeed = 3 # km/h

    stopList = []
    communityDict = {}
    stopIdList = []
    distMat = []

    @staticmethod
    def initStopData(stopDataFileName):
        BusData.stopList = []
        BusData.stopIdList = []
        with open(stopDataFileName, encoding='utf-8') as stopDataFile:
            stopDataReader = csv.reader(stopDataFile)
            for i, stop in enumerate(stopDataReader):
                if i == 0:
                    continue
                busStop = BusStop(*stop)
                BusData.stopList.append(busStop)

                BusData.stopIdList.append(int(stop[0]))

        BusData.stopIdList = np.array(BusData.stopIdList)

    @staticmethod
    def initCommunityData(communityDataFileName):
        BusData.communityDict = {}
        with open(communityDataFileName, encoding='utf-8') as f:
            r = csv.reader(f)
            for i, community in enumerate(r):
                if i == 0:
                    continue
                BusData.communityDict[community[1]] = {
                    'stopIdList': list(map(lambda stop: stop.id, filter(lambda stop: stop.region == community[1], BusData.stopList))),
                    'population': int(community[2])
                }
        # print(BusData.communityDict)

    @staticmethod
    def initDistanceMatrix():
        stopData = np.array([[complex(stop.latitude*111195, stop.longitude*91086)] for stop in BusData.stopList])
        BusData.distMat = abs(stopData.T - stopData)

    # @staticmethod
    # def calcDistanceById(sourceId, targetId):
    #     return BusData.distMat[BusData.stopIdList.index(sourceId)][BusData.stopIdList.index(targetId)]

    @staticmethod
    def calcIntervalByRoute(busCnt, stopIdList):
        totalTime = 0
        for i in range(len(stopIdList)-1):
            totalTime += BusData.distMat[BusData.stopIdList == stopIdList[i]][:, BusData.stopIdList == stopIdList[i+1]][0, 0]/BusData.busSpeed
        return totalTime/busCnt

    def __init__(self):
        self.routeList = []
        self.stopList = copy.deepcopy(BusData.stopList) 
    
    def getRouteById(self, routeId):
        return list(filter(lambda route: True if route.id == routeId else False, self.routeList))[0]

    def getStopById(self, stopId):
        return list(filter(lambda stop: True if stop.id == stopId else False, self.stopList))[0]
    
    def createNodeTable(self):
        return map(lambda stop: [stop.id, stop.name, stop.communityId], self.stopList)

    def saveNodeTable(self):
        with open('nodeTable.csv', '+w', encoding='utf-8', newline='') as nodeTable:
            nodeWriter = csv.writer(nodeTable)
            nodeWriter.writerow(['id', 'name', 'communityId'])
            nodeWriter.writerows(self.createNodeTable())

    def createEdgeTable(self):
        edgeTable = []
        index = 0
        for route in self.routeList:
            for j in range(len(route.stopIdList)-1):
                sourceId = route.stopIdList[j]
                targetId = route.stopIdList[j+1]
                distance = self.calcDistanceById(sourceId, targetId)
                edgeTable.append([index, sourceId, targetId, route.id, distance])
                index += 1
        return edgeTable

    def saveEdgeTable(self):
        with open('edgeTable.csv', '+w', encoding='utf-8', newline='') as edgeTable:
            edgeWriter = csv.writer(edgeTable)
            edgeWriter.writerow(['id', 'sourceId', 'targetId', 'nodeId', 'distance'])
            edgeWriter.writerows(self.createEdgeTable())

if __name__ == '__main__':
    busNetwork = BusData('./routeData.csv', './stopData.csv')
    busNetwork.saveEdgeTable()