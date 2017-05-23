import csv
from testdata import PROCEDURES_FILE


class Procedure(object):
    """Create instances of Procedure; also maintains complete procedure lists by patient id"""

    procedures = {} # Dictionary of procedure lists, by patient id

    @classmethod
    def load(cls):
        """Loads patient Procedure observations"""

        # Loop through procedures and build patient procedure lists:
        items = csv.reader(file(PROCEDURES_FILE, 'U'), dialect='excel-tab')
        header = items.next()
        for item in items:
            cls(dict(zip(header, item))) # Create a procedure instance

    def __init__(self, p):
        self.id     = p['ID']
        self.pid    = p['PID']
        self.date   = p['DATE']
        self.snomed = p['SNOMED']
        self.name   = p['NAME']
        self.notes  = p['NOTES']

        # Append procedure to the patient's procedure list:
        if self.pid in  self.__class__.procedures:
            self.__class__.procedures[self.pid].append(self)
        else:
            self.__class__.procedures[self.pid] = [self]

    def toJSON(self, prefix=""):
        """Builds and returns the Procedure JSON"""

        if prefix:
            prefix += "-"

        out = {
            "request": {
                "method": "PUT",
                "url": "Procedure/" + prefix + "Procedure-" + self.id
            },
            "resource": {
                "id"          : prefix + "Procedure-" + self.id,
                "resourceType": "Procedure",
                "status"      : "completed",
                "subject"     : {
                    "reference": "Patient/" + prefix + self.pid
                },
                "text": {
                    "status": "generated",
                    "div": '<div xmlns="http://www.w3.org/1999/xhtml">%s</div>' % self.name
                },
                "performedDateTime": self.date,
                "code": {
                    "coding": [
                        {
                            "system" : "http://snomed.info/sct",
                            "code"   : self.snomed,
                            "display": self.name
                        }
                    ],
                    "text": self.name
                }
            }
        }

        if self.notes:
            out["resource"]["note"] = [
                {
                    "text": self.notes
                }
            ]

        return out
