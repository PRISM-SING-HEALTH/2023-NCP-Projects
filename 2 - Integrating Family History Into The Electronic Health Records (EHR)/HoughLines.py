'''
/**************************************************************************
 *  File Name: HoughLines.py                                              *
 *  Purpose: Uses Probabilistic Hough Line Transform to get straight      *
 *  lines from image                                                      *
 *  REF URL: https://docs.opencv.org/3.4/d9/db0/tutorial_hough_lines.html *
 *  Author: Marcus Francis Cozza - 20595722@student.curtin.edu.au         *
 *  Date: 30/01/2023                                                      *
 *  Version: 1.1                                                          *
 *  Change Log:                                                           *
 *      > 1.1 - Initialise Program 30/01/2023                             *
 **************************************************************************/
 '''

# Imports
import cv2 as cv
import math
import numpy as np


def getPointsFromHoughLines(filename):
    # Loads an image with grey scale
    src = cv.imread(cv.samples.findFile(filename), cv.IMREAD_GRAYSCALE)

    # Check if image is loaded fine
    if src is None:
        print('Error opening image!')

        return -1

    dst = cv.Canny(src, 50, 200, None, 3)

    # Copy edges to the images that will display the results in BGR
    cdst = cv.cvtColor(dst, cv.COLOR_GRAY2BGR)
    cdstP = np.copy(cdst)

    lines = cv.HoughLines(dst, 1, np.pi / 180, 150, None, 0, 0)

    if lines is not None:
        for i in range(0, len(lines)):
            rho = lines[i][0][0]
            theta = lines[i][0][1]
            a = math.cos(theta)
            b = math.sin(theta)
            x0 = a * rho
            y0 = b * rho
            pt1 = (int(x0 + 1000 * (-b)), int(y0 + 1000 * (a)))
            pt2 = (int(x0 - 1000 * (-b)), int(y0 - 1000 * (a)))
            cv.line(cdst, pt1, pt2, (0, 0, 255), 3, cv.LINE_AA)

    # OUTPUT FORMAT: (x1, y1), (x2, y2)
    linesP = cv.HoughLinesP(dst, 1, np.pi / 180, 20, None, 15, 0)

    return linesP, cdstP, src
