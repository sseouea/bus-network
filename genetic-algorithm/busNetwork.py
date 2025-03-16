import numpy as np
import random
from busData import BusData, BusRoute
from dijkstra import *
import itertools
import copy

class BusNetwork:

    @staticmethod
    def calcPassengerSatisfaction(transferCnt, leastTime, carTime):
        return (leastTime/(leastTime - carTime))/((transferCnt+1)**(1/2))

    def __init__(self, routeIdList, maxBusCnt):

        self.busData = BusData()
        self.score = 0

        # initial state는 node data만 주어져 있다고 가정
        # route initializing 
        self.busData.routeList = self.getInitialBusRouteList(routeIdList, maxBusCnt)
    
    def getInitialBusRouteList(self, routeIdList, maxBusCnt):
        busRouteList = []
        randomStopList = random.sample(BusData.stopList, len(routeIdList))
        remainedBusCnt = maxBusCnt - len(routeIdList) 
        for i, routeId in enumerate(routeIdList):
            busCnt = 0 if remainedBusCnt == 0 else maxBusCnt//len(routeIdList)
            busRoute = BusRoute(routeId, f'bus-{routeId}', busCnt + 1, [randomStopList[i].id]) # 각 종류의 버스가 적어도 1개 있다고 가정
            remainedBusCnt -= busCnt
            busRouteList.append(busRoute)
        if remainedBusCnt > 0:
            route = random.choice(busRouteList)
            route.cnt += remainedBusCnt
        return busRouteList

    def getRandomStopIdNotInRoute(self, route):
        stopId = route.stopIdList[0] 
        while stopId in route.stopIdList:
            stopId = random.choice(BusData.stopIdList)
        return stopId
    
    def getCloseStopId(self, stopId, route):
        # print(f'busstops: {BusData.stopIdList}')
        # print(f'stopId: {stopId}')
        # print(f'DistMat-{stopId}: ', BusData.distMat)
        # print(f'if-{stopId}: ', BusData.stopIdList == stopId)
        # print(f'sub-{stopId}: ', BusData.distMat[BusData.stopIdList == stopId])
        distList = BusData.distMat[BusData.stopIdList == stopId][0]
        sortedDistList = sorted(distList)

        closeIdList = list(map(lambda dist: BusData.stopIdList[np.where(distList == dist)[0][0]], sortedDistList))
        closeIdListNotInRoute = list(filter(lambda id: id not in route.stopIdList, closeIdList))

        if len(closeIdListNotInRoute) == 0:
            return None

        closeIdListNotInRoute = closeIdListNotInRoute[:5]
        # closeIdList = closeIdList[1:len(closeIdList)//30]
        randomStopId = random.choice(closeIdListNotInRoute)



        # while randomStopId in route.stopIdList:
        #     randomStopId = random.choice(closeIdList)
        
        # print('where', np.where(BusData.stopIdList == randomStopId)[0])
        # print('closeidList', closeIdList)
        # print('randomStopId', randomStopId)
        
        return randomStopId

    def crossover(self):
        for route in self.busData.routeList:
            # print('cross', route.id, route.stopIdList)
            if random.randint(1, 100) < 30:
                oldStopId = random.choice(route.stopIdList)
                newStopId = self.getCloseStopId(oldStopId, route)
                if newStopId != None:
                    route.stopIdList[route.stopIdList.index(oldStopId)] = newStopId

    def mutation(self):
        self.mutateBusRoute()
        self.mutateBusCnt()
    
    def mutateBusRoute(self):
        for route in self.busData.routeList:
            # print('mutate', route.id, route.stopIdList)
            rand = random.randint(1, 100)
            idx = random.choice([0,-1])
            if rand <= 70:
            # if rand <= 50:
                newStopId = self.getCloseStopId(route.stopIdList[idx], route)

                if newStopId == None:
                    continue

                if idx == -1:
                    idx = len(route.stopIdList)
                route.stopIdList.insert(idx, newStopId)
                
            elif rand <= 85 and len(route.stopIdList) != 1:
            # elif len(route.stopIdList) != 1:
                del route.stopIdList[idx]
    
    def mutateBusCnt(self):
        for route in self.busData.routeList:
            delta = random.choice([0,0,0,0,1])

            anotherRoute = random.choice(self.busData.routeList)

            if route.cnt + delta <= 0 or anotherRoute.cnt - delta <= 0:
                continue

            route.cnt += delta
            anotherRoute.cnt -= delta

    def evaluate(self):

        stopIdSet = set()
        for route in self.busData.routeList:
            if len(route.stopIdList) != 1:
                stopIdSet.update(route.stopIdList)

        if len(stopIdSet) <= 1:
            self.score = 0
            return
        
        stopIdList = sorted(list(stopIdSet))

        # permutation = np.array(list(itertools.permutations(stopIdList, 2)))

        parameters = createParameters(self, stopIdList)
        # timer.printDelta('Parmeters')

        leastTimeMat = []
        transferMat = []

        # print('====stopIdList====')
        # print(stopIdList)

        # print('===route===')
        # for route in self.busData.routeList:
        #     print(route.id, route.stopIdList)
        # print('===networkDict===')
        # print(parameters[0])
        # print('===busDict===')
        # print(parameters[1])
        # print('===waitDict===')
        # print(parameters[2])


        carTimeMat = parameters[3]

        for sourceId in stopIdList:

            # print(f'sourceId: {sourceId}')

            if sourceId not in parameters[0].keys():
                leastTimeMat.append([float('inf')]*len(stopIdList))
                transferMat.append([0]*len(stopIdList))
                continue

            leastTimeDict, transferDict = dijkstra(*parameters[:3], sourceId)

            keyList = leastTimeDict.keys()
            
            # print(f'keyList: {keyList}')
            # print(f'leasttime: {leastTimeDict}')
            # print(f'transfer: {transferDict}')

            _leastTimeList = list(map(lambda x: leastTimeDict[x] if x in keyList else float('inf'), stopIdList))
            transferList = list(map(lambda x: transferDict[x] if x in keyList else 0, stopIdList))

            leastTimeList = list(map(lambda x: x if x != 0 else float('inf'), _leastTimeList))

            # print(f'leasttime: {leastTimeList}')
            # print(f'transfer: {transferList}')

            leastTimeMat.append(leastTimeList)
            transferMat.append(transferList)
        # result = Dijkstra(self.busData)
        # print('===bus===')
        # print(np.shape(leastTimeMat))
        # print('===transfer===')
        # print(np.shape(transferMat))

        # timer.printDelta('Dijkstra')

        
        # print('===distMat===')
        # print(BusData.distMat)
        # print('===car===')
        # print(np.shape(carTimeMat))
        scoreMat = BusNetwork.calcPassengerSatisfaction(np.array(transferMat), np.array(leastTimeMat), carTimeMat)
        totalScore = 0
        totalPopulation = 0
        np.nan_to_num(scoreMat, copy=False)
        # scoreMat[scoreMat == np.nan] = 0

        # print(f'scoreMat: {scoreMat}')

        for region in BusData.communityDict:
            if len(BusData.communityDict[region]['stopIdList']) == 0:
                continue
            population = BusData.communityDict[region]['population']
            totalPopulation += population
            booleanMap = np.isin(list(stopIdSet), BusData.communityDict[region]['stopIdList'])
            # print(f'booleanMap: {booleanMap}')
            score = (np.sum(scoreMat[booleanMap])/len(BusData.stopIdList)**2)
            totalScore += score*population

        print(f'score: {totalScore/totalPopulation}')

        self.score = totalScore/totalPopulation
    


    # def print_bus(self): # 잘 작동하는지 확인용으로 만든 거, 시간되면 csv 파일 형태로 저장되게 하는거 추천
    #     bus_info = {'id' : [], 'amount' : [], 'route' : [], 'distance' : [], 'interval' : []}
    #     for bus in self.bus:
    #         bus_info['id'].append(bus.id)
    #         bus_info['amount'].append(bus.amount)
    #         bus_info['route'].append(bus.route)
    #         bus_info['distance'].append(bus.route_distance)
    #         bus_info['interval'].append(bus.interval)

    #     bus_df = pd.DataFrame(bus_info)
    #     display(bus_df)
    #     print('')