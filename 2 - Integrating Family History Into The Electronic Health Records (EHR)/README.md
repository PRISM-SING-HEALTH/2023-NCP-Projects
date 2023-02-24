# File Structure
- imageAnalysisExtraction.py
- README.md
- OCRExtraction.py
- HoughLines.py
- 1.png
- 2.png
- 3.png
- 4.png
- 5.png
- Training Data - Contains training data set/
- ObjectDetection/
├─ RoboFlowAPI.py
- Helper/
├─ HelperClasses.py
├─ HelperFunctions.py
- Classes/
├─ PEDClass.py
├─ SymbolClass.py


# Files Breakdown

### imageAnalysisExtraction.py
Convert a pedigree into a PED using image analysis method. 

### OCRExtraction.py
Convert a pedigree into a PED using OCR.

### HoughLines.py
Algorithm for find straight lines in images

### 1.png, 2.png, 3.png, 4.png, 5.png
sample pedigrees images

### ObjectDetection/RoboFlowAPI.py
used to get object detection results from roboflow API

### Helper/HelperClasses.py & Helper/HelperFunctions.py
holds classes for point and cords and contains helper functions

### Classes/PEDClass.py && Classes/SymbolClass.py
contains PED class and symbol class

# How To Run
## OCR
OCR can be run by the **OCRExtraction.py** file, which takes the pedigree image to process, and the PED file name to save the PED to. The default is currently set to: 

    pedFilename = "test.ped"
    imageFilename = "5.png" 
    main(imageFilename, pedFilename)

## Image Analysis 
Image analysis can be run by the **Imageanalysisextraction.py** file, which takes the pedigree image to process, and the PED file name to save the PED to and the flag isAdvance. The default is currently set to: 

    pedFilename = "test.ped"
    imageFilename = "3.png" 
    main(imageFilename, pedFilename, False)
