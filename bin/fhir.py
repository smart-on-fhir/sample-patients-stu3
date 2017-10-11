import json
import os
from datetime            import datetime
from no_known_allergies  import no_known_allergies
from general_observation import GeneralObservation
from docs                import fetch_document
from patient             import Patient
from vitals              import VitalSigns
from encounter           import Encounter
from observation         import Observation
from blood_pressure      import BloodPressure
from entry               import Entry
from lab                 import Lab
from familyhistory       import FamilyHistory
from socialhistory       import SocialHistory
from immunization        import Immunization
from procedure           import Procedure
from condition           import Condition
from med                 import Med
from refill              import Refill
from document            import Document
from binary              import Binary
from allergy             import Allergy
from clinicalnote        import ClinicalNote
from practitioner        import Practitioner

GENERATION_MAP = {
    "patient"      : True,
    "LabResults"   : True,
    "BloodPressure": True,
    "Vitals"       : True,
    "Encounter"    : True,
    "SmokingStatus": True,
    "FamilyHistory": True,
    "Immunizations": True,
    "Procedures"   : True,
    "Conditions"   : True,
    "Meds"         : True, # includes Refills
    "Documents"    : True,
    "Allergies"    : True,
    "ClinicalNotes": True
}

SYSTEMS = {
    "SNOMED": "http://snomed.info/sct",
    "NDFRT" : "http://rxnav.nlm.nih.gov/REST/Ndfrt", #"http://hl7.org/fhir/ndfrt",
    "UNII"  : "http://fda.gov/UNII/", #"http://fdasis.nlm.nih.gov",
    "RXNORM": "http://www.nlm.nih.gov/research/umls/rxnorm" #"http://www.nlm.nih.gov/research/umls/rxnorm"
}

def getVital(v, vt, encounter_id):
    return {
        'id'          : v.id,
        'date'        : v.timestamp[:10],
        'code'        : vt['uri'].split('/')[-1],
        'encounter_id': encounter_id,
        'units'       : vt['unit'],
        'value'       : float(getattr(v, vt['name'])),
        'scale'       : 'Qn',
        'name'        : vt['name']
    }

base=0
def uid(resource_type=None, id=None, prefix=None):
    global base
    if not id:
        base += 1
        id = base
    if resource_type is None:
        if prefix is None:
            return str(id)
        return "%s-%s"%(prefix, str(id))
    if prefix is None:
        return "%s/%s-%s"%(resource_type, resource_type, str(id))
    return "%s/%s-%s-%s"%(resource_type, prefix, resource_type, str(id))

def pp_json(json_thing, sort=True, indents=4):
    if type(json_thing) is str:
        return json.dumps(json.loads(json_thing), sort_keys=sort, indent=indents)
    return json.dumps(json_thing, sort_keys=sort, indent=indents)

class FHIRSamplePatient(object):
    def __init__(self, pid, path, base_url=""):
        self.pid = pid
        self.path = path
        self.bundleCounter = 1

        if len(base_url) > 0 and not base_url.endswith("/"):
            base_url += "/"

        self.base_url = base_url

        return

    def appendEntry(self, bundle, data):
        """Appends an entry to the bundle"""
        if len(bundle["entry"]) >= 200:
            patientFile = open(os.path.join(
                self.path,
                "patient-%s.fhir-bundle.0%s.json" % (self.pid, self.bundleCounter)
            ), "w")
            print >> patientFile, pp_json(bundle)
            bundle["entry"] = []
            self.bundleCounter += 1

        bundle["entry"].append(data)
        return bundle

    def set_vitals(self, bundle, prefix=None):
        """Attaches the patient vitals to the given patient bundle"""

        # blood pressure measurements
        bps = []

        # other vitals data
        othervitals = []

        if self.pid in VitalSigns.vitals:

            encounters = []

            # for each vital of this patient
            for v in  VitalSigns.vitals[self.pid]:
                # print v.asTabString()
                encounter_id = None

                # Look for encounter of same type on the same date...
                e = [i for i in encounters if i.has_key("id") and i['date'] == v.start_date and i['type'] == v.encounter_type]
                if len(e) > 0:
                    encounter_id = e[0]['id']
                else:
                    encounter_id = uid(None, v.id, prefix)
                    encounters.append({
                        'date': v.start_date,
                        'type': v.encounter_type,
                        'id'  : encounter_id
                    })

                    # Add the encounter tot the transaction bundle
                    if GENERATION_MAP["Encounter"]:
                        self.appendEntry(bundle, Entry(Encounter({
                            'start_date'    : v.start_date,
                            'end_date'      : v.end_date,
                            'encounter_type': v.encounter_type,
                            'pid'           : self.pid,
                            'id'            : encounter_id
                        }, prefix)))

                for vt in VitalSigns.vitalTypes:
                    try:
                        othervitals.append(getVital(v, vt, encounter_id))
                    except: pass

                # Find and prepare blood pressure measurements
                try:
                    systolic  = getVital(v, VitalSigns.systolic , encounter_id)
                    diastolic = getVital(v, VitalSigns.diastolic, encounter_id)
                    bp = systolic # just use that as base structure
                    bp['systolic']  = int(systolic['value'])
                    bp['diastolic'] = int(diastolic['value'])
                    bp['site']      = v.bp_site
                    bp['id']        = v.id
                    bp['pid']       = self.pid

                    # site
                    if bp['site']:
                        for pc in VitalSigns.bpPositionCodes:
                            if pc['name'] == bp['site']:
                                bp['site_code'] = pc['code']
                                bp['site_system'] = pc['system']

                    # method
                    bp['method'] = v.bp_method
                    if bp['method']:
                        for pc in VitalSigns.bpPositionCodes:
                            if pc['name'] == bp['method']:
                                bp['method_code'] = pc['code']
                                bp['method_system'] = pc['system']

                    # position
                    bp['position'] = v.bp_position
                    if bp['position']:
                        for pc in VitalSigns.bpPositionCodes:
                            if pc['name'] == bp['position']:
                                bp['position_code'] = pc['code']
                                bp['position_system'] = pc['system']

                    bps.append(bp)

                except: pass

        if GENERATION_MAP["BloodPressure"]:
            for bp in bps:
                self.appendEntry(bundle, Entry(BloodPressure(bp, prefix)))

        # Append other vitals as Observation entries to the transaction bundle
        if GENERATION_MAP["Vitals"]:
            for o in othervitals:
                if "units" in o.keys():
                    o["id"] = '%s-%s' % (uid(None, None, prefix), o["name"].lower().replace(' ', '').replace('_', ''))
                    o["unitsCode"] = o["units"]
                    o["categoryCode"] = "vital-signs"
                    o["categoryDisplay"] = "Vital Signs"
                    o["pid"] = self.pid
                self.appendEntry(bundle, Entry(Observation(o, prefix)))

        return bundle

    def set_labs(self, bundle, prefix=None):
        """Attaches the patient's lab results to the bundle"""
        if GENERATION_MAP["LabResults"] and self.pid in Lab.results:
            for o in Lab.results[self.pid]:
                pid = self.pid
                # if prefix:
                #     pid = prefix + "-" + pid
                _json = o.toJSON()
                _json["id"]              = uid(None, "%s-lab" % o.id, prefix)
                _json["pid"]             = pid
                _json["categoryCode"]    = "laboratory"
                _json["categoryDisplay"] = "Laboratory"
                # print _json
                self.appendEntry(bundle, Entry(Observation(_json, prefix)))
        return bundle

    def set_patient(self, bundle, prefix=None):
        """Generates and appends the Patient entry to the transaction"""
        if GENERATION_MAP["patient"]:
            patient = Patient.mpi[self.pid]

            if prefix:
                patient.pid = prefix + "-" + patient.pid

            # look up patient photos
            if self.pid in Document.documents:
                for d in [doc for doc in Document.documents[self.pid] if doc.type == 'photograph']:
                    data = fetch_document(self.pid, d.file_name)
                    binary_id = uid(None, "%s-photo" % d.id, prefix)
                    self.appendEntry(bundle, Binary({
                        "mime_type": d.mime_type,
                        "content"  : data['base64_content'],
                        "id"       : binary_id
                    }))
                    patient.photo_title     = d.title
                    patient.photo_code      = d.mime_type
                    patient.photo_binary_id = binary_id
                    patient.photo_hash      = data["hash"]
                    patient.photo_size      = data["size"]

            patientJSON = patient.toJSON(prefix)
            bundle = self.set_documents(bundle, prefix)
            self.appendEntry(bundle, Entry(patientJSON))

            if patient.gestage:
                self.appendEntry(bundle, Entry(Observation({
                    "id"             : uid(None, "%s-gestage" % self.pid, prefix),
                    "pid"            : self.pid,
                    "date"           : patient.dob,
                    "code"           : "18185-9",
                    "name"           : "Gestational age at birth",
                    "scale"          : "Qn",
                    "value"          : patient.gestage,
                    "units"          : "weeks",
                    "unitsCode"      : "wk",
                    "categoryCode"   : "exam",
                    "categoryDisplay": "Exam"
                }, prefix)))

        return bundle

    def set_meds(self, bundle, prefix=None):
        """Generates and appends a MedicationRequest entry to the transaction"""
        if GENERATION_MAP["Meds"]:
            if self.pid in Med.meds:
                for o in Med.meds[self.pid]:
                    self.appendEntry(bundle, o.toJSON(prefix))
                    for f in Refill.refill_list(o.pid, o.rxn):
                        self.appendEntry(bundle, f.toJSON(o, prefix))
        return bundle

    def set_conditions(self, bundle, prefix=None):
        """Generates and appends a Condition entry to the transaction"""
        if GENERATION_MAP["Conditions"]:
            if self.pid in Condition.conditions:
                for o in Condition.conditions[self.pid]:
                    self.appendEntry(bundle, o.toJSON(prefix))
        return bundle

    def set_procedures(self, bundle, prefix=None):
        """Generates and appends a Procedure entry to the transaction"""
        if GENERATION_MAP["Procedures"]:
            if self.pid in Procedure.procedures:
                for o in Procedure.procedures[self.pid]:
                    self.appendEntry(bundle, o.toJSON(prefix))
        return bundle

    def set_immunizations(self, bundle, prefix=None):
        """Generates and appends a FamilyHistory entry to the transaction"""
        if GENERATION_MAP["Immunizations"]:
            if self.pid in Immunization.immunizations:
                for o in Immunization.immunizations[self.pid]:
                    self.appendEntry(bundle, o.toJSON(prefix))
        return bundle

    def set_family_history(self, bundle, prefix=None):
        """Generates and appends a FamilyHistory entry to the transaction"""
        if GENERATION_MAP["FamilyHistory"]:
            if self.pid in FamilyHistory.familyHistories:
                for fh in FamilyHistory.familyHistories[self.pid]:
                    self.appendEntry(bundle, fh.toJSON(prefix))
        return bundle

    def set_smoking_status(self, bundle, prefix=None):
        """Generates and appends a SmokingStatus entry to the transaction"""
        if GENERATION_MAP["SmokingStatus"]:
            if self.pid in SocialHistory.socialHistories:
                self.appendEntry(bundle, 
                    SocialHistory.socialHistories[self.pid].toJSON(prefix)
                )
        return bundle

    def add_practitioners(self, prefix=None):
        """Generates Practitioner bundles"""
        for p in Practitioner.instances:
            o = Practitioner.instances[p]
            path  = os.path.join(
                self.path,
                "0-practitioner-%s.fhir-bundle.json" % o.data["id"]
            )
            pFile = open(path, "w")
            print >> pFile, pp_json({
                "resourceType": "Bundle",
                "type": "transaction",
                "entry": [ o.toJSON(prefix) ]
            })

    def set_allergies(self, bundle, prefix=None):
        """Generates and appends a AllergyIntolerance entry to the transaction"""
        if GENERATION_MAP["Allergies"]:
            if self.pid in Allergy.allergies:
                for al in Allergy.allergies[self.pid]:
                    if al.statement == 'positive':
                        if al.type == 'drugClass':
                            al.typeDescription = 'medication'
                            al.system = SYSTEMS["NDFRT"] # "http://rxnav.nlm.nih.gov/REST/Ndfrt"
                        elif al.type == 'drug':
                            al.typeDescription = 'medication'
                            al.system = SYSTEMS["RXNORM"] # "http://www.nlm.nih.gov/research/umls/rxnorm"
                        elif al.type == 'food':
                            al.typeDescription = 'food'
                            al.system = SYSTEMS["UNII"] # "http://fda.gov/UNII/"
                        elif al.type == 'environmental':
                            al.typeDescription = 'environment'
                            al.system = SYSTEMS["UNII"] # "http://fda.gov/UNII/"
                        if al.reaction:
                            if al.severity.lower() == 'mild':
                                al.severity = 'mild'
                                al.criticality = 'low'
                            elif al.severity.lower() == 'severe':
                                al.severity = 'severe'
                                al.criticality = 'high'
                            elif al.severity.lower() == 'life threatening' or al.severity.lower() == 'fatal':
                                al.severity = 'severe'
                                al.criticality = 'high'
                            elif al.severity.lower() == 'moderate':
                                al.severity = 'moderate'
                                al.criticality = 'low'
                            else:
                                al.severity = None
                        self.appendEntry(bundle, al.toJSON(prefix))
                    elif al.statement == 'negative' and al.type == 'general':
                        if al.code == '716186003':
                            al.loinc_code = '52473-6'
                            al.loinc_display = 'Allergy'
                            al.text = 'No known allergies'
                            self.appendEntry(bundle, al.toJSON(prefix))
                        elif al.code == '409137002':
                            al.loinc_code = '11382-9'
                            al.loinc_display = 'Medication allergy'
                            al.text = 'No known history of drug allergy'
                            self.appendEntry(bundle, al.toJSON(prefix))
                        else:
                            self.appendEntry(bundle, GeneralObservation({
                                "id"    : al.id,
                                "date"  : al.start,
                                "system": SYSTEMS["SNOMED"], # "http://snomed.info/sct",
                                "code"  : al.code,
                                "name"  : al.allergen,
                                "categoryCode"   : "exam",
                                "categoryDisplay": "Exam"
                            }, prefix))
        return bundle

    def set_documents(self, bundle, prefix=None):
        """Generates and appends a SmokingStatus entry to the transaction"""
        if self.pid in Document.documents and GENERATION_MAP["Documents"]:

            for d in [doc for doc in Document.documents[self.pid] if doc.type != 'photograph']:
                data      = fetch_document (self.pid, d.file_name)
                # d.content = data['base64_content']
                # d.size    = data['size']
                # d.hash    = data['hash']
                # b = d
                # id = uid("Binary", "%s-document" % d.id, prefix)
                # d.binary_id = id
                # template = template_env.get_template('binary.xml')
                # print >>pfile, template.render(dict(globals(), **locals()))
                doc = Binary({
                    "mime_type": d.mime_type,
                    "content"  : data['base64_content'],
                    "id"       : uid(None, "%s-document" % d.id, prefix)
                })

                # self.appendEntry(bundle, doc)

                patientFile = open(os.path.join(
                    self.path,
                    "patient-%s-document-%s.fhir-bundle.json" % (self.pid, d.id)
                ), "w")
                print >> patientFile, pp_json({
                    "resourceType": "Bundle",
                    "type": "transaction",
                    "entry": [ doc ]
                })

                binary_id = uid(None, "%s-document-ref" % d.id, prefix)
                docRef = Document({
                    'ID'       : binary_id,
                    'PID'      : self.pid,
                    'DATE'     : datetime.now().strftime("%Y-%m-%dT%H:%M:%S+" + "05:00"), #.isoformat(),
                    'TITLE'    : d.file_name,
                    'MIME_TYPE': d.mime_type,
                    'FILE_NAME': d.file_name,
                    'TYPE'     : "Document",
                    'mime_type': d.mime_type
                })
                self.appendEntry(bundle, docRef.toJSON(data, binary_id, prefix))

                # id = uid("DocumentReference", "%s-document" % d.id, prefix)
                # d.system = 'http://smarthealthit.org/terms/codes/DocumentType#'
                # d.code = d.type
                # d.display = d.type
                # template = template_env.get_template('document.xml')
                # print >>pfile, template.render(dict(globals(), **locals()))
        # if GENERATION_MAP["Documents"]:
        #     if self.pid in SocialHistory.socialHistories:
        #         self.appendEntry(bundle, 
        #             SocialHistory.socialHistories[self.pid].toJSON(prefix)
        #         )
        return bundle

    def set_clinical_notes(self, bundle, prefix=None):
        """Generates and appends a ClinicalNote entry to the transaction"""
        if GENERATION_MAP["ClinicalNotes"] and self.pid in ClinicalNote.clinicalNotes:
            for d in ClinicalNote.clinicalNotes[self.pid]:
                if d.mime_type == 'text/plain':
                    data = fetch_document (self.pid, d.file_name)
                    # d.content = data['base64_content']
                    # b = d
                    # id = uid("Binary", "%s-note" % d.id, prefix)
                    # d.binary_id = id

                    binary_id = uid(None, "%s-note" % d.id, prefix)

                    note = Binary({
                        "mime_type": d.mime_type,
                        "content"  : data['base64_content'],
                        "id"       : binary_id
                    })

                    self.appendEntry(bundle, note)

                    # if GENERATION_MAP["Documents"]:
                    docRef = Document({
                        'ID'       : uid(None, "%s-note-ref" % d.id, prefix),
                        'PID'      : self.pid,
                        'DATE'     : datetime.now().strftime("%Y-%m-%dT%H:%M:%S+" + "05:00"), #.isoformat(),
                        'TITLE'    : "Note",
                        'MIME_TYPE': d.mime_type,
                        'FILE_NAME': d.file_name,
                        'TYPE'     : "Note",
                        'mime_type': d.mime_type
                    })
                    self.appendEntry(bundle, docRef.toJSON(data, binary_id, prefix))
            #         id = uid("DocumentReference", "%s-note" % d.id, prefix)
            #         d.system = "http://loinc.org"
            #         d.code = '34109-9'
            #         d.display = 'Note'
            #         template = template_env.get_template('document.xml')
            #         print >>pfile, template.render(dict(globals(), **locals()))
        return bundle

    def writePatientData(self, prefix=None):
        """Creates and returns a patient bundle as JSON"""

        self.add_practitioners(prefix)

        bundle = {
            "resourceType": "Bundle",
            "type": "transaction",
            "entry": []
        }

        # patient
        bundle = self.set_patient(bundle, prefix)

        # load vitals, blood pressure, encounters...
        bundle = self.set_vitals(bundle, prefix)

        # labs
        bundle = self.set_labs(bundle, prefix)

        # medication
        bundle = self.set_meds(bundle, prefix)

        # condition
        bundle = self.set_conditions(bundle, prefix)

        # procedure
        bundle = self.set_procedures(bundle, prefix)

        # immunization
        bundle = self.set_immunizations(bundle, prefix)

        # family_history
        bundle = self.set_family_history(bundle, prefix)

        # smoking_status
        bundle = self.set_smoking_status(bundle, prefix)

        # allergies
        bundle = self.set_allergies(bundle, prefix)

        # clinical notes
        bundle = self.set_clinical_notes(bundle, prefix)

        self.saveBundleToFile(bundle)

        print "%s - Done" % self.pid

    def saveBundleToFile(self, bundle):
        """Writes the given bundle to file"""
        patientFile = open(os.path.join(
            self.path,
            "patient-%s.fhir-bundle.json" % self.pid
        ), "w")
        print >> patientFile, pp_json(bundle)
