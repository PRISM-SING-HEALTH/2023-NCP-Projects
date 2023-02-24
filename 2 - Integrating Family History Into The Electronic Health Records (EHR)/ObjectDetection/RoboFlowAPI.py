'''
/*******************************************************************
 *  File Name: RoboFlowAPI.py                                      *
 *  Purpose: Get object detection results from an image            *
 *  Author: Marcus Francis Cozza - 20595722@student.curtin.edu.au  *
 *  Date: 30/01/2023                                               *
 *  Version: 1.1                                                   *
 *  Change Log:                                                    *
 *      > 1.1 - Initialise Program 30/01/2023                      *
 *******************************************************************/
 '''
from roboflow import Roboflow


def getPredictions(imageFileName):
    rf = Roboflow(api_key="KmSfecf3nSPF98AorKoc")
    project = rf.workspace().project("family-tree")
    model = project.version(3).model

    # infer on a local image
    jsonResult = model.predict(imageFileName, confidence=40, overlap=30).json()
    return jsonResult


# visualize your prediction
#model.predict("your_image.jpg", confidence=40, overlap=30).save("prediction.jpg")

# infer on an image hosted elsewhere
# print(model.predict("URL_OF_YOUR_IMAGE", hosted=True, confidence=40, overlap=30).json())