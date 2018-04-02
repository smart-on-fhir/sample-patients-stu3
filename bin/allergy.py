import csv
from testdata import ALLERGIES_FILE


SYSTEMS = {
    "SNOMED": "http://snomed.info/sct",
    "NDFRT" : "http://rxnav.nlm.nih.gov/REST/Ndfrt", #"http://hl7.org/fhir/ndfrt",
    "UNII"  : "http://fda.gov/UNII/", #"http://fdasis.nlm.nih.gov",
    "RXNORM": "http://www.nlm.nih.gov/research/umls/rxnorm" #"http://www.nlm.nih.gov/research/umls/rxnorm"
}

class Allergy(object):
    """Create instances of Allergy; also maintains complete allergy lists by patient id"""

    allergies = {} # Dictionary of allergy lists, by patient id

    @classmethod
    def load(cls):
        """Loads patient Allergy observations"""

        # Loop through allergies and build patient allergy lists:
        rows = csv.reader(file(ALLERGIES_FILE,'U'),dialect='excel-tab')
        header = rows.next()
        for row in rows:
            cls(dict(zip(header, row))) # Create a allergy instance

    def __init__(self,p):
        self.id        = p['ID']
        self.pid       = p['PID']
        self.statement = p['STATEMENT']
        self.type      = p['TYPE']
        self.allergen  = p['ALLERGEN']
        self.system    = SYSTEMS[p['SYSTEM']]
        self.code      = p['CODE']
        self.start     = p['START_DATE']
        self.end       = p['END_DATE']
        self.reaction  = p['REACTION']
        self.snomed    = p['SNOMED']
        self.severity  = p['SEVERITY']

        if self.severity == 'mild':
            self.severity_code = 255604002
        elif self.severity == 'moderate':
            self.severity_code = 6736007
        elif self.severity == 'severe':
            self.severity_code = 24484000
        elif self.severity == 'life threatening':
            self.severity_code = 442452003
        elif self.severity == 'fatal':
            self.severity_code = 399166001

        # These two should be set later
        self.typeDescription = None
        self.criticality     = None

        # Append allergy to the patient's allergy list:
        if self.pid in  self.__class__.allergies:
            self.__class__.allergies[self.pid].append(self)
        else:
            self.__class__.allergies[self.pid] = [self]

    def toJSON(self, prefix=""):
        """Builds and returns the AllergyIntolerance JSON"""
        allergyString = "Sensitivity to "
        if self.allergen.startswith("No known"):
            allergyString = self.allergen
        else:
            allergyString += self.allergen

        if prefix:
            prefix += "-"

        out = {
            "request": {
                "method": "PUT",
                "url": "AllergyIntolerance/" + prefix + "AllergyIntolerance-" + self.id
            },
            "resource": {
                "id"          : prefix + "AllergyIntolerance-" + self.id,
                "resourceType": "AllergyIntolerance",
                "text": {
                    "status": "generated",
                    "div": '<div xmlns="http://www.w3.org/1999/xhtml">%s</div>'
                           % allergyString
                },
                "assertedDate": self.start,
                "verificationStatus": "confirmed",
                "clinicalStatus": "resolved" if self.end else "active",
                "patient": {
                    "reference": "Patient/" + prefix + self.pid
                },
                "code": {
                    "coding": [
                        {
                            "system" : self.system,
                            "code"   : self.code,
                            "display": self.allergen
                        }
                    ],
                    "text": self.allergen
                }
            }
        }

        if self.typeDescription:
            out["resource"]["category"] = self.typeDescription

        if self.criticality:
            out["resource"]["criticality"] = self.criticality

        if self.reaction:
            out["resource"]["reaction"] = [
                {
                    "manifestation": [
                        {
                            "coding": [
                                {
                                    "system" : "http://snomed.info/sct",
                                    "code"   : self.snomed,
                                    "display": self.reaction
                                }
                            ],
                            "text": self.reaction
                        }
                    ]
                }
            ]

            if self.severity:
                out["resource"]["reaction"][0]["severity"] = self.severity

        return out
