"""Module for importing code mapping files: only LOINC required for now"""
from testdata import LOINC_FILE
import argparse
import csv

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

if __name__== '__main__':

    PARSER = argparse.ArgumentParser(description='Test Data Codes Module')
    GROUP = PARSER.add_mutually_exclusive_group()
    GROUP.add_argument(
        '--loinc',
        nargs='?',
        const='25324-5',
        help='Display info for a LOINC code (default = 25324-5)'
    )
    ARGS = PARSER.parse_args()

    Loinc.load([ARGS.loinc])

    if not ARGS.loinc in Loinc.info:
        PARSER.error("LOINC code %s not found"%ARGS.loinc)
    else:
        L = Loinc.info[ARGS.loinc]
        print L.code, L.name, L.scale, L.ucum, L.system
