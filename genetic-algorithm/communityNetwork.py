import csv
import random
from genetic import *
import math
from resultProcessing import *

class Community_Network:
    def __init__(self, popuDataFileName, routeCnt, maxBuscnt, networkCnt, selectionCnt, generationCnt):

        # variable
        self.resultPath = makeResultPath()
        self.maxBuscnt = maxBuscnt
        self.communities = []

        # community population 정보 가져오기
        communities = []
        with open(popuDataFileName, encoding='utf-8') as popuDataFile:
            popuDataReader = csv.reader(popuDataFile)
            for i, community in enumerate(popuDataReader):
                if i == 0:
                    continue
                # community(name) population
                self.communities.append(community[1])
                communities.append([community[1], community[2]])
        
        self.community_populations = {community : int(population) for community, population in communities}

        #busData = [bus 종류 개수, network 상 bux의 총 개수(제한)]
        total_population = sum(self.community_populations.values())
        bus_type_idxs = dict()
        bus_amount_nums = dict()

        for i, community in enumerate(self.communities):
            rate = self.community_populations[community] / total_population
            bus_type_idx = [(str(i) + '-' + str(idx)) for idx in range(math.floor((routeCnt - len(self.communities)) * rate) + 1)]
            bus_type_idxs[community] = bus_type_idx

        while sum(list(map(lambda idxs : len(idxs), bus_type_idxs.values()))) < routeCnt:
            community = random.choice(self.communities)
            new_id = str(self.communities.index(community)) + '-' + str(len(bus_type_idxs[community]))
            bus_type_idxs[community].append(new_id)

        for i, community in enumerate(self.communities):
            rate = self.community_populations[community] / total_population
            bus_amount_num = math.floor((maxBuscnt - sum(list(map(lambda bus_idx : len(bus_idx), bus_type_idxs.values())))) * rate) + len(bus_type_idxs[community])
            bus_amount_nums[community] = bus_amount_num

        while sum(bus_amount_nums.values()) < maxBuscnt:
            community = random.choice(self.communities)
            bus_amount_nums[community] = bus_amount_nums[community] + 1

        self.community_buses = {community : [bus_type_idxs[community], bus_amount_nums[community]] for community in self.communities}
        print(self.community_buses.items())

        # nodeDataFileName 저장
        nodeDataFileName = ['./data/region/regionStop_{}.csv'.format(i) for i in range(20)]

        # community별 genetic class 생성
        self.community_networks = []
        for id, name in enumerate(self.communities):
            print(f'======={name}=======')
            self.community_networks.append(Genetic(nodeDataFileName[id], './data/population.csv', self.community_buses[name][0], self.community_buses[name][1], networkCnt, selectionCnt))
            self.community_networks[id].doGeneration(generationCnt)
            bestNetwork = self.community_networks[id].bestNetwork[0]
            saveImg(createNetworkX(bestNetwork), self.resultPath, f'{name} - {bestNetwork.score} - {generationCnt}')
            saveNetwork(bestNetwork, self.resultPath, f'{name} - {bestNetwork.score}')

    def merge_network(self, networkCnt, selectionCnt, generationCnt):
        routeList = []
        stopList = []
        for community in self.community_networks:
            routeList = routeList + community.bestNetwork[0].busData.routeList
            for route in community.bestNetwork[0].busData.routeList:
                print(route.id, route.stopIdList)
            # stopList = stopList + community.bestNetwork[0].busData.stopList

        self.total_genetic = Genetic('./data/stopData_parsed.csv', './data/population.csv', [0], self.maxBuscnt, networkCnt, selectionCnt)

        for bestnetwork in self.total_genetic.bestNetwork:
            bestnetwork.busData.routeList = routeList
        
        for i in range(generationCnt):
            self.total_genetic.doGeneration(1)
            bestNetwork = self.total_genetic.bestNetwork[0]
            saveImg(createNetworkX(bestNetwork), self.resultPath, f'나주시 {i+1} - {bestNetwork.score}')
            saveNetwork(bestNetwork, self.resultPath, f'나주시 {i+1} - {bestNetwork.score}')
            
            
if __name__ == '__main__':
    community_Network = Community_Network('./data/population.csv', 51, 155, 10, 2, 10)

    community_Network.merge_network(10, 2, 20)