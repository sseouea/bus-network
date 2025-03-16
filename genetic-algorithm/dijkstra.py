import heapq
from busData import BusData
import numpy as np
import time
import copy

class Timer:
    def __init__(self):
        self.t = time.time()
    def printDelta(self, title=''):
        print(f'{title}: {time.time() - self.t}')
        self.t = time.time()

def createNetworkDict(busDict, stopIdList):

    networkDict = {}
    carTimeMat = [[0 for j in range(len(stopIdList))] for i in range(len(stopIdList))]

    for idTuple in busDict:
      sourceId, targetId = idTuple
      if sourceId not in networkDict.keys():
        networkDict[sourceId] = {}
      time = BusData.distMat[BusData.stopIdList == sourceId][:, BusData.stopIdList == targetId][0][0]/BusData.busSpeed
      networkDict[sourceId][targetId] = time
      carTimeMat[stopIdList.index(sourceId)][stopIdList.index(targetId)] = time

    # for sourceId in stopIdList:
    #   if sourceId not in networkDict.keys():
    #     networkDict[sourceId] = {}
    #   for targetId in stopIdList:
    #     if sourceId == targetId:
    #       continue
    #     networkDict[sourceId][targetId] = BusData.distMat[BusData.stopIdList == sourceId][:, BusData.stopIdList == targetId][0][0]/BusData.busSpeed

    return networkDict, carTimeMat

def getRouteIdListFromIdList(routeList, idList):
  routeIdList = []
  for route in routeList:
    if np.isin(idList, route.stopIdList).all():
      routeIdList.append(route.id)
  return routeIdList

def createParameters(busNetwork, stopIdList):

  # newRouteList = copy.deepcopy(busNetwork.busData.routeList)
  newRouteIdList = []
  for route in busNetwork.busData.routeList:
    # for optimization model
    # newRouteIdList.append([*route.stopIdList, *reversed(route.stopIdList[:-1])])

    # for real model
    newRouteIdList.append([*route.stopIdList])
  
  # print(newRouteIdList)

  busDict = {}
  
  for j, route in enumerate(busNetwork.busData.routeList):
    for i in range(len(newRouteIdList[j])-1):
      idTuple = tuple(newRouteIdList[j][i:i+2])
      if idTuple not in busDict.keys():
        busDict[idTuple] = []
      if len(busDict[idTuple]) == 0 and route.id not in busDict[idTuple]:
        busDict[idTuple].append(route.id)
    

  deleteIdTupleList = []
  for idTuple in busDict:
    if len(busDict[idTuple]) == 0:
      deleteIdTupleList.append(idTuple)
  
  for idTuple in deleteIdTupleList:
    del busDict[idTuple]

  waitDict = {
    route.id: BusData.calcIntervalByRoute(route.cnt, newRouteIdList[i]) for i, route in enumerate(busNetwork.busData.routeList)
  }

  networkDict, carTimeMat = createNetworkDict(busDict, stopIdList)


  return [networkDict, busDict, waitDict, carTimeMat]

  # time = {}
  # for idTuple in bus:
  #   if idTuple[0] not in time.keys():
  #     time[idTuple[0]] = float('inf')
  #   if idTuple[1] not in time.keys():
  #     time[idTuple[1]] = float('inf')

def dijkstra(network, bus, wait, start):
  time = {node: float('inf') for node in network}
  count = {node: int('0') for node in network}

  time[start] = 0
  queue = []

  heapq.heappush(queue, [time[start], start, count[start], None])

  while queue:
    current_time, current_node, bus_count, current_bus = heapq.heappop(queue)


    if time[current_node] < current_time:
      continue

    if current_node not in network:
      continue

    for new_node, new_time in network[current_node].items():
      temp_current_bus = current_bus
      temp_bus_count = bus_count

      waiting_time = float('inf')

      if new_node not in time:
        time[new_node] = float('inf')

      if (current_node, new_node) not in bus.keys():
        continue
        
      if current_bus is None:
        for i in bus[(current_node, new_node)]:
          if wait[i] < waiting_time:
            current_bus = i
            waiting_time = wait[i]
      elif current_bus not in bus[(current_node, new_node)]:
        for bt in bus[(current_node, new_node)]:
          if wait[bt] < waiting_time:
            current_bus = bt
            waiting_time = wait[bt]
        bus_count += 1

      waiting_time = 0 if waiting_time == float('inf') else waiting_time
      total_time = current_time + new_time + waiting_time

      if total_time < time[new_node]:
        time[new_node] = total_time
        count[new_node] = bus_count
        heapq.heappush(queue, [total_time, new_node, bus_count, current_bus])
      
      current_bus = temp_current_bus
      bus_count = temp_bus_count

  return time, count

if __name__ == '__main__':
  print(dijkstra({1: {2: 10}}, {(1,2): ['1-1']}, {'1-1': 5}, 1))