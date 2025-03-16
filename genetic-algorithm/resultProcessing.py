from PIL import Image
import csv
import os
import networkx as nx
import matplotlib.pyplot as plt

def show_video(folder_idx):
    cur_directory = os.getcwd()
    save_directory = os.path.join(cur_directory, 'Results/' + str(folder_idx))
    print(os.listdir(save_directory))
    image_list = sorted(os.listdir(save_directory), key = lambda name : int(name.split(' ')[-1].split('.')[0]))

    images = [Image.open(os.path.join(save_directory, image_path)) for image_path in image_list]
    img = images[0]
    img.save(fp = save_directory + "/network.gif", format = "GIF", append_images = images[1:], save_all = True, duration = 300, loop = 0, disposal = 2)

def makeResultPath():
        cur_directory = os.getcwd()
        save_directory = os.path.join(cur_directory, 'Results')
        folder_count = len([item for item in os.listdir(save_directory) if os.path.isdir(os.path.join(save_directory, item))])
        idx = str(folder_count)
        os.makedirs(save_directory + '/' + idx)
        return save_directory + '/' + idx + '/'


def getRouteListFromStop(busNetwork, stopId): # node을 지나는 버스 반환
    routeIdList = []
    for route in busNetwork.busData.routeList:
        for i in range(len(route.stopIdList)):
            if route.stopIdList[i] == stopId:
                routeIdList.append(route.id)
    return routeIdList 

def createNetworkX(busNetwork):
    network = nx.DiGraph()

    network.add_nodes_from(list(map(lambda stop: stop.id, busNetwork.busData.stopList)))

    nodeAttributeDict = {
        stop.id : {
            'name' : stop.name,
            'latitude' : stop.latitude,
            'longitude' : stop.longitude,
            'region': stop.region,
            'passed': getRouteListFromStop(busNetwork, stop.id)
        } for stop in busNetwork.busData.stopList
    }
    nx.set_node_attributes(network, nodeAttributeDict)

    edgeAttributeDict = {}
    newEdgeList = []

    for route in busNetwork.busData.routeList:
        for i in range(len(route.stopIdList)-1):
            edge = (route.stopIdList[i], route.stopIdList[i+1])
            # if not genetic.network.has_edge(*edge):
            #     newEdgeList.append(edge)
            newEdgeList.append(edge)
            edgeAttributeDict[edge] = { "routeId": route.id }
    network.add_edges_from(newEdgeList)

    nx.set_edge_attributes(network, edgeAttributeDict)

    return network

def saveImg(network, resultPath, title = ''):

    plt.figure(figsize=(25,20), facecolor='white')
    plt.tight_layout()
    plt.rc('font', family='HYHeadLine-Medium') # For Windows

    ax = plt.gca()
    ax.set_facecolor("white")

    #pos = nx.spring_layout(genetic.network) # layout 조정 가능
    #pos = nx.kamada_kawai_layout(genetic.network)
    #pos = nx.random_layout(genetic.network)

    pos = {node[0] : [node[1]['longitude'], node[1]['latitude']] for node in list(network.nodes(data=True))}

    nodes = list(network.nodes(data = True))
    edges = list(network.edges(data = True))

    colorList = ['red','orange','green', 'skyblue',  'lightpink', 'purple',  'brown','black']

    # node_colors = [colorList[int(node[1]['passed'][0].split('-')[0])%8] if len(node[1]['passed']) != 0 else 'grey' for node in nodes]
    node_colors = 'grey'
    edge_colors = [colorList[int(edge[2]['routeId'].split('-')[0])%8] for edge in edges]

    nx.draw_networkx_nodes(network, node_size = 40, node_color = node_colors, alpha = 0.5, pos = pos, ax = ax)
    # nx.draw_networkx_labels(network, pos=pos, font_size=8)
    # nx.draw_networkx_edges(network, width = 2, edge_color = edge_colors, alpha = 1, pos = pos, ax = ax, connectionstyle="arc3,rad=0.1")
    nx.draw_networkx_edges(network, width = 2, edge_color = edge_colors, alpha = 1, pos = pos, ax = ax)

    # nx.draw_networkx_nodes(network, node_size = 40, node_color = 'grey', alpha = 0.3, pos = pos, ax = ax)
    # nx.draw_networkx_edges(network, width = 2, edge_color = 'red', alpha = 0.7, pos = pos, ax = ax)

    ax.set_title(title, fontsize = 32)

    # image 저장
    plt.savefig(resultPath + title + '.png', dpi = 200)

    plt.close()

def saveNetwork(busNetwork, resultPath, title):
    with open(f'{resultPath}{title}.csv', '+w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['id', 'name', 'busCnt', 'stopIdArr'])
        for route in busNetwork.busData.routeList:
            w.writerow([route.id, route.name, route.cnt, '/'.join(map(str, route.stopIdList))])
