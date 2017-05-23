import csv
from testdata import PRACTITIONERS_FILE

class Practitioner(object):

    # static dictionary to hold the instances
    instances = {}

    def __init__(self, data):
        """Creates a Practitioner instance and stores it into the static store"""

        if not data.has_key("id"):
            raise BaseException("Practitioner requires id")

        self.data = data

        # Insert the practitioner instance into the static store
        _id = data["id"]
        if not _id in self.__class__.instances:
            self.__class__.instances[_id] = self

    @classmethod
    def load(cls, patient_file_name=PRACTITIONERS_FILE):
        """Load patients from a data file"""

        # Open data file and read in the first (header) record
        pats = csv.reader(file(patient_file_name, 'U'), dialect='excel-tab')
        header = pats.next()

        # Now, read in practitioner data:
        for pat in pats:
            # create practitioner from header and row values
            cls(dict(zip(header, pat)))

    def toJSON(self, prefix=""):
        """Builds and returns the Practitioner JSON"""

        data = self.data

        if prefix:
            prefix += "-"

        out = {
            "request": {
                "method": "PUT",
                "url": "Practitioner/" + prefix + "Practitioner-" + data["id"]
            },
            "resource": {
                "resourceType": "Practitioner",
                "id": prefix + "Practitioner-" + data["id"],
                "text": {
                    "status": "generated",
                    "div": '<div xmlns="http://www.w3.org/1999/xhtml">%s %s</div>'%(data["fname"], data["lname"])
                },
                "active": True,
                "identifier": [
                    {
                        "use": "official",
                        "type": {
                            "coding": [
                                {
                                    "system": "http://hl7.org/fhir/identifier-type",
                                    "code": "SB",
                                    "display": "Social Beneficiary Identifier"
                                }
                            ],
                            "text": "US Social Security Number"
                        },
                        "system": "http://hl7.org/fhir/sid/us-ssn",
                        "value": data["ssn"]
                    }
                ],
                "gender"   : data["gender"],
                "birthDate": data["dob"],
                "name": [
                    {
                        "use"   : "official",
                        "family": data["lname"],
                        "given" : [
                            data["fname"]
                        ]
                    }
                ]
            }
        }

        if data["initial"]:
            out["resource"]["name"][0]["given"].append(data["initial"])

        if data["suffix"]:
            out["resource"]["name"][0]["suffix"] = [data["suffix"]]

        if data["home"] or data["cell"] or data["email"]:
            out["resource"]["telecom"] = []

        if data["home"]:
            out["resource"]["telecom"].append({
                "system": "phone",
                "value" : data["home"],
                "use"   : "home"
            })

        if data["cell"]:
            out["resource"]["telecom"].append({
                "system": "phone",
                "value" : data["cell"],
                "use"   : "mobile"
            })

        if data["email"]:
            out["resource"]["telecom"].append({
                "system": "email",
                "value" : data["email"]
            })

        if data["street"]:
            out["resource"]["address"] = [
                {
                    "use"       : "home",
                    "line"      : [data["street"] + data["apartment"]],
                    "city"      : data["city"],
                    "state"     : data["region"],
                    "postalCode": data["pcode"],
                    "country"   : data["country"]
                }
            ]
        elif data["pcode"] and data["country"]:
            out["resource"]["address"] = [
                {
                    "use"       : "home",
                    "postalCode": data["pcode"],
                    "country"   : data["country"]
                }
            ]

        return out
