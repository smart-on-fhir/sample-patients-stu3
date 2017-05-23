def no_known_allergies(data, prefix=""):
    """Builds and returns the List JSON"""

    if prefix:
        prefix += "-"

    out = {
        "request": {
            "method": "PUT",
            "url": "List/" + prefix + "List-" + data["id"]
        },
        "status": "current",
        "resource": {
            "id"          : prefix + "List-" + data["id"],
            "resourceType": "List",
            "text": {
                "status": "generated",
                "div": '<div xmlns="http://www.w3.org/1999/xhtml">%s</div>' % data["text"]
            }
        },
        "code": {
            "coding": [
                {
                    "system" : "http://loinc.org/",
                    "code"   : data["loinc_code"],
                    "display": data["loinc_display"]
                }
            ],
            "text": data["loinc_display"]
        },
        "subject": {
            "reference": prefix + data["id"],
        },
        "date": data["start"],
        "mode": "snapshot",
        "emptyReason": {
            "coding": [
                {
                    "system" : "http://hl7.org/fhir/list-empty-reason",
                    "code"   : "nilknown",
                    "display": "Nil Known"
                }
            ],
            "text": "Nil Known"
        }
    }

    return out
