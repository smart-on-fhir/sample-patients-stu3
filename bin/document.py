import csv
from datetime import datetime
from testdata import DOCUMENTS_FILE
from patient  import Patient


class Document(object):
    """Create instances of Document; also maintains complete documents lists by patient id"""

    documents = {} # Dictionary of documents lists, by patient id

    @classmethod
    def load(cls):
        """Loads patient documents"""

        # Loop through documents and build patient documents lists:
        rows = csv.reader(file(DOCUMENTS_FILE,'U'), dialect='excel-tab')
        header = rows.next()
        for row in rows:
            cls(dict(zip(header, row))) # Create a clinical note instance

    def __init__(self,p):
        self.id        = p['ID']
        self.pid       = p['PID']
        self.date      = p['DATE']
        self.title     = p['TITLE']
        self.mime_type = p['MIME_TYPE']
        self.file_name = p['FILE_NAME']
        self.type      = p['TYPE']

        # Append document to the patient's documents list:
        if self.pid in  self.__class__.documents:
            self.__class__.documents[self.pid].append(self)
        else:
            self.__class__.documents[self.pid] = [self]

    def toJSON(self, binary={}, binary_id="", prefix=""):
        """Builds and returns the DocumentReference JSON"""

        if prefix:
            prefix += "-"

        patient = Patient.mpi[self.pid]

        out = {
            "request": {
                "method": "PUT",
                "url": "DocumentReference/" + prefix + "DocumentReference-" + self.id
            },
            "resource": {
                "id"          : prefix + "DocumentReference-" + self.id,
                "resourceType": "DocumentReference",
                "subject"     : {
                    "reference": "Patient/" + prefix + self.pid
                },
                "text": {
                    "status": "generated",
                    "div": '<div xmlns="http://www.w3.org/1999/xhtml">%s</div>'
                           % self.title
                },
                "status" : "current",
                "created": self.date,
                "indexed": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "type": {
                    "coding": [
                        {
                            "system" : "http://loinc.org",
                            "code"   : "34109-9",
                            "display": "Note"
                        }
                    ],
                    "text": "Note"
                },
                "author": [
                    {
                        "reference": "Practitioner/" + prefix + "Practitioner-" + patient.gp
                    }
                ],
                "description": self.title
            }
        }

        if binary_id and self.mime_type:
            attachment = {
                "url"        : "/" + binary_id,
                "contentType": self.mime_type
            }

            if binary.has_key("size") and binary.has_key("hash"):
                attachment["size"] = binary["size"]
                attachment["hash"] = binary["hash"]

            out["resource"]["content"] = [
                {
                    "attachment": attachment
                }
            ]

        return out
