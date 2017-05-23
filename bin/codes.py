"""Module for importing code mapping files: only LOINC required for now"""
import csv
from testdata import LOINC_FILE


class Loinc(object):
    """Creates loinc code instances and holds global loinc dictionary"""
    info = {} # Dictionary of loinc code information

    @classmethod
    def load(cls,loinc_list):
        """Loads code_info dictionary for LOINC codes in loinc_list"""

        # Open data file and read in the first (header) record
        loincs = csv.reader(file(LOINC_FILE,'U'),dialect='excel-tab')
        header = loincs.next()
        # Now, read in loinc codes:
        for loinc in loincs:
            l = dict(zip(header, loinc)) # build row dictionary of values
            if l['LOINC_NUM'] in loinc_list: # See if we're interested in this code
                cls(l) # If so, create a loinc instance and store it in Loinc.info

    def __init__(self,l):
        """Creates a loinc instance and save it in Loinc.info"""
        self.code = l['LOINC_NUM']
        self.name= l['SHORTNAME']
        self.system = l['SYSTEM']
        self.scale = l['SCALE_TYP']
        self.ucum = l['EXAMPLE_UCUM_UNITS']
        self.source= l['SOURCE']
        self.units_required = l['UNITSREQUIRED']
        self.__class__.info[self.code]=self
