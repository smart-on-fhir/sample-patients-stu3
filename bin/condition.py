import csv
from testdata import PROBLEMS_FILE


class Condition(object):
    """Create instances of Problem; also maintains complete condition lists by patient id"""

    conditions = {} # Dictionary of condition lists, by patient id

    @classmethod
    def load(cls):
        """Loads patient condition observations"""

        # Loop through problems and build patient problem lists:
        rows = csv.reader(file(PROBLEMS_FILE,'U'), dialect='excel-tab')
        header = rows.next()
        for row in rows:
            cls(dict(zip(header, row))) # Create a problem instance

    def __init__(self,p):
        self.id     = p['ID']
        self.pid    = p['PID']
        self.start  = p['START_DATE']
        self.end    = p['END_DATE']
        self.snomed = p['SNOMED']
        self.name   = p['NAME']

        # Append problem to the patient's problem list:
        if self.pid in self.__class__.conditions:
            self.__class__.conditions[self.pid].append(self)
        else:
            self.__class__.conditions[self.pid] = [self]

    def toJSON(self, prefix=""):
        """Builds and returns the Condition JSON"""

        if prefix:
            prefix += "-"

        out = {
            "request": {
                "method": "PUT",
                "url": "Condition/" + prefix + "Condition-" + self.id
            },
            "resource": {
                "id"            : prefix + "Condition-" + self.id,
                "resourceType"  : "Condition",
                "clinicalStatus": "active",
                "subject": {
                    "reference": "Patient/" + prefix + self.pid
                },
                "text": {
                    "status": "generated",
                    "div": '<div xmlns="http://www.w3.org/1999/xhtml">%s</div>' % self.name
                },
                "verificationStatus": "confirmed",
                "onsetDateTime": self.start,
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

        if self.end:
            out["resource"]["abatementDateTime"] = self.end

        return out
