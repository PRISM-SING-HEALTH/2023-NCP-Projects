'''
    This is the main module for Genetic-Report-PDF-Extraction

    Current Functionality:
        - Reads all PDFs in given file
        - Extracts data from PDFs to CSV files (one CSV for each Report Type)
        - Prints to shell any Exceptions or Errors encountered
        
    Report Types Currently Supported:
        - Invitae Diagnostic Testing Reports
        - Invitae Carrier Screening Reports
        - Invitae Familial Variant Testing Reports
'''
import os
import time
import re
from dataExtraction import InvitaeData, InvitaeCarrier, InvitaeFamilial
import output
from pdfextract import detailedExtract


def findInvitaeReportType(text: str) -> InvitaeCarrier | InvitaeData | InvitaeFamilial:
    '''
        Finds what type of report it is and creates a report variable with the correct data type. 
        Types of reports: Carrier Screening, Diagnostic Testing, Familial Variant Testing

        Parameters:
            text: str - the extracted text from the pdf report

        Returns:
            variable of correct report type. Note this variable does not contain the data from the report.
    '''
    if "INVITAE DIAGNOSTIC TESTING RESULTS" in text:
        famOrDiagnosticMatch = re.search(
            r"Test performed\s(Family history|Diagnostic test for a personal)", text)
        if famOrDiagnosticMatch is not None:
            if famOrDiagnosticMatch.group() == "Family history":
                report = InvitaeFamilial()
            else:
                report = InvitaeData()
        else:
            report = None
    elif "INVITAE CARRIER SCREEN RESULTS" in text:
        report = InvitaeCarrier()
    else:
        report = None
    return report


def invitaeOrPreventionGenetics(fileName: str) -> InvitaeData | None:
    '''
        Extracts the text from a pdf Genetic Testing Report

        Parameters:
            fileName: str - the name of the pdf

        Returns:
            extracted report or None

        Exceptions:
            NotImplementedError: when pdf is Prevention Genetics Report
            ValueError: when the pdf is not Invitae or Prevention Genetics Report
    '''
    text = detailedExtract(fileName, 0)
    report = None
    if text.find("INVITAE") != -1:
        # it is invitae
        report = findInvitaeReportType(text)
        report.getData(fileName, text)

    elif text.find("PG ") != -1:
        # it is prevention genetics
        raise NotImplementedError(
            "A Prevention Genetics Report was selected. The methods to extract data from PG has not been implemented yet")
    else:
        # it is neither invitae or prevention genetics
        raise ValueError(
            "Report selected is not Invitae or Prevention Genetics Report")

    return report


def outputToCSV(csvName: str, report: InvitaeCarrier | InvitaeData | InvitaeFamilial):
    '''
        Writes the extracted report data to a CSV file.

        Parameters:
            csvName: str - the name of CSV file
            report: InvitaeCarrier | InvitaeData | InvitaeFamilial - the report with extracted data

    '''
    if type(report) is InvitaeCarrier:
        fileNameList = csvName.split(".")
        csvName = fileNameList[0] + "-Carrier." + fileNameList[1]
        if os.path.isfile(csvName):
            output.addCarrierDataEntryToCSV(csvName, report)
        else:
            output.carrierDataToCSV(csvName, report)
    elif type(report) is InvitaeFamilial or type(report) is InvitaeData:
        if os.path.isfile(csvName):
            output.addInvitaeDataEntryToCSV(csvName, report)
        else:
            output.extractedDataToCSV(csvName, report)


if __name__ == "__main__":
    start = time.time()
    folder = input("enter the name of the folder containing reports: ")
    reportList = []

    for file in os.listdir(folder):
        if file.endswith(".pdf"):
            reportList.append(folder+"/"+file)

    csvName = input("enter CSV file to extract to: ")

    try:
        testReport = invitaeOrPreventionGenetics(reportList[0])
    except NotImplementedError as notImplemented:
        print("File: " + reportList[0] + notImplemented)
    except Exception as e:
        print("Error extracting data from " + reportList[0])
        print("\tError: " + str(e))
    else:
        outputToCSV(csvName, testReport)

    for r in reportList[1:]:
        try:
            testReport = invitaeOrPreventionGenetics(r)
        except NotImplementedError as notImplemented:
            print("File: " + r + notImplemented)
        except Exception as e:
            print("Error extracting data from " + r)
            print("\tError: " + str(e))
        else:
            outputToCSV(csvName, testReport)

    end = time.time()
    print("TIME: \033[1;32m" + str(end - start) + "\033[0m")
