from patient import Patient

def GeneralObservation(data, prefix=""):
    """Builds and returns the List JSON"""

    if prefix:
        prefix += "-"

    patient = Patient.mpi[data["pid"]]

    out = {
        "resourceType": "Observation",
        "status": "unknown",
        "id": data["id"],
        "identifier": [
            {
                "use"   : "official",
                "system": "http://www.bmc.nl/zorgportal/identifiers/observations",
                "value" : data["id"]
            }
        ],
        "text": {
            "div": '<div xmlns="http://www.w3.org/1999/xhtml">%s</div>' % data["name"]
        },
        "code": {
            "coding": [
                {
                    "system" : data["system"],
                    "code"   : data["code"],
                    "display": data["name"]
                }
            ],
            "text": data["name"]
        },
        "subject": {
            "reference": "Patient/" + prefix + data["pid"]
        },
        "performer": [
            {
                "reference": "Practitioner/" + prefix + "Practitioner-" + patient.gp
            }
        ],
        "effectiveDateTime": data["date"],
        "category": [
            {
                "coding": [
                    {
                        "system" : "http://hl7.org/fhir/observation-category",
                        "code"   : data["categoryCode"],
                        "display": data["categoryDisplay"]
                    }
                ],
                "text": data["categoryDisplay"]
            }
        ]
    }

    if data.has_key("encounter_id"):
        out["context"] = {
            "reference": "Encounter/" + data["encounter_id"]
        }


    return out
