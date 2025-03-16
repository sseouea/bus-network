import csv
from busNetwork import BusNetwork
from genetic import Genetic
from busData import BusRoute, BusData
import resultProcessing

genetic = Genetic('./data/stopData_parsed.csv', './data/population.csv', [0], 1, 10, 2)

# with open('./Results/37/나주시 40 - 0.02013305229321533.csv', encoding='utf-8') as f:
with open('./data/routeData_parsed.csv', encoding='utf-8') as f:
    r = csv.reader(f)
    genetic.bestNetwork[0].busData.routeList = []
    genetic.bestNetwork[1].busData.routeList = []
    for i, line in enumerate(r):
        if line[0] == 'id':
            continue
        # if i == 5:
        genetic.bestNetwork[0].busData.routeList.append(BusRoute(f'{line[0]}-0', line[1], line[2], line[3].split('/')))
        genetic.bestNetwork[1].busData.routeList.append(BusRoute(f'{line[0]}-0', line[1], line[2], line[3].split('/')))

# edgeCnt = 0
# for route in busNetwork.busData.routeList:
#     edgeCnt += len(route.stopIdList)-1
# print(edgeCnt)


genetic.bestNetwork[0].evaluate()

# resultPath = resultProcessing.makeResultPath()
# for i in range(100):
#     genetic.doGeneration(1)
#     network = resultProcessing.createNetworkX(genetic.bestNetwork[0])
#     resultProcessing.saveImg(network, resultPath, f'Random {i} - {genetic.bestNetwork[0].score}')
#     resultProcessing.saveNetwork(genetic.bestNetwork[0], resultPath, f'Random {i} - {genetic.bestNetwork[0].score}')

# resultProcessing.saveImg(resultProcessing.createNetworkX(genetic.bestNetwork[0]), './Results/real/', 'Real Network_curved')
