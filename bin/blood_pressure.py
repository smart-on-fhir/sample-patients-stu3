from patient import Patient

def BloodPressure(bp, prefix=""):
    """Generates BloodPressure Observation JSON object"""

    if not bp.has_key("id"):
        raise BaseException("BloodPressure requires 'id'!")

    if not bp.has_key("pid"):
        raise BaseException("BloodPressure requires 'pid'!")

    if prefix:
        prefix += "-"

    patient = Patient.mpi[bp["pid"]]

    out = {
        "resourceType": "Observation",
        "id": prefix + bp["id"],
        "status": "final",
        "effectiveDateTime": bp["date"],
        "subject": {
            "reference": "Patient/" + prefix + bp["pid"]
        },
        "text": {
            "status": "generated",
            "div": '<div xmlns="http://www.w3.org/1999/xhtml">' +
                   "%s: Blood pressure %s/%s mmHg</div>" %
                   (bp["date"], bp["systolic"], bp["diastolic"])
        },
        "category": [
            {
                "coding": [
                    {
                        "system" : "http://hl7.org/fhir/observation-category",
                        "code"   : "vital-signs",
                        "display": "Vital Signs"
                    }
                ],
                "text": "Vital Signs"
            }
        ],
        "code": {
            "coding": [
                {
                    "system" : "http://loinc.org",
                    "code"   : "55284-4",
                    "display": "Blood pressure"
                }
            ],
            "text": "Blood pressure"
        },
        "performer": [
            {
                "reference": "Practitioner/" + prefix + "Practitioner-" + patient.gp
            }
        ],
        "component": [
            {
                "code": {
                    "coding": [
                        {
                            "system" : "http://loinc.org",
                            "code"   : "8480-6",
                            "display": "Systolic blood pressure"
                        }
                    ],
                    "text": "Systolic blood pressure"
                },
                "valueQuantity": {
                    "value": bp["systolic"],
                    "unit": "mmHg",
                    "system": "http://unitsofmeasure.org",
                    "code": "mm[Hg]"
                }
            },
            {
                "code": {
                    "coding": [
                        {
                            "system" : "http://loinc.org",
                            "code"   : "8462-4",
                            "display": "Diastolic blood pressure"
                        }
                    ],
                    "text": "Diastolic blood pressure"
                },
                "valueQuantity": {
                    "value": bp["diastolic"],
                    "unit": "mmHg",
                    "system": "http://unitsofmeasure.org",
                    "code": "mm[Hg]"
                }
            }
        ]
    }

    # Encounter
    if bp.has_key("encounter_id"):
        out["context"] = {
            "reference": "Encounter/%s"%bp["encounter_id"]
        }

    # bodySite
    if bp.has_key("site_system") and bp.has_key("site_code") and bp.has_key("site"):
        out["bodySite"] = {
            "coding": [
                {
                    "system" : bp["site_system"],
                    "code"   : bp["site_code"],
                    "display": bp["site"]
                }
            ],
            "text": bp["site"]
        }

    # bodySite
    if bp.has_key("method_system") and bp.has_key("method_code") and bp.has_key("method"):
        out["method"] = {
            "coding": [
                {
                    "system" : bp["method_system"],
                    "code"   : bp["method_code"],
                    "display": bp["method"]
                }
            ],
            "text": bp["method"]
        }

    # position
    if bp.has_key("position") and bp.has_key("position_system") and bp.has_key("position_code"):
        out["extension"] = [
            {
                "url": "http://fhir-registry.smarthealthit.org/StructureDefinition/vital-signs#position",
                "valueCodeableConcept" : {
                    "coding": [
                        {
                            "system": bp["position_system"],
                            "code"  : bp["position_code"],
                            "display": bp["position"]
                        }
                    ],
                    "text": bp["position"]
                }
            }
        ]


    return out
