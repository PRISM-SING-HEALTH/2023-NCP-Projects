'''
/**************************************************************************
 *  File Name: OCRExtraction.py                                           *
 *  Purpose: Uses OCR to extract relationships                            *
 *  Author: Marcus Francis Cozza - 20595722@student.curtin.edu.au         *
 *  Date: 30/01/2023                                                      *
 *  Version: 1.1                                                          *
 *  Change Log:                                                           *
 *      > 1.1 - Initialise Program 30/01/2023                             *
 **************************************************************************/
 '''
import glob
import json
import math
import operator
import os
import sys
import networkx as nx
from matplotlib import pyplot as plt

from Classes.PEDClass import PED
from Helper.HelperFunctions import *
from HoughLines import *
from ObjectDetection.RoboFlowAPI import getPredictions
from pytesseract import pytesseract

# initialise arrays
symbolObjectArray = []
lineCords = []
shortestCords = []
PEDArray = []

# set file names
pedFilename = "test.ped"
imageFilename = "5.png"

extractLineFileName = "RemovedSymbols.png"

path_to_tesseract = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def main2(readImageFilename, writePEDFilename):
    # resultJson = getPredictions(imageFilename)

    # 1.png
    #resultJson = '{"predictions": [{"x": 1207.5, "y": 172.5, "width": 123.0, "height": 109.0, "confidence": 0.9093862771987915, "class": "Affected - Decreased Male", "image_path": "1.png", "prediction_type": "ObjectDetectionModel"}, {"x": 971.0, "y": 171.5, "width": 132.0, "height": 109.0, "confidence": 0.8745255470275879, "class": "Affected - Decreased Female", "image_path": "1.png", "prediction_type": "ObjectDetectionModel"}, {"x": 594.5, "y": 583.0, "width": 125.0, "height": 102.0, "confidence": 0.8732601404190063, "class": "Affected Female", "image_path": "1.png", "prediction_type": "ObjectDetectionModel"}, {"x": 1349.5, "y": 584.0, "width": 117.0, "height": 92.0, "confidence": 0.8691983222961426, "class": "Affected Female", "image_path": "1.png", "prediction_type": "ObjectDetectionModel"}, {"x": 1493.0, "y": 171.5, "width": 112.0, "height": 93.0, "confidence": 0.8616546988487244, "class": "Affected Female", "image_path": "1.png", "prediction_type": "ObjectDetectionModel"}, {"x": 1087.5, "y": 998.5, "width": 125.0, "height": 91.0, "confidence": 0.8568559885025024, "class": "Affected Female", "image_path": "1.png", "prediction_type": "ObjectDetectionModel"}, {"x": 756.0, "y": 998.5, "width": 104.0, "height": 77.0, "confidence": 0.8531278371810913, "class": "Male", "image_path": "1.png", "prediction_type": "ObjectDetectionModel"}, {"x": 824.0, "y": 583.0, "width": 106.0, "height": 92.0, "confidence": 0.8529415130615234, "class": "Male", "image_path": "1.png", "prediction_type": "ObjectDetectionModel"}, {"x": 682.5, "y": 173.0, "width": 103.0, "height": 84.0, "confidence": 0.8474584817886353, "class": "Affected Male", "image_path": "1.png", "prediction_type": "ObjectDetectionModel"}, {"x": 1577.5, "y": 582.5, "width": 109.0, "height": 91.0, "confidence": 0.8442121744155884, "class": "Female", "image_path": "1.png", "prediction_type": "ObjectDetectionModel"}, {"x": 368.5, "y": 581.5, "width": 139.0, "height": 103.0, "confidence": 0.8157013654708862, "class": "Female", "image_path": "1.png", "prediction_type": "ObjectDetectionModel"}, {"x": 136.5, "y": 581.5, "width": 111.0, "height": 95.0, "confidence": 0.8137791156768799, "class": "Male", "image_path": "1.png", "prediction_type": "ObjectDetectionModel"}, {"x": 1088.0, "y": 997.5, "width": 120.0, "height": 85.0, "confidence": 0.7238418459892273, "class": "Consultand Female", "image_path": "1.png", "prediction_type": "ObjectDetectionModel"}], "image": {"width": "1868", "height": "1160"}}'

    # 2.png
    #resultJson = '{"predictions": [{"x": 385.5, "y": 87.5, "width": 107.0, "height": 97.0, "confidence": 0.9241393804550171, "class": "Deceased Female", "image_path": "2.png", "prediction_type": "Objec tDetectionModel"}, {"x": 139.5, "y": 87.0, "width": 113.0, "height": 98.0, "confidence": 0.9031888246536255, "class": "Deceased Male", "image_path": "2.png", "prediction_type": "Objec tDetectionModel"}, {"x": 846.0, "y": 89.5, "width": 118.0, "height": 97.0, "confidence": 0.8956431746482849, "class": "Affected - Decreased Female", "image_path": "2.png", "prediction _type": "ObjectDetectionModel"}, {"x": 489.0, "y": 808.5, "width": 102.0, "height": 81.0, "confidence": 0.8696268200874329, "class": "Consultand Female", "image_path": "2.png", "predi ction_type": "ObjectDetectionModel"}, {"x": 720.0, "y": 448.5, "width": 104.0, "height": 81.0, "confidence": 0.8696115016937256, "class": "Affected Female", "image_path": "2.png", "pr ediction_type": "ObjectDetectionModel"}, {"x": 594.0, "y": 87.0, "width": 92.0, "height": 76.0, "confidence": 0.8544217348098755, "class": "Affected Male", "image_path": "2.png", "pre diction_type": "ObjectDetectionModel"}, {"x": 256.5, "y": 445.5, "width": 97.0, "height": 81.0, "confidence": 0.8438169956207275, "class": "Male", "image_path": "2.png", "prediction_t ype": "ObjectDetectionModel"}, {"x": 198.5, "y": 809.0, "width": 89.0, "height": 74.0, "confidence": 0.8379479646682739, "class": "Male", "image_path": "2.png", "prediction_type": "Ob jectDetectionModel"}, {"x": 778.5, "y": 809.5, "width": 99.0, "height": 77.0, "confidence": 0.8379451632499695, "class": "Female", "image_path": "2.png", "prediction_type": "ObjectDet ectionModel"}], "image": {"width": "1036", "height": "928"}}'

    # 3.png
    #resultJson = '{"predictions": [{"x": 595.0, "y": 75.0, "width": 78.0, "height": 72.0, "confidence": 0.9082944989204407, "class": "Deceased Male", "image_path": "3.png", "prediction_type": "ObjectDetectionModel"}, {"x": 510.0, "y": 640.5, "width": 76.0, "height": 63.0, "confidence": 0.8999674916267395, "class": "Consultand Female", "image_path": "3.png", "prediction_type": "ObjectDetectionModel"}, {"x": 235.0, "y": 74.0, "width": 78.0, "height": 68.0, "confidence": 0.8926987648010254, "class": "Deceased Male", "image_path": "3.png", "prediction_type": "ObjectDetectionModel"}, {"x": 788.0, "y": 74.5, "width": 78.0, "height": 71.0, "confidence": 0.8883305788040161, "class": "Deceased Female", "image_path": "3.png", "prediction_type": "ObjectDetectionModel"}, {"x": 176.0, "y": 358.0, "width": 84.0, "height": 68.0, "confidence": 0.8839989900588989, "class": "Deceased Male", "image_path": "3.png", "prediction_type": "ObjectDetectionModel"}, {"x": 689.5, "y": 358.0, "width": 79.0, "height": 60.0, "confidence": 0.8754889965057373, "class": "Female", "image_path": "3.png", "prediction_type": "ObjectDetectionModel"}, {"x": 428.5, "y": 74.5, "width": 81.0, "height": 73.0, "confidence": 0.8754005432128906, "class": "Deceased Female", "image_path": "3.png", "prediction_type": "ObjectDetectionModel"}, {"x": 587.5, "y": 939.0, "width": 71.0, "height": 54.0, "confidence": 0.8728984594345093, "class": "Male", "image_path": "3.png", "prediction_type": "ObjectDetectionModel"}, {"x": 737.5, "y": 642.0, "width": 81.0, "height": 62.0, "confidence": 0.8720635175704956, "class": "Female", "image_path": "3.png", "prediction_type": "ObjectDetectionModel"}, {"x": 431.5, "y": 939.0, "width": 75.0, "height": 54.0, "confidence": 0.8677240610122681, "class": "Male", "image_path": "3.png", "prediction_type": "ObjectDetectionModel"}, {"x": 846.0, "y": 356.0, "width": 84.0, "height": 66.0, "confidence": 0.867713451385498, "class": "Female", "image_path": "3.png", "prediction_type": "ObjectDetectionModel"}, {"x": 282.5, "y": 640.0, "width": 71.0, "height": 60.0, "confidence": 0.8641939163208008, "class": "Male", "image_path": "3.png", "prediction_type": "ObjectDetectionModel"}, {"x": 330.0, "y": 357.0, "width": 68.0, "height": 60.0, "confidence": 0.8506650924682617, "class": "Affected Male", "image_path": "3.png", "prediction_type": "ObjectDetectionModel"}], "image": {"width": "1008", "height": "1060"}}'

    # 4.png
    #resultJson = '{"predictions": [{"x": 361.5, "y": 91.0, "width": 99.0, "height": 86.0, "confidence": 0.920861005783081, "class": "Deceased Female", "image_path": "4.png", "prediction_type": "ObjectDetectionModel"}, {"x": 548.0, "y": 90.5, "width": 96.0, "height": 87.0, "confidence": 0.9036645889282227, "class": "Deceased Male", "image_path": "4.png", "prediction_type": "ObjectDetectionModel"}, {"x": 137.5, "y": 90.0, "width": 101.0, "height": 86.0, "confidence": 0.9022492170333862, "class": "Deceased Male", "image_path": "4.png", "prediction_type": "ObjectDetectionModel"}, {"x": 659.5, "y": 411.5, "width": 101.0, "height": 83.0, "confidence": 0.8901426792144775, "class": "Female", "image_path": "4.png", "prediction_type": "ObjectDetectionModel"}, {"x": 774.5, "y": 90.5, "width": 111.0, "height": 87.0, "confidence": 0.8847164511680603, "class": "Affected - Decreased Female", "image_path": "4.png", "prediction_type": "ObjectDetectionModel"}, {"x": 188.5, "y": 736.5, "width": 89.0, "height": 73.0, "confidence": 0.8641092777252197, "class": "Male", "image_path": "4.png", "prediction_type": "ObjectDetectionModel"}, {"x": 243.5, "y": 410.0, "width": 95.0, "height": 82.0, "confidence": 0.8576736450195312, "class": "Male", "image_path": "4.png", "prediction_type": "ObjectDetectionModel"}, {"x": 454.0, "y": 739.5, "width": 98.0, "height": 73.0, "confidence": 0.8574193120002747, "class": "Consultand Female", "image_path": "4.png", "prediction_type": "ObjectDetectionModel"}, {"x": 710.0, "y": 737.5, "width": 96.0, "height": 79.0, "confidence": 0.8570454120635986, "class": "Female", "image_path": "4.png", "prediction_type": "ObjectDetectionModel"}, {"x": 244.5, "y": 412.0, "width": 97.0, "height": 82.0, "confidence": 0.7917690277099609, "class": "Affected Male", "image_path": "4.png", "prediction_type": "ObjectDetectionModel"}], "image": {"width": "916", "height": "856"}}'

    # 5.png
    resultJson = '{"predictions": [{"x": 1450.0, "y": 431.0, "width": 80.0, "height": 64.0, "confidence": 0.9222506284713745, "class": "Affected Female", "image_path": "5.png", "prediction_type": "ObjectDetectionModel"}, {"x": 781.5, "y": 722.5, "width": 83.0, "height": 67.0, "confidence": 0.9149703979492188, "class": "Consultand Female", "image_path": "5.png", "prediction_type": "ObjectDetectionModel"}, {"x": 1065.5, "y": 140.5, "width": 81.0, "height": 71.0, "confidence": 0.9018796682357788, "class": "Female", "image_path": "5.png", "prediction_type": "ObjectDetectionModel"}, {"x": 865.5, "y": 144.5, "width": 89.0, "height": 75.0, "confidence": 0.9014055728912354, "class": "Deceased Male", "image_path": "5.png", "prediction_type": "ObjectDetectionModel"}, {"x": 964.0, "y": 429.0, "width": 80.0, "height": 62.0, "confidence": 0.8946155905723572, "class": "Affected Female", "image_path": "5.png", "prediction_type": "ObjectDetectionModel"}, {"x": 1012.5, "y": 724.0, "width": 77.0, "height": 64.0, "confidence": 0.8921630382537842, "class": "Female", "image_path": "5.png", "prediction_type": "ObjectDetectionModel"}, {"x": 696.5, "y": 144.5, "width": 83.0, "height": 73.0, "confidence": 0.8915976285934448, "class": "Deceased Female", "image_path": "5.png", "prediction_type": "ObjectDetectionModel"}, {"x": 1288.0, "y": 433.5, "width": 84.0, "height": 65.0, "confidence": 0.8850415945053101, "class": "Female", "image_path": "5.png", "prediction_type": "ObjectDetectionModel"}, {"x": 1609.5, "y": 432.0, "width": 83.0, "height": 66.0, "confidence": 0.882286787033081, "class": "Female", "image_path": "5.png", "prediction_type": "ObjectDetectionModel"}, {"x": 272.5, "y": 432.0, "width": 79.0, "height": 68.0, "confidence": 0.8818713426589966, "class": "Male", "image_path": "5.png", "prediction_type": "ObjectDetectionModel"}, {"x": 495.0, "y": 143.5, "width": 74.0, "height": 65.0, "confidence": 0.8787811994552612, "class": "Affected Male", "image_path": "5.png", "prediction_type": "ObjectDetectionModel"}, {"x": 1933.0, "y": 432.5, "width": 72.0, "height": 65.0, "confidence": 0.8732598423957825, "class": "Male", "image_path": "5.png", "prediction_type": "ObjectDetectionModel"}, {"x": 433.0, "y": 432.5, "width": 78.0, "height": 67.0, "confidence": 0.8588083982467651, "class": "Male", "image_path": "5.png", "prediction_type": "ObjectDetectionModel"}, {"x": 2092.5, "y": 432.0, "width": 69.0, "height": 64.0, "confidence": 0.8581544160842896, "class": "Male", "image_path": "5.png", "prediction_type": "ObjectDetectionModel"}, {"x": 546.0, "y": 723.0, "width": 76.0, "height": 66.0, "confidence": 0.8571099638938904, "class": "Male", "image_path": "5.png", "prediction_type": "ObjectDetectionModel"}, {"x": 109.5, "y": 432.5, "width": 75.0, "height": 67.0, "confidence": 0.8566229939460754, "class": "Male", "image_path": "5.png", "prediction_type": "ObjectDetectionModel"}, {"x": 1770.5, "y": 434.0, "width": 87.0, "height": 66.0, "confidence": 0.8438470363616943, "class": "Affected Female", "image_path": "5.png", "prediction_type": "ObjectDetectionModel"}, {"x": 1127.0, "y": 430.0, "width": 84.0, "height": 72.0, "confidence": 0.8309265375137329, "class": "Affected Female", "image_path": "5.png", "prediction_type": "ObjectDetectionModel"}, {"x": 594.0, "y": 432.0, "width": 74.0, "height": 60.0, "confidence": 0.8062177896499634, "class": "Affected Male", "image_path": "5.png", "prediction_type": "ObjectDetectionModel"}], "image": {"width": "2250", "height": "930"}}'

    resultJson = json.loads(resultJson)

    numOfFile = removeSymbolsFromImage(imageFilename, extractLineFileName, resultJson)

    for i in range(0, numOfFile):
        imagePath = "TextImages/" + str(i) + ".png"
        img = Image.open(imagePath)
        pytesseract.tesseract_cmd = path_to_tesseract
        text = pytesseract.image_to_string(img)
        refinedText = refineImageText(text)
        refinedText = refinedText.split()
        resultJson["predictions"][i]["Relationship"] = refinedText[1]
        resultJson["predictions"][i]["RelationshipOrder"] = refinedText[0]

    resultJson["predictions"] = remove_close_points(resultJson["predictions"], 5)


    files = glob.glob('TextImages/*')
    for f in files:
        os.remove(f)

    resultJson["predictions"].sort(key=lambda x: int(x["RelationshipOrder"]))
    PEDArray = []

    for i in resultJson["predictions"]:
        if int(i["RelationshipOrder"]) == 0:
            patient = findRelationship("Patient", resultJson["predictions"])

            if "Male" in patient["class"]:
                ped = PED("FAMID", str(i["x"]) + "-" + str(i["y"]), str(patient["x"]) + "-" + str(patient["y"]),
                          0, convertClassToSex(i["class"]),
                          convertClassToAffected(i["class"]))
                ped.addRelationship(i["Relationship"])
                PEDArray.append(ped)
            else:
                ped = PED("FAMID", str(i["x"]) + "-" + str(i["y"]), 0, str(patient["x"]) + "-" + str(patient["y"]),
                          convertClassToSex(i["class"]),
                          convertClassToAffected(i["class"]))
                ped.addRelationship(i["Relationship"])
                PEDArray.append(ped)
        elif int(i["RelationshipOrder"]) == 1:
            mother = findRelationship("Mother", resultJson["predictions"])
            father = findRelationship("Father", resultJson["predictions"])

            ped = PED("FAMID", str(i["x"]) + "-" + str(i["y"]), str(father["x"]) + "-" + str(father["y"]),
                      str(mother["x"]) + "-" + str(mother["y"]), convertClassToSex(i["class"]),
                      convertClassToAffected(i["class"]))
            ped.addRelationship(i["Relationship"])
            PEDArray.append(ped)
        elif int(i["RelationshipOrder"]) == 2:
            GM, GF = getGrandRelationship(resultJson["predictions"])

            distanceFromParentToGrandMother1 = math.dist((GM[0]["x"], GM[0]["y"]), (i["x"], i["y"]))
            distanceFromParentToGrandMother2 = math.dist((GM[1]["x"], GM[1]["y"]), (i["x"], i["y"]))

            distanceFromParentToGrandFather1 = math.dist((GF[0]["x"], GF[0]["y"]), (i["x"], i["y"]))
            distanceFromParentToGrandFather2 = math.dist((GF[1]["x"], GF[1]["y"]), (i["x"], i["y"]))

            if distanceFromParentToGrandMother1 < distanceFromParentToGrandMother2:
                grandMotherFromFather = GM[0]
            else:
                grandMotherFromFather = GM[1]

            if distanceFromParentToGrandFather1 < distanceFromParentToGrandFather2:
                grandFatherFromFather = GF[0]
            else:
                grandFatherFromFather = GF[1]

            grandMotherFromMother = grandMotherFromFather
            grandFatherFromMother = grandFatherFromFather
            ped = PED("FAMID", str(i["x"]) + "-" + str(i["y"]),
                      str(grandFatherFromFather["x"]) + "-" + str(grandFatherFromFather["y"]),
                      str(grandMotherFromFather["x"]) + "-" + str(grandMotherFromFather["y"]),
                      convertClassToSex(i["class"]),
                      convertClassToAffected(i["class"]))
            ped.addRelationship(i["Relationship"])
            PEDArray.append(ped)


        elif int(i["RelationshipOrder"]) == 3:
            mother = findRelationship("Mother", resultJson["predictions"])
            father = findRelationship("Father", resultJson["predictions"])

            GM, GF = getGrandRelationship(resultJson["predictions"])

            distanceFromMotherToGrandMother1 = math.dist((GM[0]["x"], GM[0]["y"]), (mother["x"], mother["y"]))
            distanceFromMotherToGrandMother2 = math.dist((GM[1]["x"], GM[1]["y"]), (mother["x"], mother["y"]))

            distanceFromMotherToGrandFather1 = math.dist((GF[0]["x"], GF[0]["y"]), (father["x"], father["y"]))
            distanceFromMotherToGrandFather2 = math.dist((GF[1]["x"], GF[1]["y"]), (father["x"], father["y"]))

            if i["x"] > mother["x"]:
                if distanceFromMotherToGrandMother1 < distanceFromMotherToGrandMother2:
                    grandMotherFromMother = GM[0]
                else:
                    grandMotherFromMother = GM[1]

                if distanceFromMotherToGrandFather1 < distanceFromMotherToGrandFather2:
                    grandFatherFromMother = GF[1]
                else:
                    grandFatherFromMother = GF[0]

                ped = PED("FAMID", str(i["x"]) + "-" + str(i["y"]),
                          str(grandFatherFromMother["x"]) + "-" + str(grandFatherFromMother["y"]),
                          str(grandMotherFromMother["x"]) + "-" + str(grandMotherFromMother["y"]),
                          convertClassToSex(i["class"]),
                          convertClassToAffected(i["class"]))
                ped.addRelationship(i["Relationship"])
                PEDArray.append(ped)


            elif i["x"] < father["x"]:
                if distanceFromMotherToGrandMother1 < distanceFromMotherToGrandMother2:
                    grandMotherFromFather = GM[1]
                else:
                    grandMotherFromFather = GM[0]

                if distanceFromMotherToGrandFather1 < distanceFromMotherToGrandFather2:
                    grandFatherFromFather = GF[0]
                else:
                    grandFatherFromFather = GF[1]
                ped = PED("FAMID", str(i["x"]) + "-" + str(i["y"]),
                          str(grandFatherFromFather["x"]) + "-" + str(grandFatherFromFather["y"]),
                          str(grandMotherFromFather["x"]) + "-" + str(grandMotherFromFather["y"]),
                          convertClassToSex(i["class"]),
                          convertClassToAffected(i["class"]))
                ped.addRelationship(i["Relationship"])
                PEDArray.append(ped)
        elif int(i["RelationshipOrder"]) == 4:
            ped = PED("FAMID", str(i["x"]) + "-" + str(i["y"]),
                      0,
                      0,
                      convertClassToSex(i["class"]),
                      convertClassToAffected(i["class"]))
            ped.addRelationship(i["Relationship"])
            PEDArray.append(ped)
    PEDArray.reverse()
    convertPEDArrToFile(PEDArray, "test.ped")


main2(imageFilename, pedFilename)
