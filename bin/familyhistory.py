import csv
from testdata import FAMILYHISTORY_FILE


class FamilyHistory(object):
    """Create instances of FamilyHistory and maintain FamilyHistory lists by patient ID"""

    familyHistories = {} # Dictionary of FamilyHistory lists by patient ID

    @classmethod
    def load(cls):
        """Loads patient family histories"""

        # Loop through family histories and build patient FamilyHistory lists:
        histories = csv.reader(file(FAMILYHISTORY_FILE,'U'), dialect='excel-tab')
        header = histories.next()
        for history in histories:
            cls(dict(zip(header, history))) # Create a FamilyHistory instance

    def __init__(self,fh):
        self.id            = fh['ID']
        self.patientid     = fh['PID']
        self.relativecode  = fh['RELATIVE_CODE']
        self.relativetitle = fh['RELATIVE_TITLE']
        self.dateofbirth   = fh['DATE_OF_BIRTH']
        self.dateofdeath   = fh['DATE_OF_DEATH']
        self.problemcode   = fh['PROBLEM_CODE']
        self.problemtitle  = fh['PROBLEM_TITLE']
        self.heightcm      = fh['HEIGHT_CM']

        # Append FamilyHistory to the patient's list:
        if self.patientid in self.__class__.familyHistories:
            self.__class__.familyHistories[self.patientid].append(self)
        else:
            self.__class__.familyHistories[self.patientid] = [self]

    def asTabString(self):
        """Returns a tab-separated string representation of a FamilyHistory"""
        dl = [
            self.patientid,
            self.relativecode,
            self.relativetitle,
            self.dateofbirth,
            self.dateofdeath,
            self.problemcode,
            self.problemtitle,
            self.heightcm
        ]
        s = ""
        for v in dl:
            s += "%s\t"%v
        return s[0:-1] # Throw away the last tab

    def toJSON(self, prefix=""):

        if prefix:
            prefix += "-"

        out = {
            "request": {
                "method": "PUT",
                "url": "FamilyMemberHistory/" + prefix + "FamilyMemberHistory-" + self.id
            },
            "resource": {
                "id"          : prefix + "FamilyMemberHistory-" + self.id,
                "resourceType": "FamilyMemberHistory",
                "status"      : "completed",
                "patient"     : {
                    "reference": "Patient/" + prefix + self.patientid
                },
                "text": {
                    "status": "generated",
                    "div": '<div xmlns="http://www.w3.org/1999/xhtml">' +
                           "Data on patient's %s</div>" % self.relativetitle
                }
            }
        }


        if self.relativecode == '66839005':
            out["resource"]["relationship"]= {
                "coding": [
                    {
                        "system" : "http://hl7.org/fhir/v3/RoleCode",
                        "code"   : "FTH",
                        "display": "father"
                    }
                ],
                "text": "Father"
            }

        elif self.relativecode == '72705000':
            out["resource"]["relationship"] = {
                "coding": [
                    {
                        "system" : "http://hl7.org/fhir/v3/RoleCode",
                        "code"   : "MTH",
                        "display": "mother"
                    }
                ],
                "text": "Mother"
            }

        elif self.relativecode == '27733009':
            out["resource"]["relationship"] = {
                "coding": [
                    {
                        "system" : "http://hl7.org/fhir/v3/RoleCode",
                        "code"   : "SIS",
                        "display": "sister"
                    }
                ],
                "text": "Sister"
            }

        elif self.relativecode == '70924004':
            out["resource"]["relationship"] = {
                "coding": [
                    {
                        "system" : "http://hl7.org/fhir/v3/RoleCode",
                        "code"   : "BRO",
                        "display": "brother"
                    }
                ],
                "text": "Brother"
            }

        elif self.relativecode == '34871008':
            out["resource"]["relationship"] = {
                "coding": [
                    {
                        "system" : "http://hl7.org/fhir/v3/RoleCode",
                        "code"   : "GRFTH",
                        "display": "grandfather"
                    }
                ],
                "text": "Grandfather"
            }

        elif self.relativecode == '113157001':
            out["resource"]["relationship"] = {
                "coding": [
                    {
                        "system" : "http://hl7.org/fhir/v3/RoleCode",
                        "code"   : "GRMTH",
                        "display": "grandmother"
                    }
                ],
                "text": "Grandmother"
            }

        if self.heightcm:
            out["resource"]["extension"] = [
                {
                    "url": "http://fhir-registry.smarthealthit.org/StructureDefinition/family-history#height",
                    "valueQuantity": {
                        "value" : float(self.heightcm),
                        "unit"  : "centimeters",
                        "system": "http://unitsofmeasure.org",
                        "code"  : "cm"
                    }
                }
            ]

        if self.dateofbirth:
            out["resource"]["bornDate"] = self.dateofbirth

        if self.dateofdeath:
            out["resource"]["deceasedDate"] = self.dateofdeath

        if self.problemcode:
            out["resource"]["condition"] = [
                {
                    "code": {
                        "coding": [
                            {
                                "system": "http://snomed.info/sct",
                                "code": self.problemcode,
                                "display": self.problemtitle
                            }
                        ],
                        "text": self.problemtitle
                    }
                }
            ]

        return out
