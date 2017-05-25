import csv
from testdata import MEDS_FILE


class Med(object):
    """Create instances of Medication list entries; also maintains complete med lists by patient id"""

    meds = {} # Dictionary of med lists, by patient id

    @classmethod
    def load(cls):
        """Loads patient Med observations"""

        # Loop through meds and build patient med lists:
        meds = csv.reader(file(MEDS_FILE,'U'),dialect='excel-tab')
        header = meds.next()
        for med in meds:
            cls(dict(zip(header,med))) # Create a med instance (saved in Med.meds)


    def __init__(self,m):
        self.id       = m['ID']
        self.pid      = m['PID']
        self.start    = m['START_DATE']
        self.end      = m['END_DATE']
        self.status   = "active" if not self.end else "completed"
        self.rxn      = m['RxNorm']
        self.name     = m['Name']
        self.sig      = m['SIG']
        self.q        = m['Q']
        self.days     = m['DAYS']
        self.refills  = int(m['REFILLS']) + 1 if m['REFILLS'] else m['REFILLS']
        self.qtt      = m['Q_TO_TAKE_VALUE']
        if self.qtt != "":
            self.qtt = int(float(self.qtt))
        self.qttunit  = m['Q_TO_TAKE_UNIT']
        self.freq     = m['FREQUENCY_VALUE']
        self.frequnit = m['FREQUENCY_UNIT']
        self.freqduration = ""

        assert self.frequnit == '' or self.frequnit.startswith('/')

        if self.frequnit.startswith('/'):
            self.freqduration = self.frequnit.split('/')[1]

        # Append med to the patient's med list:
        if self.pid in  self.__class__.meds:
            self.__class__.meds[self.pid].append(self)
        else:
            self.__class__.meds[self.pid] = [self]

    def toJSON(self, prefix=""):
        """Builds and returns the MedicationRequest JSON"""

        if prefix:
            prefix += "-"

        out = {
            "request": {
                "method": "PUT",
                "url": "MedicationRequest/" + prefix + "MedicationRequest-" + self.id
            },
            "resource": {
                "id"          : prefix + "MedicationRequest-" + self.id,
                "resourceType": "MedicationRequest",
                "subject"     : {
                    "reference": "Patient/" + prefix + self.pid
                },
                "text": {
                    "status": "generated",
                    "div": '<div xmlns="http://www.w3.org/1999/xhtml">%s (rxnorm: %s)</div>'
                           % (self.name, self.rxn)
                },

                # active | on-hold | cancelled | completed | entered-in-error | stopped | draft | unknown
                "status": self.status,

                # proposal | plan | order | instance-order
                "intent": "order",

                # Identifies the medication being requested. This is a link to a
                # resource that represents the medication which may be the details
                # of the medication or simply an attribute carrying a code that
                # identifies the medication from a known list of medications.
                "medicationCodeableConcept": {
                    "coding": [
                        {
                            "system" : "http://www.nlm.nih.gov/research/umls/rxnorm",
                            "code"   : self.rxn,
                            "display": self.name
                        }
                    ],
                    "text": self.name
                }
            }
        }

        # dosageInstruction - Indicates how the medication is to be used by the patient.
        instruction = {
            "text": self.sig
        }

        if self.freqduration:
            instruction["timing"] = {
                "repeat": {
                    "boundsPeriod": {
                        "start": self.start
                    },
                    "frequency"  : int(self.freq),
                    "period"     : 1,
                    "periodUnit" : self.freqduration
                }
            }

            if self.end != "":
                instruction["timing"]["repeat"]["boundsPeriod"]["end"] = self.end

        if self.qtt and self.qttunit:
            instruction["doseQuantity"] = {
                "value" : float(self.qtt),
                "unit"  : self.qttunit,
                "system": "http://unitsofmeasure.org",
                "code"  : self.qttunit
            }

        if "prn" in self.sig:
            instruction["asNeededBoolean"] = True

        if self.sig:
            out["resource"]["dosageInstruction"] = [instruction]

        # dispenseRequest - Medication supply authorization
        if self.refills or self.q or self.days:
            dispenseRequest = {}
            if self.refills:
                dispenseRequest["numberOfRepeatsAllowed"] = self.refills
            if self.q and self.qttunit:
                dispenseRequest["quantity"] = {
                    "value" : float(self.q),
                    "unit"  : self.qttunit,
                    "system": "http://unitsofmeasure.org",
                    "code"  : self.qttunit
                }
            if self.days:
                dispenseRequest["expectedSupplyDuration"] = {
                    "value" : int(self.days),
                    "unit"  : "days",
                    "system": "http://unitsofmeasure.org",
                    "code"  : "d"
                }
            out["resource"]["dispenseRequest"] = dispenseRequest

        return out
