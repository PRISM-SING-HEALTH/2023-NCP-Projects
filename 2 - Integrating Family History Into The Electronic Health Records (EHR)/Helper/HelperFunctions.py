'''
/*******************************************************************
 *  File Name: HelperFunctions.py                                  *
 *  Purpose: Helper functions for converting graph                 *
 *  Author: Marcus Francis Cozza - 20595722@student.curtin.edu.au  *
 *  Date: 30/01/2023                                               *
 *  Version: 1.1                                                   *
 *  Change Log:                                                    *
 *      > 1.1 - Initialise Program 30/01/2023                      *
 *******************************************************************/
 '''
import cv2
from PIL import ImageDraw
from PIL import Image
from Classes.SymbolClass import Symbol
from Helper.HelperClasses import *

# Constants
CIRCLE_SIZE = 5

# Remove symbol area
WIDTH_RIGHT = 140
WIDTH_LEFT = 140
HEIGHT_TOP = 100
HEIGHT_BOTTOM = 160

'''
 /*******************************************************
  * CLASS: point                                        *
  * PURPOSE: hold x and y in a point class              *
  *******************************************************/
'''
def removeSymbolsFromImage(readFilename, saveFilename, predictionsJson):
    symbolObjectArray = []

    try:
        imageForText = cv2.imread(readFilename)

        img = Image.open(readFilename)
        drawCircle = ImageDraw.Draw(img)
    except IOError:
        print("Can't Read Image")
        pass

    window_name = 'Image'
    counter = 0
    for i in predictionsJson["predictions"]:
        cloneImageForText = imageForText.copy()
        symbolClass = Symbol(i["x"], i["y"], i["confidence"], i["class"])
        symbolObjectArray.append(symbolClass)

        midBoxWidth = symbolClass.xPos - 10
        midBoxHeight = symbolClass.yPos - 10

        widthOfBox = i["width"] / 2
        heightOfBox = i["height"] / 2

        bottomTextWidth = midBoxWidth - widthOfBox
        bottomTextHeight = midBoxHeight + heightOfBox
        # remove just the symbol

        drawCircle.rectangle(
            (midBoxWidth - widthOfBox, midBoxHeight - heightOfBox, midBoxWidth + widthOfBox,
             midBoxHeight + heightOfBox),
            fill=(255, 255, 255, 255))


        # remove defined area around the symbol
        #image = cv2.rectangle(imageForText, (int(bottomTextWidth - 40), int(bottomTextHeight)), (int(bottomTextWidth + 160), int(bottomTextHeight + 50)),
        #              (255, 0, 0), 2).copy()

        x1 = int(bottomTextWidth - 40)
        y1 = int(bottomTextHeight)

        x2 = int(bottomTextWidth + 160)
        y2 = int(bottomTextHeight + 50)

        textImage = cloneImageForText[y1:y2, x1:x2]

        cv2.imwrite("TextImages/"+str(counter) + ".png", textImage)

        counter += 1
        drawCircle.ellipse(
            (midBoxWidth - CIRCLE_SIZE, midBoxHeight - CIRCLE_SIZE, midBoxWidth + CIRCLE_SIZE,
             midBoxHeight + CIRCLE_SIZE),
            fill=(255, 0, 0, 255))

    img.save(saveFilename)
    return counter

def refineImageText(text):
    text = text.lower()
    returnString = ""
    if 'grandf' in text:
        returnString = "4 GrandFather"
    elif 'grandm' in text:
        returnString = "4 GrandMother"
    elif 'uncle' in text:
        returnString = "3 Uncle"
    elif 'aunt' in text:
        returnString = "3 Aunt"
    elif 'mother' in text:
        returnString = "2 Mother"
    elif 'father' in text:
        returnString = "2 Father"
    elif 'son' in text or 'child' in text:
        returnString = "0 son"
    elif 'daughter' in text or 'child' in text:
        returnString = "0 daughter"
    elif 'sister' in text:
        returnString = "1 Sister"
    elif 'brother' in text:
        returnString = "1 Brother"
    else:
        returnString = "1 Patient"

    return returnString

def findRelationship(type, resultJson):
    for i in resultJson:
        if i["Relationship"] == type:
            return i
    return 0

def getGrandRelationship(resultJson):
    GM = []
    GF = []
    for i in resultJson:
        if i["Relationship"] == "GrandMother":
            GM.append(i)
        elif i["Relationship"] == "GrandFather":
            GF.append(i)
    return GM, GF


def convertClassToSex(symbolClass):
    sex = "a"
    if 'Male' in symbolClass:
        sex = 1
    elif 'Female' in symbolClass:
        sex = 2
    return sex


def convertClassToAffected(symbolClass):
    affected = 0
    if 'Affected' in symbolClass:
        affected = 2
    else:
        affected = 1
    return affected


def checkIfSymbolNode(x, y, symbolArr):
    for i in symbolArr:
        if symbolArr.xPos == x and symbolArr.yPos == y:
            return True
    return False


def checkIfSymbolNode(x, y, symbolArr):
    for i in symbolArr:
        if i.xPos == x and i.yPos == y:
            return True
    return False

def remove_close_points(json_array, threshold):
    result = json_array
    result.sort(key=lambda x: int(x["confidence"]))
    duplicateSymbols = []
    for i in result:
        counter = 0
        for k in json_array:
            if not(i == k):
                x1 = i["x"]
                y1 = i["y"]

                x2 = k["x"]
                y2 = k["y"]

                distance = math.dist((x1, y1), (x2, y2))

                if not(distance >= threshold):
                    duplicateSymbols.append(counter)


            counter += 1

    for i in range(0, len(duplicateSymbols) - 1):
        result.pop(duplicateSymbols[i])

    return result






def convertPEDArrToFile(PEDArray, filename):
    f = open(filename, "w")
    for i in PEDArray:
        f.write(
            str(i.familyID) + "\t " + str(i.individualID) + "\t " + str(i.paternalID) + "\t " + str(i.maternalID) + "\t " + str(
                i.sex) + "\t " + str(i.phenotype) + "\t" + str(i.getRelationship()) +"\n")
    f.close()


def appendPEDArrToFile(PEDArray, filename):
    f = open(filename, "a")
    for i in PEDArray:
        f.write(
            str(i.familyID) + " " + str(i.individualID) + " " + str(i.paternalID) + " " + str(i.maternalID) + " " + str(
                i.sex) + " " + str(i.phenotype) + "\n")
    f.close()


def convertStringToPoint(cordsString):
    cordsString = cordsString.split()
    xCord = cordsString[0].split(':')
    yCord = cordsString[1].split(':')
    xCord = xCord[1]
    yCord = yCord[1]
    return point(xCord, yCord)


def convertSymbolToPoint(cordsString):
    cordsString = cordsString.split('-')
    xCord = cordsString[0]
    yCord = cordsString[1]
    return point(int(xCord), int(yCord))


def convertPointToString(x, y):
    strPoint = "x:" + str(int(x)) + " " + "y:" + str(int(y))
    return strPoint
