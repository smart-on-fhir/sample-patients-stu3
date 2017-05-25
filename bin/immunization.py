import csv
from testdata import IMMUNIZATIONS_FILE


class Immunization(object):
    """Create instances of Immunization list entries; also maintains complete Immunization lists by patient id"""

    immunizations = {} # Dictionary of Immunization lists, by patient id

    @classmethod
    def load(cls):
        """Loads patient Immunization observations"""
        # Loop through Immunizations and build patient Immunizations lists:
        rows = csv.reader(file(IMMUNIZATIONS_FILE,'U'), dialect='excel-tab')
        header = rows.next()
        for i in rows:
            cls(dict(zip(header, i))) # Create a Immunization instance (saved in Immunizations.immunizations)

    def __init__(self, m):
        pid = m["PID"]
        self.data = m

        # Append Immunization to the patient's Immunization list:
        if pid in  self.__class__.immunizations:
            self.__class__.immunizations[pid].append(self)
        else:
            self.__class__.immunizations[pid] = [self]


    def toJSON(self, prefix=""):
        """Builds and returns the Immunization JSON"""

        data = self.data

        if prefix:
            prefix += "-"

        cvx_system, cvx_id = data["CVX"].rsplit("cvx", 1)
        cvx_system += "cvx"

        out = {
            "request": {
                "method": "PUT",
                "url": "Immunization/" + prefix + "Immunization-" + data["ID"]
            },
            "resource": {
                "id"          : prefix + "Immunization-" + data["ID"],
                "resourceType": "Immunization",
                "status"      : "completed",
                "primarySource": True,
                "patient"     : {
                    "reference": "Patient/" + prefix + data["PID"]
                },
                "text": {
                    "status": "generated",
                    "div": '<div xmlns="http://www.w3.org/1999/xhtml">%s</div>'%data["CVX_title"]
                },
                "date": data["date"],
                "vaccineCode": {
                    "coding": [
                        {
                            "system" : cvx_system,
                            "code"   : cvx_id,
                            "display": data["CVX_title"]
                        }
                    ],
                    "text": data["CVX_title"]
                }
            }
        }

        if data["administration_status"] == 'http://smarthealthit.org/terms/codes/ImmunizationAdministrationStatus#doseGiven':
            out["resource"]["notGiven"] = False
        elif data["administration_status"] == 'http://smarthealthit.org/terms/codes/ImmunizationAdministrationStatus#notAdministered':
            out["resource"]["notGiven"] = True
            if data["refusal_reason"] == 'http://smartplatforms.org/terms/codes/ImmunizationRefusalReason#allergy':
                out["resource"]["explanation"] = {
                    "reasonNotGiven": [
                        {
                            "coding": [
                                {
                                    "system" : "http://smarthealthit.org/terms/codes/ImmunizationRefusalReason#",
                                    "code"   : "allergy",
                                    "display": "Allergy to vaccine/vaccine components, or allergy to eggs"
                                }
                            ],
                            "text": "Allergy to vaccine/vaccine components, or allergy to eggs"
                        }
                    ]
                }
            elif data["refusal_reason"] == 'http://smarthealthit.org/terms/codes/ImmunizationRefusalReason#documentedImmunityOrPreviousDisease':
                out["resource"]["explanation"] = {
                    "reasonNotGiven": [
                        {
                            "coding": [
                                {
                                    "system" : "http://smarthealthit.org/terms/codes/ImmunizationRefusalReason#",
                                    "code"   : "documentedImmunityOrPreviousDisease",
                                    "display": "Documented immunity or previous disease"
                                }
                            ],
                            "text": "Documented immunity or previous disease"
                        }
                    ]
                }
            elif data["refusal_reason"] == 'http://smarthealthit.org/terms/codes/ImmunizationRefusalReason#notIndicatedPerGuidelines':
                out["resource"]["explanation"] = {
                    "reasonNotGiven": [
                        {
                            "coding": [
                                {
                                    "system" : "http://smarthealthit.org/terms/codes/ImmunizationRefusalReason#",
                                    "code"   : "notIndicatedPerGuidelines",
                                    "display": "Not indicated per guidelines"
                                }
                            ],
                            "text": "Not indicated per guidelines"
                        }
                    ]
                }

        return out
