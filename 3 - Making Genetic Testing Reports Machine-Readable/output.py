'''
    This module is for outputting the extracted data from Genetic Testing Reports to a CSV file
    
    Report Types Currently Supported:
        - Invitae Diagnostic Testing Reports
        - Invitae Carrier Screening Reports
        - Invitae Familial Variant Testing Reports
'''
from dataExtraction import InvitaeData, InvitaeCarrier, InvitaeFamilial


def multiResultOutput(multiResult: list) -> str:
    output = ""
    for r in multiResult:
        if r == multiResult[-1]:
            output = output + r
        else:
            output = output + r + "; "
    return output


def getGeneListOutput(geneList: list[dict]) -> str:
    '''
        Formats the geneList data into a list separated by ';' for writing to csv

        Parameters:
            geneList: list[dict] - list of genes to format

        Returns:
            a string of the formatted genes output
    '''
    output = ""
    for gene in geneList:
        output += gene.get('gene') + "; "
    return output


def extractedDataToCSV(csvName: str, reportData: InvitaeData) -> None:
    '''
        Extracted Data is outputed to CSV. This is for Invitae Diagnostic Testing Reports.

        Parameters:
            csvName: str - name of CSV file to write to
            reportData: InvitaeData - the data to write to the csv file
    '''

    with open(csvName, 'w') as f:
        f.write(
            "Report ID,Patient ID (MRN),Patient Name,DOB,sex,Lab,Report Date,Sample Type,Reason for Testing,Tests,Result,Gene,Transcript,Variant,Protein Change,Exon,Zygosity,Classification,Association,Population Databases,Protein Modeling,ClinVar,PubMed,Experimental Studies,Familial VUS,Genes Tested\n")
        if len(reportData.variations) != 0:
            for i in range(len(reportData.variations)):
                f.write(reportData.reportID + "," + reportData.patient['id'] + "," + reportData.patient['name'] + "," + reportData.patient['dob'] + "," + reportData.patient['sex'] + "," + reportData.lab + "," + reportData.reportDate + "," + reportData.sampleType + "," + reportData.reason + "," + multiResultOutput(reportData.tests) + "," + reportData.result + "," + reportData.variations[i]['gene'] + "," + reportData.variations[i]["geneTranscriptID"] + "," + reportData.variations[i]["geneVariant"] + "," + reportData.variations[i]["proteinVariant"] + "," + reportData.variations[i]['exon']+","+reportData.variations[i]
                        ["zygosity"] + "," + reportData.variations[i]["classification"] + "," + reportData.variations[i]["association"] + "," + reportData.variations[i]["population"] + "," + reportData.variations[i]["proteinModeling"] + "," + reportData.variations[i]["clinVar"] + "," + reportData.variations[i]["pubMed"] + "," + reportData.variations[i]["experimental"] + "," + reportData.variations[i]["familial"] + "," + getGeneListOutput(reportData.geneList) + "\n")
        else:
            f.write(reportData.reportID + "," + reportData.patient['id'] + "," + reportData.patient['name'] + "," + reportData.patient['dob'] + "," + reportData.patient['sex'] + "," + reportData.lab + "," + reportData.reportDate + "," + reportData.sampleType + "," + reportData.reason + "," + multiResultOutput(
                reportData.tests) + "," + reportData.result + "," + ',,,,,,,,,,,,,,' + getGeneListOutput(reportData.geneList) + "\n")


def addInvitaeDataEntryToCSV(csvName: str, reportData: InvitaeData) -> None:
    '''
        Adds the extracted data to an existing CSV. This is for Invitae Diagnostic Testing Reports.

        Parameters:
            csvName: str - name of CSV file to write to
            reportData: InvitaeData - the data to write to the csv file
    '''
    with open(csvName, 'a') as f:
        if len(reportData.variations) != 0:
            for i in range(len(reportData.variations)):
                f.write(reportData.reportID + "," + reportData.patient['id'] + "," + reportData.patient['name'] + "," + reportData.patient['dob'] + "," + reportData.patient['sex'] + "," + reportData.lab + "," + reportData.reportDate + "," + reportData.sampleType + "," + reportData.reason + "," + multiResultOutput(reportData.tests) + "," + reportData.result + "," + reportData.variations[i]['gene'] + "," + reportData.variations[i]["geneTranscriptID"] + "," + reportData.variations[i]["geneVariant"] + "," + reportData.variations[i]["proteinVariant"] + "," + reportData.variations[i]['exon']+","+reportData.variations[i]
                        ["zygosity"] + "," + reportData.variations[i]["classification"] + "," + reportData.variations[i]["association"] + "," + reportData.variations[i]["population"] + "," + reportData.variations[i]["proteinModeling"] + "," + reportData.variations[i]["clinVar"] + "," + reportData.variations[i]["pubMed"] + "," + reportData.variations[i]["experimental"] + "," + reportData.variations[i]["familial"] + "," + getGeneListOutput(reportData.geneList) + "\n")
        else:
            f.write(reportData.reportID + "," + reportData.patient['id'] + "," + reportData.patient['name'] + "," + reportData.patient['dob'] + "," + reportData.patient['sex'] + "," + reportData.lab + "," + reportData.reportDate + "," + reportData.sampleType + "," + reportData.reason + "," + multiResultOutput(
                reportData.tests) + "," + reportData.result + "," + ',,,,,,,,,,,,,,' + getGeneListOutput(reportData.geneList) + "\n")


def carrierDataToCSV(csvName: str, reportData: InvitaeCarrier) -> None:
    '''
        Extracted Data is outputed to CSV. This is for Invitae Carrier Screening Reports.

        Parameters:
            csvName: str - name of CSV file to write to
            reportData: InvitaeData - the data to write to the csv file
    '''
    with open(csvName, 'w') as f:
        f.write("Report ID,Patient ID (MRN),Patient Name,DOB,Sex,Lab,Report Date,Sample Type,Reason for Testing,Tests,Result,Gene,Transcript,Variant,Protein Change,Exon,Zygosity,Classification,Carrier,Inheritance,Partner Testing,Population Databases,Protein Modeling,ClinVar,PubMed,Experimental Studies,Genes Tested\n")
        if len(reportData.variations) != 0:
            for i in range(len(reportData.variations)):
                f.write(reportData.reportID + "," + reportData.patient['id'] + "," + reportData.patient['name'] + "," + reportData.patient['dob'] + "," + reportData.patient['sex'] + "," + reportData.lab + "," + reportData.reportDate + "," + reportData.sampleType + "," + reportData.reason + "," + multiResultOutput(reportData.tests) + "," + reportData.result + "," + reportData.variations[i]['gene'] + "," + reportData.variations[i]["geneTranscriptID"] + "," + reportData.variations[i]["geneVariant"] + "," + reportData.variations[i]["proteinVariant"] + "," + reportData.variations[i]['exon']+","+reportData.variations[i]
                        ["zygosity"] + "," + reportData.variations[i]["classification"] + "," + reportData.variations[i]["result"] + "," + reportData.variations[i]["inheritance"] + "," + reportData.variations[i]["partnerTest"] + "," + reportData.variations[i]["population"] + "," + reportData.variations[i]["proteinModeling"] + "," + reportData.variations[i]["clinVar"] + "," + reportData.variations[i]["pubMed"] + "," + reportData.variations[i]["experimental"] + "," + getGeneListOutput(reportData.geneList) + "\n")
        else:
            f.write(reportData.reportID + "," + reportData.patient['id'] + "," + reportData.patient['name'] + "," + reportData.patient['dob'] + "," + reportData.patient['sex'] + "," + reportData.lab + "," + reportData.reportDate + "," + reportData.sampleType + "," + reportData.reason + "," + multiResultOutput(
                reportData.tests) + "," + reportData.result + ",,,,,,,,,,,,,,,," + getGeneListOutput(reportData.geneList) + "\n")


def addCarrierDataEntryToCSV(csvName: str, reportData: InvitaeCarrier) -> None:
    '''
        Adds the extracted data to an existing CSV. This is for Invitae Carrier Screening Reports.

        Parameters:
            csvName: str - name of CSV file to write to
            reportData: InvitaeData - the data to write to the csv file
    '''
    with open(csvName, 'a') as f:
        if len(reportData.variations) != 0:
            for i in range(len(reportData.variations)):
                f.write(reportData.reportID + "," + reportData.patient['id'] + "," + reportData.patient['name'] + "," + reportData.patient['dob'] + "," + reportData.patient['sex'] + "," + reportData.lab + "," + reportData.reportDate + "," + reportData.sampleType + "," + reportData.reason + "," + multiResultOutput(reportData.tests) + "," + reportData.result + "," + reportData.variations[i]['gene'] + "," + reportData.variations[i]["geneTranscriptID"] + "," + reportData.variations[i]["geneVariant"] + "," + reportData.variations[i]["proteinVariant"] + "," + reportData.variations[i]['exon']+","+reportData.variations[i]
                        ["zygosity"] + "," + reportData.variations[i]["classification"] + "," + reportData.variations[i]["result"] + "," + reportData.variations[i]["inheritance"] + "," + reportData.variations[i]["partnerTest"] + "," + reportData.variations[i]["population"] + "," + reportData.variations[i]["proteinModeling"] + "," + reportData.variations[i]["clinVar"] + "," + reportData.variations[i]["pubMed"] + "," + reportData.variations[i]["experimental"] + "," + getGeneListOutput(reportData.geneList) + "\n")
        else:
            f.write(reportData.reportID + "," + reportData.patient['id'] + "," + reportData.patient['name'] + "," + reportData.patient['dob'] + "," + reportData.patient['sex'] + "," + reportData.lab + "," + reportData.reportDate + "," + reportData.sampleType + "," + reportData.reason + "," + multiResultOutput(
                reportData.tests) + "," + reportData.result + ",,,,,,,,,,,,,,,," + getGeneListOutput(reportData.geneList) + "\n")


def familialDataToCSV(csvName: str, reportData: InvitaeFamilial) -> None:
    '''
        Extracted Data is outputed to CSV. This is for Invitae Familial Variant Testing Reports.

        Parameters:
            csvName: str - name of CSV file to write to
            reportData: InvitaeData - the data to write to the csv file
    '''
    with open(csvName, 'w') as f:
        f.write(
            "Report ID,Patient ID (MRN),Patient Name,DOB,sex,Lab,Report Date,Sample Type,Reason for Testing,Tests,Result,Gene,Transcript,Variant,Protein Change,Exon,Zygosity,Classification,Association,Population Databases,Protein Modeling,ClinVar,PubMed,Experimental Studies,Genes Tested\n")
        if len(reportData.variations) != 0:
            for i in range(len(reportData.variations)):
                f.write(reportData.reportID + "," + reportData.patient['id'] + "," + reportData.patient['name'] + "," + reportData.patient['dob'] + "," + reportData.patient['sex'] + "," + reportData.lab + "," + reportData.reportDate + "," + reportData.sampleType + "," + reportData.reason + "," + multiResultOutput(reportData.tests) + "," + reportData.result + "," + reportData.variations[i]['gene'] + "," + reportData.variations[i]["geneTranscriptID"] + "," + reportData.variations[i]["geneVariant"] + "," + reportData.variations[i]["proteinVariant"] + "," + reportData.variations[i]['exon']+","+reportData.variations[i]
                        ["zygosity"] + "," + reportData.variations[i]["classification"] + "," + reportData.variations[i]["association"] + "," + reportData.variations[i]["population"] + "," + reportData.variations[i]["proteinModeling"] + "," + reportData.variations[i]["clinVar"] + "," + reportData.variations[i]["pubMed"] + "," + reportData.variations[i]["experimental"] + "," + getGeneListOutput(reportData.geneList) + "\n")
        else:
            f.write(reportData.reportID + "," + reportData.patient['id'] + "," + reportData.patient['name'] + "," + reportData.patient['dob'] + "," + reportData.patient['sex'] + "," + reportData.lab + "," + reportData.reportDate + "," + reportData.sampleType + "," + reportData.reason + "," + multiResultOutput(
                reportData.tests) + "," + reportData.result + "," + ',,,,,,,,,,,,,' + getGeneListOutput(reportData.geneList) + "\n")


def addFamilialDataEntryToCSV(csvName: str, reportData: InvitaeFamilial) -> None:
    '''
        Adds the extracted data to an existing CSV. This is for Invitae Familial Variant Testing Reports.

        Parameters:
            csvName: str - name of CSV file to write to
            reportData: InvitaeData - the data to write to the csv file
    '''
    with open(csvName, 'a') as f:
        if len(reportData.variations) != 0:
            for i in range(len(reportData.variations)):
                f.write(reportData.reportID + "," + reportData.patient['id'] + "," + reportData.patient['name'] + "," + reportData.patient['dob'] + "," + reportData.patient['sex'] + "," + reportData.lab + "," + reportData.reportDate + "," + reportData.sampleType + "," + reportData.reason + "," + multiResultOutput(reportData.tests) + "," + reportData.result + "," + reportData.variations[i]['gene'] + "," + reportData.variations[i]["geneTranscriptID"] + "," + reportData.variations[i]["geneVariant"] + "," + reportData.variations[i]["proteinVariant"] + "," + reportData.variations[i]['exon']+","+reportData.variations[i]
                        ["zygosity"] + "," + reportData.variations[i]["classification"] + "," + reportData.variations[i]["association"] + "," + reportData.variations[i]["population"] + "," + reportData.variations[i]["proteinModeling"] + "," + reportData.variations[i]["clinVar"] + "," + reportData.variations[i]["pubMed"] + "," + reportData.variations[i]["experimental"] + "," + getGeneListOutput(reportData.geneList) + "\n")
        else:
            f.write(reportData.reportID + "," + reportData.patient['id'] + "," + reportData.patient['name'] + "," + reportData.patient['dob'] + "," + reportData.patient['sex'] + "," + reportData.lab + "," + reportData.reportDate + "," + reportData.sampleType + "," + reportData.reason + "," + multiResultOutput(
                reportData.tests) + "," + reportData.result + "," + ',,,,,,,,,,,,,' + getGeneListOutput(reportData.geneList) + "\n")
