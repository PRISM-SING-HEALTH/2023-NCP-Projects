'''
/*******************************************************************
 *  File Name: SymbolClass.py                                      *
 *  Purpose: class for holding Symbol structure                    *
 *  Author: Marcus Francis Cozza - 20595722@student.curtin.edu.au  *
 *  Date: 30/01/2023                                               *
 *  Version: 1.1                                                   *
 *  Change Log:                                                    *
 *      > 1.1 - Initialise Program 30/01/2023                      *
 *******************************************************************/
 '''
class Symbol:
    def __init__(self, xPos, yPos, confidence, modelClass):
        self.xPos = xPos
        self.yPos = yPos
        self.confidence = confidence
        self.modelClass = modelClass

    # HELPER FUNCTIONS

    # format string output
    def __str__(self):
        return f"xPos:{self.xPos} yPos:{self.yPos} conf:{self.confidence} class:{self.modelClass} relationship:{self.relationship}"



