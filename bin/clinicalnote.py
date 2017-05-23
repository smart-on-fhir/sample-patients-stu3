import csv
from testdata import CLINICAL_NOTES_FILE


class ClinicalNote(object):
    """Create instances of Clinical Note; also maintains complete clinical notes lists by patient id"""

    clinicalNotes = {} # Dictionary of clinical notes lists, by patient id

    @classmethod
    def load(cls):
        """Loads patient clinical notes"""

        # Loop through clinical notes and build patient clinical notes lists:
        rows = csv.reader(file(CLINICAL_NOTES_FILE,'U'), dialect='excel-tab')
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

        # Append clinical note to the patient's clinical notes list:
        if self.pid in  self.__class__.clinicalNotes:
            self.__class__.clinicalNotes[self.pid].append(self)
        else:
            self.__class__.clinicalNotes[self.pid] = [self]

    def toJSON(self, prefix=""):
        """Builds and returns the DocumentReference JSON"""

        if prefix:
            prefix += "-"

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
                }
            }
        }

        return out
