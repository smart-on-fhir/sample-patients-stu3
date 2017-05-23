

def Encounter(data, prefix=""):
    """Generates an Encounter JSON"""

    if prefix:
        prefix += "-"

    resource = {
        "resourceType": "Encounter",
        "id": data["id"],
        "status": "finished",
        "class": {
            "code": data["encounter_type"]
        },
        "text": {
            "status": "generated",
            "div": '<div xmlns="http://www.w3.org/1999/xhtml">' +
                   data["start_date"] +": " + data["encounter_type"] +
                   " encounter</div>"
        },
        "type": [
            {
                "coding": [
                    {
                        "system": "http://snomed.info",
                        "code": "270427003",
                        "display": "Patient-initiated encounter"
                    }
                ],
                "text": "Patient-initiated " + data["encounter_type"] + " encounter"
            }
        ],
        "subject": {
            "reference": "Patient/" + prefix + data["pid"]
        },
        "period": {
            "start": data["start_date"],
            "end": data["end_date"]
        }
    }

    return resource
