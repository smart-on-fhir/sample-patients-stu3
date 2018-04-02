import csv
from testdata import SOCIALHISTORY_FILE
from testdata import rndDate
from patient import Patient

SMOKINGCODES = {
    '428041000124106': 'Current some day smoker',
    '266919005'      : 'Never smoker',
    '449868002'      : 'Current every day smoker',
    '266927001'      : 'Unknown if ever smoked',
    '8517006'        : 'Former smoker'
}

class SocialHistory(object):
    """Create instances of SocialHistory; also maintains socialHistory by patient id"""

    socialHistories = {} # Dictionary of socialHistory by patient ID

    @classmethod
    def load(cls):
        """Loads patient SocialHistory"""

        # Loop through socialHistories and build patient socialHistory lists:
        histories = csv.reader(file(SOCIALHISTORY_FILE, 'U'), dialect='excel-tab')
        header = histories.next()
        for history in histories:
            cls(dict(zip(header, history))) # Create a socialHistory instance

    def __init__(self, p):
        self.pid = p['PID']
        self.id  = p['ID']
        self.smokingStatusCode = p['SMOKINGSTATUSCODE']
        self.smokingStatusText = SMOKINGCODES[self.smokingStatusCode]

        # Append socialHistory to the patient's socialHistory list:
        if self.pid in  self.__class__.socialHistories:
            raise "Found >1 socialHistory for a patient"
        else:
            self.__class__.socialHistories[self.pid] = self

    def toJSON(self, prefix=""):

        if prefix:
            prefix += "-"

        patient = Patient.mpi[self.pid]

        return {
            "request": {
                "method": "PUT",
                "url": "Observation/" + prefix + "smokingstatus-" + self.id
            },
            "resource": {
                "id": prefix + "smokingstatus-" + self.id,
                "resourceType": "Observation",
                "status": "final",
                "identifier": [
                    {
                        "use"   : "official",
                        "system": "http://www.bmc.nl/zorgportal/identifiers/observations",
                        "value" : prefix + self.id
                    }
                ],
                "text": {
                    "status": "generated",
                    "div": '<div xmlns="http://www.w3.org/1999/xhtml">' +
                           'Tobacco smoking status: %s</div>'%self.smokingStatusText
                },
                "performer": [
                    {
                        "reference": "Practitioner/" + prefix + "Practitioner-" + patient.gp
                    }
                ],
                "effectiveDateTime": rndDate(2016).isoformat(),
                "code": {
                    "coding": [
                        {
                            "system" : "http://loinc.org",
                            "code"   : "72166-2",
                            "display": "Tobacco smoking status"
                        }
                    ],
                    "text": "Tobacco smoking status"
                },
                "subject": {
                    "reference": "Patient/" + prefix + self.pid
                },
                "category": [
                    {
                        "coding": [
                            {
                                "system" : "http://hl7.org/fhir/observation-category",
                                "code"   : "social-history",
                                "display": "Social History"
                            }
                        ],
                        "text": "Social History"
                    }
                ],
                "valueCodeableConcept": {
                    "coding": [
                        {
                            "system" : "http://snomed.info/sct",
                            "code"   : self.smokingStatusCode,
                            "display": self.smokingStatusText
                        }
                    ],
                    "text": self.smokingStatusText
                }
            }
        }
