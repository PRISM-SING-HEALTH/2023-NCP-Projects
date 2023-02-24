'''
/*******************************************************************
 *  File Name: PEDClass.py                                         *
 *  Purpose: class for holding PED structure                       *
 *  Author: Marcus Francis Cozza - 20595722@student.curtin.edu.au  *
 *  Date: 30/01/2023                                               *
 *  Version: 1.1                                                   *
 *  Change Log:                                                    *
 *      > 1.1 - Initialise Program 30/01/2023                      *
 *******************************************************************/
 '''
class PED:
    def __init__(self, familyID, individualID, paternalID, maternalID, sex, phenotype):
        self.familyID = familyID
        self.individualID = individualID
        self.paternalID = paternalID
        self.maternalID = maternalID
        self.sex = sex
        self.phenotype = self._is_phenotype_valid(phenotype)

        # set relationship status to empty
        self.relationship = ""

    # SETTERS:

    def addRelationship(self, relationship):
        self.relationship = relationship

    # GETTERS
    def getRelationship(self):
        return self.relationship

    # HELPER FUNCTIONS
    # format string output
    def __str__(self):
        return("FamID:" + str(self.familyID) + " individualID:" + str(self.individualID) + " paternalID:" + str(self.paternalID) + " maternalID:" + str(self.maternalID) + " Sex:" + str(self.sex) + " Phenotype:" + str(self.phenotype))

    # valid phenotype input
    def _is_phenotype_valid(self, phenotype):
        if not(phenotype == 9 or phenotype == 0 or phenotype == 1 or phenotype == 2):
            raise ValueError("Invalid Phenotype")
        return phenotype



