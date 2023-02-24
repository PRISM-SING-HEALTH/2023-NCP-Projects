'''
/*******************************************************************
 *  File Name: imageAnalysisExtraction.py                          *
 *  Purpose: Uses image analysis to extract relationships          *
 *  Author: Marcus Francis Cozza - 20595722@student.curtin.edu.au  *
 *  Date: 30/01/2023                                               *
 *  Version: 1.1                                                   *
 *  Change Log:                                                    *
 *      > 1.1 - Initialise Program 30/01/2023                      *
 *******************************************************************/
 '''
import json
import sys
import networkx as nx
from matplotlib import pyplot as plt

from Classes.PEDClass import PED
from Helper.HelperFunctions import *
from HoughLines import *
from ObjectDetection.RoboFlowAPI import getPredictions

# initialise arrays
symbolObjectArray = []
lineCords = []
shortestCords = []
PEDArray = []

# set file names
pedFilename = "test.ped"
imageFilename = "3.png"

extractLineFileName = "RemovedSymbols.png"

# initialise graph
G = nx.Graph()


def main(readImageFilename, writePEDFilename, isAdvance):
    resultJson = getPredictions(imageFilename)
    print(resultJson)

    # 1.png
    #resultJson = '{"predictions": [{"x": 1207.5, "y": 172.5, "width": 123.0, "height": 109.0, "confidence": 0.9093862771987915, "class": "Affected - Decreased Male", "image_path": "1.png", "prediction_type": "ObjectDetectionModel"}, {"x": 971.0, "y": 171.5, "width": 132.0, "height": 109.0, "confidence": 0.8745255470275879, "class": "Affected - Decreased Female", "image_path": "1.png", "prediction_type": "ObjectDetectionModel"}, {"x": 594.5, "y": 583.0, "width": 125.0, "height": 102.0, "confidence": 0.8732601404190063, "class": "Affected Female", "image_path": "1.png", "prediction_type": "ObjectDetectionModel"}, {"x": 1349.5, "y": 584.0, "width": 117.0, "height": 92.0, "confidence": 0.8691983222961426, "class": "Affected Female", "image_path": "1.png", "prediction_type": "ObjectDetectionModel"}, {"x": 1493.0, "y": 171.5, "width": 112.0, "height": 93.0, "confidence": 0.8616546988487244, "class": "Affected Female", "image_path": "1.png", "prediction_type": "ObjectDetectionModel"}, {"x": 1087.5, "y": 998.5, "width": 125.0, "height": 91.0, "confidence": 0.8568559885025024, "class": "Affected Female", "image_path": "1.png", "prediction_type": "ObjectDetectionModel"}, {"x": 756.0, "y": 998.5, "width": 104.0, "height": 77.0, "confidence": 0.8531278371810913, "class": "Male", "image_path": "1.png", "prediction_type": "ObjectDetectionModel"}, {"x": 824.0, "y": 583.0, "width": 106.0, "height": 92.0, "confidence": 0.8529415130615234, "class": "Male", "image_path": "1.png", "prediction_type": "ObjectDetectionModel"}, {"x": 682.5, "y": 173.0, "width": 103.0, "height": 84.0, "confidence": 0.8474584817886353, "class": "Affected Male", "image_path": "1.png", "prediction_type": "ObjectDetectionModel"}, {"x": 1577.5, "y": 582.5, "width": 109.0, "height": 91.0, "confidence": 0.8442121744155884, "class": "Female", "image_path": "1.png", "prediction_type": "ObjectDetectionModel"}, {"x": 368.5, "y": 581.5, "width": 139.0, "height": 103.0, "confidence": 0.8157013654708862, "class": "Female", "image_path": "1.png", "prediction_type": "ObjectDetectionModel"}, {"x": 136.5, "y": 581.5, "width": 111.0, "height": 95.0, "confidence": 0.8137791156768799, "class": "Male", "image_path": "1.png", "prediction_type": "ObjectDetectionModel"}, {"x": 1088.0, "y": 997.5, "width": 120.0, "height": 85.0, "confidence": 0.7238418459892273, "class": "Consultand Female", "image_path": "1.png", "prediction_type": "ObjectDetectionModel"}], "image": {"width": "1868", "height": "1160"}}'

    # 2.png
    #resultJson = '{"predictions": [{"x": 385.5, "y": 87.5, "width": 107.0, "height": 97.0, "confidence": 0.9241393804550171, "class": "Deceased Female", "image_path": "2.png", "prediction_type": "Objec tDetectionModel"}, {"x": 139.5, "y": 87.0, "width": 113.0, "height": 98.0, "confidence": 0.9031888246536255, "class": "Deceased Male", "image_path": "2.png", "prediction_type": "Objec tDetectionModel"}, {"x": 846.0, "y": 89.5, "width": 118.0, "height": 97.0, "confidence": 0.8956431746482849, "class": "Affected - Decreased Female", "image_path": "2.png", "prediction _type": "ObjectDetectionModel"}, {"x": 489.0, "y": 808.5, "width": 102.0, "height": 81.0, "confidence": 0.8696268200874329, "class": "Consultand Female", "image_path": "2.png", "predi ction_type": "ObjectDetectionModel"}, {"x": 720.0, "y": 448.5, "width": 104.0, "height": 81.0, "confidence": 0.8696115016937256, "class": "Affected Female", "image_path": "2.png", "pr ediction_type": "ObjectDetectionModel"}, {"x": 594.0, "y": 87.0, "width": 92.0, "height": 76.0, "confidence": 0.8544217348098755, "class": "Affected Male", "image_path": "2.png", "pre diction_type": "ObjectDetectionModel"}, {"x": 256.5, "y": 445.5, "width": 97.0, "height": 81.0, "confidence": 0.8438169956207275, "class": "Male", "image_path": "2.png", "prediction_t ype": "ObjectDetectionModel"}, {"x": 198.5, "y": 809.0, "width": 89.0, "height": 74.0, "confidence": 0.8379479646682739, "class": "Male", "image_path": "2.png", "prediction_type": "Ob jectDetectionModel"}, {"x": 778.5, "y": 809.5, "width": 99.0, "height": 77.0, "confidence": 0.8379451632499695, "class": "Female", "image_path": "2.png", "prediction_type": "ObjectDet ectionModel"}], "image": {"width": "1036", "height": "928"}}'

    # 3.png
    #resultJson = '{"predictions": [{"x": 595.0, "y": 75.0, "width": 78.0, "height": 72.0, "confidence": 0.9082944989204407, "class": "Deceased Male", "image_path": "3.png", "prediction_type": "ObjectDetectionModel"}, {"x": 510.0, "y": 640.5, "width": 76.0, "height": 63.0, "confidence": 0.8999674916267395, "class": "Consultand Female", "image_path": "3.png", "prediction_type": "ObjectDetectionModel"}, {"x": 235.0, "y": 74.0, "width": 78.0, "height": 68.0, "confidence": 0.8926987648010254, "class": "Deceased Male", "image_path": "3.png", "prediction_type": "ObjectDetectionModel"}, {"x": 788.0, "y": 74.5, "width": 78.0, "height": 71.0, "confidence": 0.8883305788040161, "class": "Deceased Female", "image_path": "3.png", "prediction_type": "ObjectDetectionModel"}, {"x": 176.0, "y": 358.0, "width": 84.0, "height": 68.0, "confidence": 0.8839989900588989, "class": "Deceased Male", "image_path": "3.png", "prediction_type": "ObjectDetectionModel"}, {"x": 689.5, "y": 358.0, "width": 79.0, "height": 60.0, "confidence": 0.8754889965057373, "class": "Female", "image_path": "3.png", "prediction_type": "ObjectDetectionModel"}, {"x": 428.5, "y": 74.5, "width": 81.0, "height": 73.0, "confidence": 0.8754005432128906, "class": "Deceased Female", "image_path": "3.png", "prediction_type": "ObjectDetectionModel"}, {"x": 587.5, "y": 939.0, "width": 71.0, "height": 54.0, "confidence": 0.8728984594345093, "class": "Male", "image_path": "3.png", "prediction_type": "ObjectDetectionModel"}, {"x": 737.5, "y": 642.0, "width": 81.0, "height": 62.0, "confidence": 0.8720635175704956, "class": "Female", "image_path": "3.png", "prediction_type": "ObjectDetectionModel"}, {"x": 431.5, "y": 939.0, "width": 75.0, "height": 54.0, "confidence": 0.8677240610122681, "class": "Male", "image_path": "3.png", "prediction_type": "ObjectDetectionModel"}, {"x": 846.0, "y": 356.0, "width": 84.0, "height": 66.0, "confidence": 0.867713451385498, "class": "Female", "image_path": "3.png", "prediction_type": "ObjectDetectionModel"}, {"x": 282.5, "y": 640.0, "width": 71.0, "height": 60.0, "confidence": 0.8641939163208008, "class": "Male", "image_path": "3.png", "prediction_type": "ObjectDetectionModel"}, {"x": 330.0, "y": 357.0, "width": 68.0, "height": 60.0, "confidence": 0.8506650924682617, "class": "Affected Male", "image_path": "3.png", "prediction_type": "ObjectDetectionModel"}], "image": {"width": "1008", "height": "1060"}}'

    # 4.png
    #resultJson = '{"predictions": [{"x": 361.5, "y": 91.0, "width": 99.0, "height": 86.0, "confidence": 0.920861005783081, "class": "Deceased Female", "image_path": "4.png", "prediction_type": "ObjectDetectionModel"}, {"x": 548.0, "y": 90.5, "width": 96.0, "height": 87.0, "confidence": 0.9036645889282227, "class": "Deceased Male", "image_path": "4.png", "prediction_type": "ObjectDetectionModel"}, {"x": 137.5, "y": 90.0, "width": 101.0, "height": 86.0, "confidence": 0.9022492170333862, "class": "Deceased Male", "image_path": "4.png", "prediction_type": "ObjectDetectionModel"}, {"x": 659.5, "y": 411.5, "width": 101.0, "height": 83.0, "confidence": 0.8901426792144775, "class": "Female", "image_path": "4.png", "prediction_type": "ObjectDetectionModel"}, {"x": 774.5, "y": 90.5, "width": 111.0, "height": 87.0, "confidence": 0.8847164511680603, "class": "Affected - Decreased Female", "image_path": "4.png", "prediction_type": "ObjectDetectionModel"}, {"x": 188.5, "y": 736.5, "width": 89.0, "height": 73.0, "confidence": 0.8641092777252197, "class": "Male", "image_path": "4.png", "prediction_type": "ObjectDetectionModel"}, {"x": 243.5, "y": 410.0, "width": 95.0, "height": 82.0, "confidence": 0.8576736450195312, "class": "Male", "image_path": "4.png", "prediction_type": "ObjectDetectionModel"}, {"x": 454.0, "y": 739.5, "width": 98.0, "height": 73.0, "confidence": 0.8574193120002747, "class": "Consultand Female", "image_path": "4.png", "prediction_type": "ObjectDetectionModel"}, {"x": 710.0, "y": 737.5, "width": 96.0, "height": 79.0, "confidence": 0.8570454120635986, "class": "Female", "image_path": "4.png", "prediction_type": "ObjectDetectionModel"}, {"x": 244.5, "y": 412.0, "width": 97.0, "height": 82.0, "confidence": 0.7917690277099609, "class": "Affected Male", "image_path": "4.png", "prediction_type": "ObjectDetectionModel"}], "image": {"width": "916", "height": "856"}}'

    # 5.png
    #resultJson = '{"predictions": [{"x": 1450.0, "y": 431.0, "width": 80.0, "height": 64.0, "confidence": 0.9222506284713745, "class": "Affected Female", "image_path": "5.png", "prediction_type": "ObjectDetectionModel"}, {"x": 781.5, "y": 722.5, "width": 83.0, "height": 67.0, "confidence": 0.9149703979492188, "class": "Consultand Female", "image_path": "5.png", "prediction_type": "ObjectDetectionModel"}, {"x": 1065.5, "y": 140.5, "width": 81.0, "height": 71.0, "confidence": 0.9018796682357788, "class": "Female", "image_path": "5.png", "prediction_type": "ObjectDetectionModel"}, {"x": 865.5, "y": 144.5, "width": 89.0, "height": 75.0, "confidence": 0.9014055728912354, "class": "Deceased Male", "image_path": "5.png", "prediction_type": "ObjectDetectionModel"}, {"x": 964.0, "y": 429.0, "width": 80.0, "height": 62.0, "confidence": 0.8946155905723572, "class": "Affected Female", "image_path": "5.png", "prediction_type": "ObjectDetectionModel"}, {"x": 1012.5, "y": 724.0, "width": 77.0, "height": 64.0, "confidence": 0.8921630382537842, "class": "Female", "image_path": "5.png", "prediction_type": "ObjectDetectionModel"}, {"x": 696.5, "y": 144.5, "width": 83.0, "height": 73.0, "confidence": 0.8915976285934448, "class": "Deceased Female", "image_path": "5.png", "prediction_type": "ObjectDetectionModel"}, {"x": 1288.0, "y": 433.5, "width": 84.0, "height": 65.0, "confidence": 0.8850415945053101, "class": "Female", "image_path": "5.png", "prediction_type": "ObjectDetectionModel"}, {"x": 1609.5, "y": 432.0, "width": 83.0, "height": 66.0, "confidence": 0.882286787033081, "class": "Female", "image_path": "5.png", "prediction_type": "ObjectDetectionModel"}, {"x": 272.5, "y": 432.0, "width": 79.0, "height": 68.0, "confidence": 0.8818713426589966, "class": "Male", "image_path": "5.png", "prediction_type": "ObjectDetectionModel"}, {"x": 495.0, "y": 143.5, "width": 74.0, "height": 65.0, "confidence": 0.8787811994552612, "class": "Affected Male", "image_path": "5.png", "prediction_type": "ObjectDetectionModel"}, {"x": 1933.0, "y": 432.5, "width": 72.0, "height": 65.0, "confidence": 0.8732598423957825, "class": "Male", "image_path": "5.png", "prediction_type": "ObjectDetectionModel"}, {"x": 433.0, "y": 432.5, "width": 78.0, "height": 67.0, "confidence": 0.8588083982467651, "class": "Male", "image_path": "5.png", "prediction_type": "ObjectDetectionModel"}, {"x": 2092.5, "y": 432.0, "width": 69.0, "height": 64.0, "confidence": 0.8581544160842896, "class": "Male", "image_path": "5.png", "prediction_type": "ObjectDetectionModel"}, {"x": 546.0, "y": 723.0, "width": 76.0, "height": 66.0, "confidence": 0.8571099638938904, "class": "Male", "image_path": "5.png", "prediction_type": "ObjectDetectionModel"}, {"x": 109.5, "y": 432.5, "width": 75.0, "height": 67.0, "confidence": 0.8566229939460754, "class": "Male", "image_path": "5.png", "prediction_type": "ObjectDetectionModel"}, {"x": 1770.5, "y": 434.0, "width": 87.0, "height": 66.0, "confidence": 0.8438470363616943, "class": "Affected Female", "image_path": "5.png", "prediction_type": "ObjectDetectionModel"}, {"x": 1127.0, "y": 430.0, "width": 84.0, "height": 72.0, "confidence": 0.8309265375137329, "class": "Affected Female", "image_path": "5.png", "prediction_type": "ObjectDetectionModel"}, {"x": 594.0, "y": 432.0, "width": 74.0, "height": 60.0, "confidence": 0.8062177896499634, "class": "Affected Male", "image_path": "5.png", "prediction_type": "ObjectDetectionModel"}], "image": {"width": "2250", "height": "930"}}'

    #resultJson = json.loads(resultJson)

    removeSymbolsFromImage(imageFilename, extractLineFileName, resultJson)

    # calculate straight line points from a file and get the points and reference to the image created and the source.
    linesP, cdstP, src = getPointsFromHoughLines(extractLineFileName)

    # TODO: move out later
    for i in resultJson["predictions"]:
        symbolClass = Symbol(i["x"], i["y"], i["confidence"], i["class"])
        symbolObjectArray.append(symbolClass)

    ''' Line Extraction ---------------------------------------------------------------------------------------'''
    # convert points into array of cords
    for i in range(0, len(linesP)):
        l = linesP[i][0]
        lineCords.append(cord(l[0], l[1], l[2], l[3]))

    # add nodes and points to graph
    for j in lineCords:
        G.add_node(point(j.x1, j.x2).__str__(), weight=0)
        G.add_node(point(j.y1, j.y2).__str__(), weight=0)

        G.add_edge(point(j.x1, j.x2).__str__(), point(j.y1, j.y2).__str__(), weight=1)

    cv.imwrite("ExtractNoLines.png", cdstP)

    # find the shortest distance
    for i in G.nodes:
        shortDistance = sys.maxsize
        counter = 0
        savedPos1 = point(0, 0)
        savedPos2 = point(0, 0)

        for k in symbolObjectArray:
            pointI = convertStringToPoint(i)
            distance = math.dist([pointI.x, pointI.y], [k.xPos, k.yPos])

            if shortDistance > distance:
                shortDistance = distance
                savedPos1.x = k.xPos
                savedPos1.y = k.yPos

                savedPos2.x = pointI.x
                savedPos2.y = pointI.y

            if counter == len(symbolObjectArray) - 1:
                cv.line(cdstP, (int(savedPos1.x), int(savedPos1.y)), (int(savedPos2.x), int(savedPos2.y)),
                        (0, 255, 255),
                        3, cv.LINE_AA)
                shortestCords.append(cord(savedPos1.x, savedPos1.y, savedPos2.x, savedPos2.y))

            counter += 1
    cv.imwrite("ExtractSymbolLine.png", cdstP)

    for k in symbolObjectArray:
        G.add_node(point(k.xPos, k.yPos).__str__(), weight=1)

    for i in shortestCords:
        G.add_edge(point(i.x1, i.x2).__str__(), point(i.y1, i.y2).__str__(), weight=2)

    sub_graphs = (G.subgraph(c) for c in nx.connected_components(G))

    maxNodeSubGraph = 0
    subGraphNodes = 0
    maxNodeIndex = 0
    for i, sg in enumerate(sub_graphs):
        if (sg.number_of_nodes() > maxNodeSubGraph):
            maxNodeSubGraph = sg.number_of_nodes()
            subGraphNodes = sg.nodes(data=True)
            maxNodeIndex = i

    sub_graphs = (G.subgraph(c) for c in nx.connected_components(G))

    for i, sg in enumerate(sub_graphs):
        if (maxNodeIndex == i):
            pass
        else:
            currentShortestDistance = sys.maxsize
            currentShortestCord = cord(0, 0, 0, 0)

            for j in sg.nodes():
                for k in subGraphNodes:
                    pointI = convertStringToPoint(j)
                    pointK = convertStringToPoint(k[0])
                    distance = math.dist([pointI.x, pointI.y], [pointK.x, pointK.y])

                    if distance < currentShortestDistance:
                        currentShortestDistance = distance
                        currentShortestCord = cord(pointI.x, pointI.y, pointK.x, pointK.y)
            G.add_edge(point(currentShortestCord.x1, currentShortestCord.x2).__str__(), point(currentShortestCord.y1, currentShortestCord.y2).__str__(), weight=1)

    for i in symbolObjectArray:
        currentPaths = []
        currentShortestPath = sys.maxsize
        for k in shortestCords:
            # remove same paths
            if not (i == k):
                try:
                    # get all paths
                    path = nx.shortest_path(G, source=convertPointToString(i.xPos, i.yPos),
                                            target=convertPointToString(k.x1, k.x2), weight="weight")

                    # remove path that go to its self
                    if len(path) != 1:
                        # remove paths from the same level
                        if abs(convertStringToPoint(path[0]).y - convertStringToPoint(path[len(path) - 1]).y) > 5:
                            # back sure the connected are not form high to low
                            if convertStringToPoint(path[len(path) - 1]).y < convertStringToPoint(path[0]).y:
                                # make sure they are not the same value
                                if not (convertStringToPoint(path[len(path) - 1]).y == convertStringToPoint(path[0]).y):
                                    # check that we only have the shortest paths
                                    if len(path) <= currentShortestPath:
                                        currentPaths.append(path)
                                        currentShortestPath = len(path)

                except nx.NetworkXNoPath:
                    pass

        pathFromSymbolToSymbol = []
        # get all paths
        [pathFromSymbolToSymbol.append(x) for x in currentPaths if x not in pathFromSymbolToSymbol]

        # paths are in order, so we find the two shortest ones which are our relationships
        if len(pathFromSymbolToSymbol) == 0:
            pass
        elif len(pathFromSymbolToSymbol) <= 2:
            pointStart = convertStringToPoint(pathFromSymbolToSymbol[0][0])
            pointEnd1 = convertStringToPoint(pathFromSymbolToSymbol[len(pathFromSymbolToSymbol) - 1][-1])
            pointEnd2 = convertStringToPoint(pathFromSymbolToSymbol[len(pathFromSymbolToSymbol) - 2][-1])

            # Male
            if pointEnd1.x < pointEnd2.x:
                PEDArray.append(
                    PED("FAMID", str(pointStart .x) + "-" + str(pointStart.y), str(pointEnd1.x) + "-" + str(pointEnd1.y),
                        str(pointEnd2.x) + "-" + str(pointEnd2.y), 1, 0))
            else:
                PEDArray.append(
                    PED("FAMID", str(pointStart.x) + "-" + str(pointStart.y), str(pointEnd2.x) + "-" + str(pointEnd2.y),
                        str(pointEnd1.x) + "-" + str(pointEnd1.y), 0, 0))
            cv.line(cdstP, (pointStart.x, pointStart.y), (pointEnd1.x, pointEnd1.y), (100, 200, 100), 3, cv.LINE_AA)
            cv.line(cdstP, (pointStart.x, pointStart.y), (pointEnd2.x, pointEnd2.y), (100, 200, 100), 3, cv.LINE_AA)

    symbolObjectArray.sort(key=lambda x: x.yPos)
    for i in symbolObjectArray:
        counter = 0
        for k in PEDArray:
            currentNodePoint = convertSymbolToPoint(k.individualID)
            if currentNodePoint.x == int(i.xPos) and currentNodePoint.y == int(i.yPos):
                PEDArray[counter].sex = convertClassToSex(i.modelClass)
                PEDArray[counter].phenotype = convertClassToAffected(i.modelClass)

            counter += 1

    currentHighest = symbolObjectArray[0].yPos

    for i in symbolObjectArray:
        if abs(i.yPos - currentHighest) <= 5:
            currentHighest = i.yPos
            PEDArray.insert(0, PED("FAMID", str(int(i.xPos)) + "-" + str(int(i.yPos)), 0,
                                   0, convertClassToSex(i.modelClass), convertClassToAffected(i.modelClass)))
    ''' END Line Extraction ---------------------------------------------------------------------------------------'''

    # Put results in PED
    convertPEDArrToFile(PEDArray, pedFilename)

    ''' Display Graph ---------------------------------------------------------------------------------------'''
    nodes, nodeWeights = zip(*nx.get_node_attributes(G, 'weight').items())

    edges, edgeWeights = zip(*nx.get_edge_attributes(G, 'weight').items())

    # Show graph
    pos = nx.spring_layout(G, scale=10)
    nx.draw(G, pos, node_color=nodeWeights, edge_color=edgeWeights, with_labels=True)
    plt.show()

    ''' END Display Graph ---------------------------------------------------------------------------------------'''

    ''' Draw Lines On Image ---------------------------------------------------------------------------------------'''
    for k in symbolObjectArray:
        cv.putText(cdstP, str(k.xPos) + " " + str(k.yPos), (int(k.xPos), int(k.yPos)), cv.FONT_HERSHEY_SIMPLEX, 0.7,
                   (255, 255, 0), 1,
                   cv.LINE_AA)

    if linesP is not None:
        for i in lineCords:
            cv.line(cdstP, (i.x1, i.x2), (i.y1, i.y2), (0, 0, 255), 3, cv.LINE_AA)

            # more top cords
            cv.putText(cdstP, str(i.x1) + " " + str(i.x2), (i.x1, i.x2), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 1,
                       cv.LINE_AA)

            # more bottom cords
            cv.putText(cdstP, str(i.y1) + " " + str(i.y2), (i.y1, i.y2), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 1,
                       cv.LINE_AA)

    # DISPLAY IMAGES
    # cv.namedWindow("Lines Extraction View", cv.WINDOW_NORMAL)
    # cv.namedWindow("Source", cv.WINDOW_NORMAL)
    # cv.imshow("Source", src)
    # cv.imshow("Lines Extraction View", cdstP)
    # cv.waitKey()

    # Saved lines to file

    cv.imwrite("ExtractLines.png", cdstP)
    if (isAdvance == True):


        PEDArray.clear()
        draw_line_widget = DrawLineWidget("ExtractLines.png", symbolObjectArray, "ExtractNoLines.png")
        while True:
            cv.imshow('image', draw_line_widget.show_image())
            key = cv.waitKey(1)

            if key == ord('q'):
                cv.destroyAllWindows()
                break

        objectSymbolArray = draw_line_widget.getSymbolArray()
        objectSymbolArray.sort(key=lambda x: x.x2)
        for i in range(0, len(objectSymbolArray), 2):
            if (objectSymbolArray[i].y1 < objectSymbolArray[i + 1].y1):
                PEDArray.append(
                    PED("FAMID", str(objectSymbolArray[i].x1) + "-" + str(objectSymbolArray[i].x2),
                        str(objectSymbolArray[i].y1) + "-" + str(objectSymbolArray[i].y2),
                        str(objectSymbolArray[i + 1].y1) + "-" + str(objectSymbolArray[i + 1].y2), 1, 0))
            else:
                PEDArray.append(
                    PED("FAMID", str(objectSymbolArray[i].x1) + "-" + str(objectSymbolArray[i].x2),
                        str(objectSymbolArray[i + 1].y1) + "-" + str(objectSymbolArray[i + 1].y2),
                        str(objectSymbolArray[i].y1) + "-" + str(objectSymbolArray[i].y2), 1, 0))
        for i in symbolObjectArray:
            counter = 0
            for k in PEDArray:
                currentNodePoint = convertSymbolToPoint(k.individualID)


main(imageFilename, pedFilename, False)
