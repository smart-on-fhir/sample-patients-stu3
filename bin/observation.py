from patient import Patient

def escape(s):
    """Escapes a string to make it HTML-safe"""
    s = str(s)
    s = s.replace('"', "&quot;")
    s = s.replace(">", "&gt;")
    s = s.replace("<", "&lt;")
    return s

def Observation(data, prefix=""):
    """Generates an Observation JSON bundle"""

    if not data.has_key("pid"):
        raise BaseException("Observation requires 'pid")
    if not data.has_key("id"):
        raise BaseException("Observation requires 'id")
    if not data.has_key("code"):
        raise BaseException("Observation requires 'code")
    if not data.has_key("name"):
        raise BaseException("Observation requires 'name")

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
            "status": "generated",
            "div": '<div xmlns="http://www.w3.org/1999/xhtml">%s: %s = %s %s</div>' % (
                escape(data["date"]),
                escape(data["name"]),
                escape(data["value"]),
                escape(data.get("units", ''))
            )
        },
        "performer": [
            {
                "reference": "Practitioner/" + prefix + "Practitioner-" + patient.gp
            }
        ],
        "code": {
            "coding": [
                {
                    "system" : "http://loinc.org",
                    "code"   : data["code"],
                    "display": data["name"]
                }
            ],
            "text": data["name"]
        },
        "subject": {
            "reference": "Patient/" + prefix + data["pid"]
        },
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

    if data.has_key("low") and data.get("scale", None) == "Ord" and data["low"][0]:
        out["extension"] = [
            {
                "url": "http://fhir-registry.smarthealthit.org/StructureDefinition/labs#value-range",
                "valueString": data["low"]
            }
        ]

    if data.has_key("scale") and data.has_key("value"):
        if data["scale"] == 'Ord' or data["scale"] == 'Nom':
            out["valueString"] = data["value"]


    # The healthcare event (e.g. a patient and healthcare provider
    # interaction) during which this observation is made.
    # This will typically be the encounter the event occurred within, but
    # some events may be initiated prior to or after the official completion
    # of an encounter or episode but still be tied to the context of the
    # encounter or episode (e.g. pre-admission lab tests).
    if data.has_key("encounter_id"):
        out["context"] = {
            "reference": "Encounter/" + data["encounter_id"]
        }

    # Normally, an observation will have either a single value or a set of
    # related observations. A few observations (e.g. Apgar score) may have
    # both a value and related observations (for an Apgar score, the
    # observations from which the measure is derived). If a value is present,
    # the datatype for this element should be determined by Observation.code.
    # This element has a variable name depending on the type as follows:
    # valueQuantity, valueCodeableConcept, valueString, valueBoolean,
    # valueRange, valueRatio, valueSampledData, valueAttachment, valueTime,
    # valueDateTime, or valuePeriod. (The name format is "'value' + the type
    # name" with a capital on the first letter of the type).
    if data.has_key("scale") and data["scale"] == 'Qn':
        try:
            value = float(data["value"] or "0")
            code  = data["units"]
            if data.has_key("unitsCode"):
                code  = data["unitsCode"]

            out["valueQuantity"] = {
                "value" : value,
                "system": "http://unitsofmeasure.org"
            }

            if code:
                out["valueQuantity"]["code"] = code

            if data["units"]:
                out["valueQuantity"]["unit"] = data["units"]

        except:
            out["valueString"] = data["value"]

    # Most observations only have one generic reference range. Systems MAY
    # choose to restrict to only supplying the relevant reference range
    # based on knowledge about the patient (e.g., specific to the patient's
    # age, gender, weight and other factors), but this may not be possible
    # or appropriate. Whenever more than one reference range is supplied,
    # the differences between them SHOULD be provided in the reference range
    # and/or age properties.
    if data.has_key("low") and data.has_key("high") and data.has_key("units") and data["units"]:
        low =  {
            "value" : float(data["low"] or "0"),
            "system": "http://unitsofmeasure.org"
        }

        high = {
            "value" : float(data["high"] or "0"),
            "system": "http://unitsofmeasure.org"
        }

        if data["units"]:
            low["unit"] = data["units"]
            low["code"] = data["units"]
            high["unit"] = data["units"]
            high["code"] = data["units"]

        out["referenceRange"] = [
            {
                "type": {
                    "coding": [
                        {
                            "system" : "http://hl7.org/fhir/referencerange-meaning",
                            "code"   : "normal",
                            "display": "Normal Range"
                        }
                    ],
                    "text": "Normal Range"
                },
                "low": low,
                "high": high
            }
        ]

    return out
