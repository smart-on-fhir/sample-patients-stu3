import csv
from testdata import REFILLS_FILE


class Refill(object):
    """Create instances of a med refill; also maintains complete refills lists by patient id"""

    refills = {} # Dictionary of refills, by patient id

    @classmethod
    def load(cls):
        """Loads med refills"""

        # Loop through refills and build med refill list:
        refills = csv.reader(file(REFILLS_FILE,'U'),dialect='excel-tab')
        header = refills.next()
        for refill in refills:
            cls(dict(zip(header, refill))) # Create a refill instance

    @classmethod
    def refill_list(cls,pid,rxn):
        """Return a refill history for patient, pid, and for med, rxn"""
        refills = {}
        if not pid in cls.refills:
            return []
        for med in cls.refills[pid]:
            if int(med.q) and med.rxn==rxn: # non-zero quantity
                refills[rxn+med.date]=med # and only one rnx per day
        return refills.values()

    def __init__(self,p):
        self.id   = p['ID']
        self.pid  = p['PID']
        self.date = p['DATE']
        self.rxn  = p['RXN']
        self.days = p['DAYS']
        self.q    = p['Q']

        # Append refill to the refills list:
        if self.pid in  self.__class__.refills:
            self.__class__.refills[self.pid].append(self)
        else:
            self.__class__.refills[self.pid] = [self]

    def toJSON(self, med, prefix=""):
        """Builds and returns the MedicationDispense JSON"""

        if prefix:
            prefix += "-"

        out = {
            "request": {
                "method": "PUT",
                "url": "MedicationDispense/" + prefix + "MedicationDispense-" + self.id
            },
            "resource": {
                "id"          : prefix + "MedicationDispense-" + self.id,
                "resourceType": "MedicationDispense",
                "subject"     : {
                    "reference": "Patient/" + prefix + self.pid
                },
                "text": {
                    "status": "generated",
                    "div": '<div xmlns="http://www.w3.org/1999/xhtml">' +
                           'Dispensed %s tablets = %s day supply of %s</div>'
                           % (self.q, self.days, med.name)
                },
                "status": "completed",

                "whenHandedOver": self.date,

                # Identifies the medication being requested. This is a link to a
                # resource that represents the medication which may be the details
                # of the medication or simply an attribute carrying a code that
                # identifies the medication from a known list of medications.
                "medicationCodeableConcept": {
                    "coding": [
                        {
                            "system" : "http://www.nlm.nih.gov/research/umls/rxnorm",
                            "code"   : self.rxn,
                            "display": med.name
                        }
                    ],
                    "text": med.name
                },

                "authorizingPrescription": [
                    {
                        "reference": "MedicationRequest/" + prefix + "MedicationRequest-" + med.id
                    }
                ],

                "quantity": {
                    "value" : float(self.q),
                    "unit"  : "tablets",
                    "system": "http://unitsofmeasure.org",
                    "code"  : "{tablets}"
                },

                "daysSupply": {
                    "value" : int(self.days),
                    "unit"  : "days",
                    "system": "http://unitsofmeasure.org",
                    "code"  : "d"
                }
            }
        }

        return out
