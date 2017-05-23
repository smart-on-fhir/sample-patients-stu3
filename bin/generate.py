import argparse
# import sys
import os
from patient       import Patient
from vitals        import VitalSigns
from lab           import Lab
from socialhistory import SocialHistory
from familyhistory import FamilyHistory
from immunization  import Immunization
from procedure     import Procedure
from condition     import Condition
from med           import Med
from refill        import Refill
from document      import Document
from allergy       import Allergy
from clinicalnote  import ClinicalNote
from practitioner  import Practitioner

def initData():
    """Load data and mappings from Raw data files and mapping files"""
    Patient.load()
    VitalSigns.load()
    Lab.load()
    Procedure.load()
    Immunization.load()
    FamilyHistory.load()
    SocialHistory.load()
    Condition.load()
    Med.load()
    Refill.load()
    Document.load()
    Allergy.load()
    ClinicalNote.load()
    Practitioner.load()

def displayPatientSummary(pid):
    """writes a patient summary to stdout"""
    if not pid in Patient.mpi: return
    print Patient.mpi[pid].asTabString()
    print "PROBLEMS: ",
    # if not pid in Problem.problems: print "None",
    # else: 
    #     for prob in Problem.problems[pid]: print prob.name+"; ",
    # print "\nMEDICATIONS: ",
    # if not pid in Med.meds: print "None",
    # else:
    #     for med in Med.meds[pid]: 
    #         print med.name+"{%d}; "%len(Refill.refill_list(pid,med.rxn)),
    # print "\nLABS: ",
    # if not pid in Lab.results: print "None",
    # else:
    #     print "%d results"%len(Lab.results[pid])
    print "\n"

if __name__ == '__main__':

    # Create the parser
    PARSER = argparse.ArgumentParser(description='SMART on FHIR Test Data Generator')
    GROUP = PARSER.add_mutually_exclusive_group()
    GROUP.add_argument(
        '--summary',
        metavar='pid',
        nargs='?',
        const="all",
        help="displays patient summary (default is 'all')"
    )
    GROUP.add_argument(
        '--write-fhir',
        dest='writeFHIR',
        metavar='dir',
        nargs='?',
        const='.',
        help="writes patient XML files to an FHIR sample data directory dir (default='.')"
    )
    PARSER.add_argument(
        '--id-prefix',
        dest='prefix',
        metavar='id_prefix',
        nargs='?',
        const='',
        help="adds the given prefix to the FHIR resource IDs (default=none)"
    )
    PARSER.add_argument(
        '--base-url',
        dest='baseURL',
        metavar='base_url',
        nargs='?',
        const='',
        help="uses the supplied URL base to generate absolute resource references (default='')"
    )

    ARGS = PARSER.parse_args()

    # print summary ------------------------------------------------------------
    if ARGS.summary:
        initData()

        if ARGS.summary == "all": # Print a summary of all patients
            for pid in Patient.mpi:
                displayPatientSummary(pid)
        else: # Just print a single patient's summary
            displayPatientSummary(ARGS.summary)
        PARSER.exit()

    if ARGS.writeFHIR:
        import fhir
        print "Writing files to %s:"%ARGS.writeFHIR
        initData()
        path = ARGS.writeFHIR
        baseURL = ARGS.baseURL or ""

        if not os.path.exists(path):
            PARSER.error("Invalid path: '%s'.Path must already exist."%path)

        if ARGS.prefix:
            prefix = ARGS.prefix
        else:
            prefix = None

        for pid in Patient.mpi:
            fhir.FHIRSamplePatient(pid, path, baseURL).writePatientData(prefix)
            # Show progress with '.' characters
            # print "%s %s - %s" % (baseURL, prefix, pid)
            # sys.stdout.flush()
        # PARSER.exit(0, "\nDone writing %d patient FHIR files!\n"%len(Patient.mpi))
        PARSER.exit()

    PARSER.error("No arguments given")
