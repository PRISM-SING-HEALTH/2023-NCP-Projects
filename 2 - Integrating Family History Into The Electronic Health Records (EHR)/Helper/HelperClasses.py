'''
/*******************************************************************
 *  File Name: HelperClasses.py                                      *
 *  Purpose: Helper classes for holding information about cords    *
 *  Author: Marcus Francis Cozza - 20595722@student.curtin.edu.au  *
 *  Date: 30/01/2023                                               *
 *  Version: 1.1                                                   *
 *  Change Log:                                                    *
 *      > 1.1 - Initialise Program 30/01/2023                      *
 *******************************************************************/
'''

from HoughLines import *

'''
 /*******************************************************
  * CLASS: point                                        *
  * PURPOSE: hold x and y in a point class              *
  *******************************************************/
'''
class point:
    def __init__(self, x, y):
        self.x = int(x)
        self.y = int(y)

    def __str__(self):
        return f"x:{self.x} y:{self.y}"


'''
 /*******************************************************
  * CLASS: cord                                         *
  * PURPOSE: hold x1, y1, x2, y2 in a cord class        *
  *******************************************************/
'''
class cord:
    def __init__(self, x1, x2, y1, y2):
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2

    def __str__(self):
        return f"x1:{self.x1} x2:{self.x2} y1:{self.y1} y2:{self.y2}"



'''
 /*******************************************************
  * CLASS: DrawLineWidget                               *
  * PURPOSE: class that allows for lines to be drawn    *
  *        from symbol to symbol                         *
  *******************************************************/
'''
class DrawLineWidget(object):
    def __init__(self, imageToRead, symbolCords, imageWithNoLines):
        self.original_image = cv.imread(imageToRead)
        self.imageWithNoLines = cv.imread(imageWithNoLines)
        self.clone = self.original_image.copy()
        self.symbolCords = symbolCords
        self.symbolsArray = []
        self.resetPEDFileChildSymbols("test.ped")

        cv.namedWindow('image', cv.WINDOW_NORMAL)
        cv.setMouseCallback('image', self.extract_coordinates)

        # List to store start/end points
        self.image_coordinatesFirstPos = []
        self.image_coordinatesSecondPos = []

    def checkIfPointIsCloseToSymbol(self, x, y):
        for i in self.symbolCords:
            if abs(i.xPos - x) < 50 and abs(i.yPos - y) < 50 and not (i.xPos == x) and not (i.yPos == x):
                return True
        return False

    def getSymbolPointFromClosePoint(self, x, y):
        for i in self.symbolCords:
            if abs(i.xPos - x) < 50 and abs(i.yPos - y) < 50 and not (i.xPos == x) and not (i.yPos == x):
                return point(i.xPos, i.yPos)
        return False

    def extract_coordinates(self, event, x, y, flags, parameters):
        # Record starting (x,y) coordinates on left mouse button click
        if event == cv.EVENT_LBUTTONDOWN:
            if len(self.image_coordinatesFirstPos) == 0 and self.checkIfPointIsCloseToSymbol(x, y):
                self.image_coordinatesFirstPos = [(x, y)]
            elif (self.checkIfPointIsCloseToSymbol(x, y)):
                self.image_coordinatesSecondPos = [(x, y)]
                # Draw line
                cv.line(self.clone, self.image_coordinatesFirstPos[0], self.image_coordinatesSecondPos[0],
                        (0, 200, 255), 3)
                cv.imshow("image", self.clone)

                x1, y1 = self.image_coordinatesFirstPos[0]
                x2, y2 = self.image_coordinatesSecondPos[0]

                pointStart = self.getSymbolPointFromClosePoint(x1, y1)
                pointEnd = self.getSymbolPointFromClosePoint(x2, y2)

                self.symbolsArray.append(cord(pointStart.x, pointStart.y, pointEnd.x, pointEnd.y))

                self.image_coordinatesFirstPos = []
                self.image_coordinatesSecondPos = []
            else:
                self.image_coordinatesFirstPos = []
                self.image_coordinatesSecondPos = []
        # Clear drawing lines on right mouse button click
        elif event == cv.EVENT_RBUTTONDOWN:
            self.clone = self.original_image.copy()
            self.symbolsArray = []

        elif event == cv.EVENT_RBUTTONDBLCLK:
            self.clone = self.imageWithNoLines.copy()
            self.symbolsArray = []

    def show_image(self):
        return self.clone

    def resetPEDFileChildSymbols(self, filename):
        f1 = open(filename, 'r')
        Lines = f1.readlines()
        f1.close()
        f2 = open(filename, 'w')
        for line in Lines:

            if line.split()[2] == '0':
                f2.write(str(line))

        f2.close()

    def getSymbolArray(self):
        return self.symbolsArray
