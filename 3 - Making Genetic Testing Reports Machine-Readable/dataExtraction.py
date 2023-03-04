'''
    This is the module containing the classes for the Report Types. It extracts the data for the reports.

    Current Functionality:
        - Contains InvitaeData class for Invitae Diagnostic Testing Reports
        - Contains InvitaeCarrier class for Invitae Carrier Screening Reports
        - Contains InvitaeFamilial class for Invitae Familial Variant Testing Reports
    
    Report Types Currently Supported:
        - Invitae Diagnostic Testing Reports
        - Invitae Carrier Screening Reports
        - Invitae Familial Variant Testing Reports
'''
import re
from pdfextract import detailedExtract, tableExtract, findPageNum


class InvitaeData:
    '''Class for data extracted from Invitae Genetic Testing Report'''

    def __init__(self) -> None:
        self.text = ""
        self.reportID = ""
        self.lab = ""
        self.patient = {
            "id": "",
            "name": "",
            "dob": "",
            "sex": ""
        }
        self.reportDate = ""
        self.sampleType = ""
        self.reason = ""
        self.tests = []
        self.result = ""
        self.variations = []
        self.geneList = []  # list of genes and their transcriptID

    # METHODS FOR GETTING DATA FROM EXTRACTED TEXT
    def getData(self, fileName: str, text: str) -> None:
        '''
            Gets the data from the extracted text

            Parameters:
                fileName: str - the name of the pdf
                text: str - the extracted text
        '''
        self.fileName = fileName
        self.text = text
        self.lines = self.text.splitlines()

        # report ID
        self.getReportID()

        # lab
        self.getLab()

        # patient details
        self.getPatient()

        # report date
        self.getReportDate()

        # sample type
        self.getSampleType()

        # reason for testing
        self.getReasonForTests()

        # tests
        self.getTests()

        # result
        self.getResult()

        if self.result != "NEGATIVE":
            # variations
            self.getVariations()

        # geneList
        self.getGeneList()

    def getReportID(self):
        '''
            Gets the Report ID of the Genetic Testing Report.
        '''
        matchID = re.search(r"Invitae #:(.*)", self.text)
        if matchID is not None:
            self.reportID = matchID.group(1).strip()

    def getLab(self):
        '''
            Gets the Lab of the Genetic Testing Report.
        '''
        if 'Invitae' in self.text:
            self.lab = 'Invitae'
        else:
            raise ValueError("Not Invitae Genetic Testing Report")

    def getPatient(self):
        '''
            Gets the Patient's details from the report.
        '''
        # Patient's ID
        matchMRN = re.search(r"(Patient ID [(]MRN[)]:|MRN:)(.*)", self.text)
        if matchMRN is not None:
            self.patient["id"] = matchMRN.group(2).strip().replace(",", ";")
            if matchMRN.group(2).isspace() or len(matchMRN.group(2)) == 0:
                self.patient['id'] = "-"

        # Patient's name
        matchName = re.search(r"Patient name:(.*) Sample type", self.text)
        if matchName is not None:
            self.patient["name"] = matchName.group(1).strip().replace(",", ";")

        # Patient's date of birth
        matchDOB = re.search(r"DOB:(.*) Sample", self.text)
        if matchDOB is not None:
            self.patient["dob"] = matchDOB.group(1).strip().replace(",", ";")

        # Patient's sex
        matchSex = re.search(
            r"(Sex:|Sex assigned at birth:)(.*)Sample", self.text)
        if matchSex is not None:
            self.patient["sex"] = matchSex.group(2).strip().replace(",", ";")

    def getReportDate(self):
        '''
            Gets the Report Date from the report.
        '''
        matchDate = re.search(r"Report date:(.*)", self.text)
        if matchDate is not None:
            self.reportDate = matchDate.group(1).strip().replace(",", ";")

    def getSampleType(self):
        '''
            Gets the Sample Type from the report.
        '''
        matchSample = re.search(r"Sample type:(.*) Report", self.text)
        if matchSample is not None:
            self.sampleType = matchSample.group(1).strip().replace(",", ";")

    def getReasonForTests(self):
        '''
            Gets the Reason For Testing from the report.
        '''
        matchReason = re.search(
            r"Test performed\s(.*)Sequence analysis and deletion", self.text)
        if matchReason is not None:
            self.reason = matchReason.group(1).strip().replace(",", ";")

    def getTests(self):
        '''
            Gets the list of tests conducted from the report.
        '''
        matchObj = re.search(r".* Genes Analyzed section\.", self.text)
        if matchObj is not None:
            x = self.lines.index(matchObj.group())
            x = x + 1
            while "RESULT:" not in self.lines[x]:
                if len(self.lines[x]) > 0:
                    self.tests.append(self.lines[x])
                x = x + 1

    def getResult(self):
        '''
            Gets the Result from the report.
        '''
        matchResult = re.search(
            r"RESULT: (POSITIVE|NEGATIVE|UNCERTAIN|CARRIER|POTENTIALLY POSITIVE)", self.text)
        if matchResult is not None:
            self.result = matchResult.group(1)

    def getAssociation(self):
        '''
            Gets the Associations from the report.
        '''
        matchAssociationList = re.findall(
            r"The .* gene is associated with[\w\s\-,():]*[(]MedGen\sUID:\s\d*[)]", self.text)
        if matchAssociationList:
            if len(matchAssociationList) <= len(self.variations):
                i = 0
                for var in self.variations:
                    y = re.split(r" gene is associated with ",
                                 matchAssociationList[i])
                    gene = y[0][4:]
                    if gene == var["gene"]:
                        association = re.sub(
                            r"\s[(]MedGen\sUID:\s\d*[)]", "", y[1])
                        if "\n" in association:
                            association = association.replace("\n", "")
                        var["association"] = "{0}{1}".format(
                            association[0].capitalize(), association[1:]).replace(",", "")
                        if i != len(matchAssociationList) - 1:
                            i = i + 1
                    else:
                        var["association"] = "-"
            else:
                raise IndexError("There are more Associations than Variations")
        else:
            for v in self.variations:
                v["association"] = "-"

    def getExon(self, variantText: str) -> str:
        '''
            Returns the exon for a gene variant.
        '''
        matchExon = re.search(r"(Exon|Intron|Exons) ([\d\-]*)", variantText)
        if matchExon is not None:
            exon = matchExon.group(2)
        else:
            exon = "-"
        return exon

    def getPopulation(self, variantText: str) -> str:
        '''
            Returns the population (gnomAD) for a gene variant.
        '''
        matchPopulation = re.search(
            r"gnomAD (no frequency|[\d.]*%)", variantText)
        if matchPopulation is not None:
            population = matchPopulation.group(1).strip()
        else:
            population = "-"
        return population

    def getClinVar(self, variantText: str) -> str:
        '''
            Returns the ClinVar ID for a gene variant.
        '''
        matchClinVar = re.search(r"[(]Variation ID: (\d*)[)]", variantText)
        if matchClinVar is not None:
            clinVar = matchClinVar.group(1).strip()
        else:
            literature = re.search(
                r"not been reported in the literature", variantText)
            if literature is not None:
                clinVar = None
            else:
                clinVar = None
        return clinVar

    def getPubMedAndExperimental(self, variantText: str) -> tuple[str | None, str | None]:
        '''
            Returns the PMIDs for a gene variant.
        '''
        matchPMID = re.findall(
            r"(Experimental studies|.*).*PMID: ([\d,\s\w]*)[)][.]", variantText,)
        pubMed = ""
        experimental = None
        for pmid in matchPMID:
            if pmid[0] == 'Experimental studies':
                experimental = pmid[1]
            else:
                pubMed = pubMed + pmid[1] + "; "
        return (pubMed, experimental)

    def getModeling(self, variantText: str) -> str:
        '''
            Returns the Protein Modelling for a gene variant.
        '''
        matchModeling = re.search(
            r"modeling of protein sequence[\w\s\-,():.]*(is not expected to disrupt|is expected to disrupt)", variantText)
        if matchModeling is not None:
            modelingGroup = matchModeling.group(1)
            if modelingGroup == "is not expected to disrupt":
                modeling = "Not expected to disrupt"
            elif modelingGroup == "is expected to disrupt":
                modeling = "Expected to disrupt"
            else:
                modeling = "-"
        else:
            modeling = "-"
        return modeling

    def getFamilial(self):
        '''
            Returns the Familial VUS testing for a gene variant.
        '''
        clinicalSummary = re.search(
            r"Clinical summary.*Variant details", self.text, re.S)
        if clinicalSummary is not None:
            uncertainSigSearch = re.findall(
                r"Variant[s]? of Uncertain Significance, .* identified in (.*)\.", clinicalSummary.group())
            familialMatchList = re.findall(
                r"(Familial VUS testing is not offered\.|This variant qualifies for complimentary family studies as part of our VUS Resolution Program\.|Familial VUS testing is not recommended\.)", clinicalSummary.group())
            if len(uncertainSigSearch) == len(familialMatchList) and len(uncertainSigSearch) != 0:
                i = 0
                for var in self.variations:
                    if i < len(uncertainSigSearch) and uncertainSigSearch[i] == var['gene']:
                        if familialMatchList[i] == "Familial VUS testing is not offered.":
                            var['familial'] = "Not offered"
                        elif familialMatchList[i] == "This variant qualifies for complimentary family studies as part of our VUS Resolution Program.":
                            var['familial'] = "Qualifies for familial testing"
                        elif familialMatchList[i] == "Familial VUS testing is not recommended.":
                            var['familial'] = "Not recommended"
                        i += 1
            elif len(uncertainSigSearch) != 0:
                raise ValueError(
                    "Different number of uncertain significance variants and familial VUS")

    def getExtraVariantDetails(self, variantText: str, i: int):
        '''
            Gets the Extra Variant Details, including: Exon, Population, ClinVar ID, PubMed ID, and Protein Modelling

            Parameters:
                variantText: str - the text containing the extra variant details
                i: int - the number of the variant in the variations list
        '''
        # exon
        self.variations[i]['exon'] = self.getExon(variantText)

        # population
        self.variations[i]['population'] = self.getPopulation(variantText)

        # clinVar
        clinVar = self.getClinVar(variantText)
        if clinVar is None:
            self.variations[i]['clinVar'] = "-"
        else:
            self.variations[i]['clinVar'] = clinVar

        # pubMed and experimental
        pubMed, experimental = self.getPubMedAndExperimental(variantText)
        if pubMed != "":
            self.variations[i]['pubMed'] = pubMed[0:-2].replace(
                ",", ";").replace("\n", "")
        if experimental is not None:

            self.variations[i]['experimental'] = experimental.replace(
                ",", ";").replace("\n", "")

        # protein modeling
        self.variations[i]['proteinModeling'] = self.getModeling(variantText)

    def getGeneVariations(self, variantText: str, i: int):
        '''
            Gets the gene variations from the extracted text

            Parameters:
                variantText: str - the text containing the extra variant details
                i: int - the number of the variant in the variations list
        '''
        geneDetailsMatch = re.search(
            r".*(PATHOGENIC|Uncertain Significance|Benign [(]Pseudodeficiency allele[)]|Likely Pathogenic)", variantText)
        if geneDetailsMatch is not None:
            geneDetails = geneDetailsMatch.group().split(", ")
            if "Exons" in geneDetails[1]:
                self.variations[i]['gene'] = geneDetails[0]
                self.variations[i]['exon'] = re.search(
                    r"Exons ([\d\-]*)", geneDetails[1]).group(1)
                self.variations[i]['zygosity'] = geneDetails[2]
                self.variations[i]['classification'] = geneDetails[3]
                geneAndProtein = geneDetails[1].split(" (")
                self.variations[i]['geneVariant'] = geneAndProtein[0]
                self.variations[i]['proteinVariant'] = geneAndProtein[1][0:-1]
            else:
                # 0 = Gene, 1 = Exon, 2 = gene variation and protein change, 3 = zygosity, 4 = classification
                self.variations[i]['gene'] = geneDetails[0]
                self.variations[i]['exon'] = geneDetails[1]
                self.variations[i]['zygosity'] = geneDetails[3]
                self.variations[i]['classification'] = geneDetails[4]
                geneAndProtein = geneDetails[2].split(" (")
                self.variations[i]['geneVariant'] = geneAndProtein[0]
                self.variations[i]['proteinVariant'] = geneAndProtein[1][0:-1]
        else:
            print("\033[1;31mgetGeneVariations FAILED for " +
                  self.fileName + "\033[0m")

    def getVariantDetails(self):
        '''
        Gets the Extra Variant details from the report. This includes Exon, Population Database, ClinVar, PubMed, Protein Modeling, Experimental Studies
        '''
        variantDetailsMatch = re.search(
            r"Variant details.*Genes analyzed.*This table", self.text, re.S)
        if variantDetailsMatch is not None:
            variantDetailsTxt = variantDetailsMatch.group()
            for i in range(len(self.variations)-1):
                y = r"["+self.variations[i]['gene'] + r"]{" + str(len(self.variations[i]['gene'])) + r"}, [., A-Za-z0-9]*" + r"["+self.variations[i]['geneVariant'] + r"]{" + str(len(self.variations[i]['geneVariant'])) + r"}.*classified as.*" + \
                    r"["+self.variations[i]['classification'].title().replace(
                        "(Pseudodeficiency Allele)", "pseudodeficiency allele") + r"]{" + str(len(self.variations[i]['classification'])) + r"}.*" + r"["+self.variations[i+1]['gene'] + r"]{" + str(len(self.variations[i+1]['gene'])) + r"}, [., A-Za-z0-9]*[" + self.variations[i+1]['geneVariant'] + r"]{" + str(len(self.variations[i+1]['geneVariant'])) + r"}"
                variantText = re.search(y, variantDetailsTxt, re.S)
                if variantText is not None:
                    z = variantText.group()
                    self.getExtraVariantDetails(variantText.group(), i)
            y = r"["+self.variations[-1]['gene'] + r"]{" + str(len(self.variations[-1]['gene'])) + r"}, [., A-Za-z0-9]*" + r"["+self.variations[-1]['geneVariant'] + r"]{" + str(len(self.variations[-1]['geneVariant'])) + r"}.*classified as.*" + \
                r"["+self.variations[-1]['classification'].title().replace(
                "(Pseudodeficiency Allele)", "pseudodeficiency allele") + r"]{" + str(len(self.variations[-1]['classification'])) + r"}"

            variantText = re.search(y, variantDetailsTxt, re.S)
            if variantText is not None:
                self.getExtraVariantDetails(variantText.group(), -1)

    def getVariations(self):
        '''
        Gets the Gene Variations identified from the report.
        '''
        x = self.lines.index("GENE VARIANT ZYGOSITY VARIANT CLASSIFICATION")
        x = x + 1
        while "About this test" not in self.lines[x]:
            if len(self.lines[x]) > 0:
                vMatch = re.search(
                    r"([\w() *]*) (Deletion|c\.[\w><*?+]*) [(](Exons [\d\-]*|p\.[\w><*?+]*|Intronic)[)] ([\w]*) (PATHOGENIC|Uncertain Significance|Benign [(]Pseudodeficiency allele[)]|Likely Pathogenic)", self.lines[x])
                if vMatch is not None:
                    self.variations.append({"gene": vMatch.group(1), "geneTranscriptID": "", "geneVariant": vMatch.group(2), "proteinVariant": vMatch.group(3), "zygosity": vMatch.group(4), "classification": vMatch.group(5),
                                           "association": "", "exon": "", "population": "no frequency", "proteinModeling": "", "clinVar": "-", "pubMed": "-", "experimental": "-", "familial": "N/A"})
            x = x + 1

        # add associations to variations
        self.getAssociation()
        self.getVariantDetails()
        self.getFamilial()

    def getGeneList(self):
        '''
        Gets the list of genes that were analyzed and the relevant gene transcript from the report
        '''
        tables = []
        pageNumStart = findPageNum(self.fileName, "Genes analyzed\s")
        pageNumEnd = findPageNum(self.fileName, "Methods")
        for i in range(pageNumStart, pageNumEnd):
            tables.extend(tableExtract(self.fileName, i))
        for table in tables:
            for row in table:
                transcript = row[1]
                gene = row[0]
                if row != ["GENE", "TRANSCRIPT"]:
                    if "\n" in row[1]:
                        transcript = row[1].replace("\n", "")
                    if "\n" in row[0]:
                        gene = row[0].replace("\n", "")
                    self.geneList.append(
                        {"gene": gene, "transcript": transcript})

        self.getGeneTranscript()

    def getGeneTranscript(self):
        '''
        Locates and adds the relevant gene transcript to the gene variations.
        '''
        for var in self.variations:
            for row in self.geneList:
                if var['gene'] == row["gene"] or str(var['gene'] + "*") == row["gene"]:
                    var['geneTranscriptID'] = row["transcript"]


class InvitaeCarrier(InvitaeData):
    '''Class for data extracted from Invitae Carrier Screening Reports'''

    def __init__(self) -> None:
        super().__init__()

    def getData(self, fileName: str, text: str) -> None:
        '''
        Gets the data from the extracted text
        # Parameters:
        fileName: str - the name of the pdf file to extract text from
        '''
        self.fileName = fileName
        pageNum = findPageNum(fileName, "INVITAE CARRIER SCREEN RESULTS")
        self.text = detailedExtract(fileName, pageNum)
        self.lines = self.text.splitlines()

        # report ID
        self.getReportID()

        # lab
        self.getLab()

        # patient details
        self.getPatient()

        # report date
        self.getReportDate()

        # sample type
        self.getSampleType()

        # reason for testing
        self.getReasonForTests()

        # tests
        self.getTests()

        # result
        self.getResult()

        if self.result != "NEGATIVE":
            # variations
            self.getVariations()

        # geneList
        self.getGeneList()

    def getReportID(self):
        super().getReportID()

    def getLab(self):
        super().getLab()

    def getPatient(self):
        super().getPatient()

    def getReportDate(self):
        super().getReportDate()

    def getSampleType(self):
        super().getSampleType()

    def getReasonForTests(self):
        '''
        Gets the reason for testing from the report.
        '''
        matchReason = re.search(
            r"Test performed\s(.*)Invitae Comprehensive Carrier Screen", self.text)
        if matchReason is not None:
            self.reason = matchReason.group(1).strip()

    def getTests(self):
        '''
        Gets the list of tests conducted from the report.
        '''
        matchObj = re.search(r".* Carrier Screen", self.text)

        x = self.lines.index(matchObj.group())
        x = x + 1
        while "RESULT:" not in self.lines[x]:
            if len(self.lines[x]) > 0:
                self.tests.append(self.lines[x].replace(",", ""))
            x = x + 1

    def getResult(self):
        super().getResult()

    def getExon(self, variantText: str) -> str:
        return super().getExon(variantText)

    def getPopulation(self, variantText: str) -> str:
        return super().getPopulation(variantText)

    def getClinVar(self, variantText: str) -> str:
        return super().getClinVar(variantText)

    def getPubMedAndExperimental(self, variantText: str) -> tuple[str | None, str | None]:
        return super().getPubMedAndExperimental(variantText)

    def getModeling(self, variantText: str) -> str:
        return super().getModeling(variantText)

    def getGeneVariations(self, variantText: str, i: int):
        super().getGeneVariations(variantText, i)

    def getExtraVariantDetails(self, variantText: str, i: int):
        super().getExtraVariantDetails(variantText, i)

    def varDictSort(self, var):
        return var['gene']

    def getVariantDetails(self):
        '''
        Gets the Extra Variant details from the report. This includes Exon, Population Database, ClinVar, PubMed, Protein Modeling, Experimental Studies
        '''
        variantDetailsMatch = re.search(
            r"Variant details.*Residual risk.*This table", self.text, re.S)
        if variantDetailsMatch is not None:
            variantDetailsTxt = variantDetailsMatch.group()
            self.variations.sort(key=self.varDictSort)
            for i in range(len(self.variations)-1):
                y = r"["+self.variations[i]['gene'] + r"]{" + str(len(self.variations[i]['gene'])) + r"}, [., A-Za-z0-9]*" + r"["+self.variations[i]['geneVariant'] + \
                    r"]{" + str(len(self.variations[i]['geneVariant'])) + r"}.*[" + self.variations[i+1]['gene'] + r"]{" + str(len(self.variations[i+1]['gene'])) + \
                    r"}, [., A-Za-z0-9]*[" + self.variations[i+1]['geneVariant'] + \
                    r"]{" + \
                    str(len(self.variations[i+1]['geneVariant'])) + r"}"
                variantText = re.search(y, variantDetailsTxt, re.S)
                if variantText is not None:
                    self.getGeneVariations(variantText.group(), i)
                    self.getExtraVariantDetails(variantText.group(), i)

            y = r"["+self.variations[-1]['gene'] + r"]{" + str(len(self.variations[-1]['gene'])) + r"}, [., A-Za-z0-9]*" + r"[" + \
                self.variations[-1]['geneVariant'] + r"]{" + str(
                    len(self.variations[-1]['geneVariant'])) + r"}.*Residual risk.*This table"

            variantText = re.search(y, variantDetailsTxt, re.S)
            if variantText is not None:
                self.getGeneVariations(variantText.group(), -1)
                self.getExtraVariantDetails(variantText.group(), -1)

    def printString(self, row: list, up: int) -> str:
        upto = row.index(row[up])
        txt = ""
        for i in range(0, upto):
            txt = txt + row[i] + " "
        return txt[0:-1]

    def getVariations(self):
        '''
        Gets the Gene Variations identified from the report.
        '''
        try:
            x = self.lines.index("RESULTS GENE VARIANT(S) INHERITANCE")
        except ValueError as e:
            x = self.lines.index(
                "RESULTS GENE VARIANT(S) INHERITANCE PARTNER TESTING")

        x = x + 2
        while "Next steps" not in self.lines[x]:
            if len(self.lines[x]) > 0:
                vMatch = re.search(
                    r"([\w*:()\- ]*) ([\w() *]*) (Deletion|c\.[\w><*?+]*) [(](Exons [\d\-]*|p\.[\w><*?+]*|Intronic)[)] ([\w ]*) (Yes|No)", self.lines[x])

                if vMatch is not None:
                    self.variations.append({"gene": vMatch.group(2), "geneTranscriptID": "", "geneVariant": vMatch.group(3), "proteinVariant": vMatch.group(4), "zygosity": "", "classification": "", "exon": "",
                                           "population": "no frequency", "proteinModeling": "", "clinVar": "-", "pubMed": "-", "experimental": "-", "inheritance": vMatch.group(5), "partnerTest": vMatch.group(6), "result": vMatch.group(1)})
            x = x + 1

        self.getVariantDetails()

    def getGeneList(self):
        if re.search(r"Genes analyzed", self.text) is not None:
            super().getGeneList()
        else:
            genesMatch = re.search(
                r"Methods.*The.*following.*transcripts.*in.*the.*report: (.*[)][.]).*Variants.*of.*uncertain.*significance", self.text, re.S)
            if genesMatch is not None:
                genesMatch = re.sub(
                    r"Laboratory Director:.*INVITAE CARRIER SCREEN RESULTS", "", genesMatch.group(1), flags=re.S)
                genesAndTranscripts = genesMatch.split(",")
                for gAndT in genesAndTranscripts:
                    gAndT = gAndT.strip()
                    if " " in gAndT:
                        gAndTList = gAndT.split(" ")
                    elif "\n" in gAndT:
                        gAndTList = gAndT.split("\n")
                    gene = gAndTList[0]
                    transcript = gAndTList[1].replace("(", "").replace(")", "")
                    self.geneList.append(
                        {"gene": gene, "transcript": transcript})
                self.getGeneTranscript()

    def getGeneTranscript(self):
        super().getGeneTranscript()


class InvitaeFamilial(InvitaeData):
    '''Class for data extracted from Invitae Familial Variant Testing Reports'''

    def __init__(self) -> None:
        super().__init__()

    def getData(self, fileName: str, text: str) -> None:
        '''
        Gets the data from the extracted text
        # Parameters:
        fileName: str - the name of the pdf file to extract text from
        '''
        self.fileName = fileName
        self.text = text
        self.lines = self.text.splitlines()

        # report ID
        self.getReportID()

        # lab
        self.getLab()

        # patient details
        self.getPatient()

        # report date
        self.getReportDate()

        # sample type
        self.getSampleType()

        # reason for testing
        self.getReasonForTests()

        # tests
        self.getTests()

        # result
        self.getResult()

        if self.result != "NEGATIVE":
            # variations
            self.getVariations()

        # geneList
        self.getGeneList()

    def getReportID(self):
        super().getReportID()

    def getLab(self):
        super().getLab()

    def getPatient(self):
        super().getPatient()

    def getReportDate(self):
        super().getReportDate()

    def getSampleType(self):
        super().getSampleType()

    def getReasonForTests(self):
        super().getReasonForTests()

    def getTests(self):
        self.tests.append("Familial Variant Testing")

    def getResult(self):
        super().getResult()

    def getExon(self, variantText: str) -> str:
        return super().getExon(variantText)

    def getPopulation(self, variantText: str) -> str:
        return super().getPopulation(variantText)

    def getClinVar(self, variantText: str) -> str:
        return super().getClinVar(variantText)

    def getPubMedAndExperimental(self, variantText: str) -> tuple[str | None, str | None]:
        return super().getPubMedAndExperimental(variantText)

    def getModeling(self, variantText: str) -> str:
        return super().getModeling(variantText)

    def getGeneVariations(self, variantText: str, i: int):
        super().getGeneVariations(variantText, i)

    def getExtraVariantDetails(self, variantText: str, i: int):
        super().getExtraVariantDetails(variantText, i)

    def getVariantDetails(self):
        super().getVariantDetails()

    def getVariations(self):
        '''
        Gets the Gene Variations identified from the report.
        '''
        x = self.lines.index("GENE VARIANT ZYGOSITY VARIANT CLASSIFICATION")
        x = x + 1
        while "About this test" not in self.lines[x]:
            if len(self.lines[x]) > 0:
                vMatch = re.search(
                    r"([\w() *]*) (Deletion|c\.[\w><*?+]*) [(](Exons [\d\-]*|p\.[\w><*?+]*|Intronic)[)] ([\w]*) (PATHOGENIC|Uncertain Significance|Benign [(]Pseudodeficiency allele[)]|Likely Pathogenic)", self.lines[x])
                if vMatch is not None:
                    self.variations.append({"gene": vMatch.group(1), "geneTranscriptID": "", "geneVariant": vMatch.group(2), "proteinVariant": vMatch.group(3), "zygosity": vMatch.group(4), "classification": vMatch.group(5),
                                           "association": "", "exon": "", "population": "no frequency", "proteinModeling": "", "clinVar": "-", "pubMed": "-", "experimental": "-", "familial": "N/A"})
            x = x + 1

        # add associations to variations
        self.getAssociation()
        self.getVariantDetails()

    def getGeneList(self):
        super().getGeneList()

    def getGeneTranscript(self):
        super().getGeneTranscript()
