from busNetwork import BusNetwork 
from busData import BusData
import copy
import time
import multiprocessing as mp
import resultProcessing

class Timer:
    def __init__(self):
        self.t = time.time()
    def printDelta(self, title=''):
        print(f'{title}: {time.time() - self.t}')
        self.t = time.time()

class Genetic:

    @staticmethod
    def copyNetwork(network, copyCnt):
        # networkList = []
        # for _ in range(copyCnt):
        #     busNetwork = BusNetwork([0], 1)
        #     busNetwork.busData.routeList = network.busData.routeList
        #     networkList.append(busNetwork)
        # return networkList
        return [copy.deepcopy(network) for _ in range(copyCnt)]

    def __init__(self, stopDataFileName, communityDataFileName, routeIdList, maxBusCnt, networkCnt = 40, selectionCnt=4): 


        BusData.initStopData(stopDataFileName)
        BusData.initCommunityData(communityDataFileName)
        BusData.initDistanceMatrix()

        self.selectionCnt = selectionCnt
        self.networkCnt = networkCnt 

        self.bestNetwork = [BusNetwork(routeIdList, maxBusCnt) for _ in range(self.selectionCnt)]

    def replace(self):
        self.networkList = []
        for i in range(self.selectionCnt):
            self.networkList += Genetic.copyNetwork(self.bestNetwork[i], self.networkCnt//self.selectionCnt)
    
    def selection(self):
        networkList = sorted(self.networkList, key = lambda network : network.score, reverse = True)
        # if self.bestNetwork[0].score < networkList[0].score:
        #     self.bestNetwork = networkList[:self.selectionCnt]
        self.bestNetwork = [networkList[0]]
    
    def doGeneration(self, generationCnt):

        self.timer = Timer()

        for i in range(generationCnt):
            print(f'======= Generation {i} ========')
            self.replace()
            for network in self.networkList:
                self.evolveNetwork(network)
            self.selection()
            # for route in self.bestNetwork[0].busData.routeList:
            #     print(route.id, route.stopIdList)
            # self.network = resultProcessing.createNetworkX(self.bestNetwork[0])
            # resultProcessing.saveImg(self.network, self.resultPath, f'Basic {i} - {self.bestNetwork[0].score}')
            self.timer.printDelta('Done')
        
    
    @staticmethod
    def evolveNetwork(network):
        network.crossover()
        network.mutation()
        network.evaluate()

if __name__ == '__main__':

    # Test Code
    resultPath = resultProcessing.makeResultPath()
    genetic = Genetic(stopDataFileName='./data/stopData_parsed.csv', communityDataFileName='./data/population.csv', routeIdList=list(map(lambda x: f'{x}-0', range(51))), maxBusCnt=155, networkCnt=1, selectionCnt=1)
    for i in range(30):
        genetic.doGeneration(1)
        network = resultProcessing.createNetworkX(genetic.bestNetwork[0])
        resultProcessing.saveImg(network, resultPath, f'Random {i+1} - {genetic.bestNetwork[0].score}')
        resultProcessing.saveNetwork(genetic.bestNetwork[0], resultPath, f'Random {i+1} - {genetic.bestNetwork[0].score}')

