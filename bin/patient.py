import csv
# import datetime
from random import randint
from testdata import rndDate, rndName, rndAddress, rndTelephone, toEmail, rndGestAge
from testdata import PATIENTS_FILE, RI_PATIENTS_FILE

XMLNS_HTML = "http://www.w3.org/1999/xhtml"

class Patient(object):
    """Creates patient instances and maintains a dictionary of all patients"""

    mpi = {}  # static dictionary to hold the master patient index.

    @classmethod
    def generate(cls, patient_file_name=RI_PATIENTS_FILE):
        """Generates a patient file from raw data; replaces old patients file"""

        # Open the patient data file for writing generated data
        f = open(PATIENTS_FILE, 'w')
        top = True # Starting at the top of the file (need to write header here...)

        # Open the raw data file and read in the first (header) record
        pats = csv.reader(file(patient_file_name, 'U'), dialect='excel-tab')
        header = pats.next()

        # Read in patient data:
        for pat in pats:

            # create patient from header and row values
            p = dict((zip(header, pat)))

            # Add synthetic data
            patient_name = rndName(p['GENDER'])
            p['fname'] = patient_name[0]
            p['initial'] = patient_name[1]
            p['lname'] = patient_name[2]

            # Add random day of year to year of birth to get dob value
            # Make it for the prior year so vists, tests come after birth
            p['dob'] = rndDate(int(p['YOB']) - 1).isoformat()

            # Map raw GENDER to SMART encoding values
            # (For the moment, SMART only handles 'male' and 'female'...)
            gender = 'male' if p['GENDER'] == 'M' else 'female'
            p['gender'] = gender

            p['email'] = toEmail(patient_name)

            # Finally, add a random address:
            adr = rndAddress()
            p = dict(p.items() + adr.items())
            p['home'] = '' if randint(0, 1) else rndTelephone()
            p['cell'] = '' if randint(0, 1) else rndTelephone()
            p['gestage'] = '' if randint(0, 1) else rndGestAge()

            # Write out the new patient data file:
            # Start with the header (writing only once at the top of the file):
            if top:
                head = p.keys()
                print >> f, "\t".join(head)
                top = False
            # Then write out the row:
            print >> f, "\t".join([p[field] for field in head])
        f.close()

    @classmethod
    def load(cls, patient_file_name=PATIENTS_FILE):
        """Load patients from a data file"""

        # Open data file and read in the first (header) record
        pats = csv.reader(file(patient_file_name, 'U'), dialect='excel-tab')
        header = pats.next()

        # Now, read in patient data:
        for pat in pats:
            cls(dict(zip(header, pat))) # create patient from header and row values

    def __init__(self, patient_dictionary):
        """Patient instance is initialized with a demographics dictionary"""
        self.demographics = patient_dictionary

        # Initialize instance vars for backward compatibility
        self.pid    = self.demographics['PID']
        self.fname  = self.demographics['fname']
        self.lname  = self.demographics['lname']
        self.gender = self.demographics['gender']
        self.zip    = self.demographics['pcode']
        self.dob    = self.demographics['dob']

        # Initialize additional instance vars
        self.initial   = self.demographics['initial']
        self.street    = self.demographics['street']
        self.apartment = self.demographics['apartment']
        self.city      = self.demographics['city']
        self.region    = self.demographics['region']
        self.pcode     = self.demographics['pcode']
        self.country   = self.demographics['country']
        self.email     = self.demographics['email']
        self.home      = self.demographics['home']
        self.cell      = self.demographics['cell']
        self.gestage   = self.demographics['gestage']
        self.gp        = self.demographics['gp']

        self.photo_title     = None
        self.photo_code      = None
        self.photo_binary_id = None
        self.photo_hash      = None
        self.photo_size      = None

        # Insert the patient instance into the Patient mpi store:
        pid = self.pid
        if not pid in self.__class__.mpi:
            self.__class__.mpi[pid] = self

    def asTabString(self):
        """Return a string with a tab-separated represention of demographics"""
        name = "%s, %s"%(self.lname, self.fname)
        return "%s\t%s\t%s\t%s"%(self.pid, self.dob, self.gender, name)

    def toJSON(self, prefix=""):

        if prefix:
            prefix += "-"

        out = {
            "resourceType": "Patient",
            "id": self.pid,
            "text": {
                "status": "generated",
                "div": '<div xmlns="%s">%s %s</div>'%(XMLNS_HTML, self.fname, self.lname)
            },
            "active": True,
            "identifier": [
                {
                    "use" : "official",
                    "type": {
                        "coding": [
                            {
                                "system" : "http://hl7.org/fhir/v2/0203",
                                "code"   : "MR",
                                "display": "Medical Record Number"
                            }
                        ],
                        "text": "Medical Record Number"
                    },
                    "system": "http://hospital.smarthealthit.org",
                    "value" : self.pid
                }
            ],
            "gender"   : self.gender,
            "birthDate": self.dob,
            "name": [
                {
                    "use"   : "official",
                    "family": self.lname,
                    "given" : [
                        self.fname
                    ]
                }
            ]
        }

        if self.initial:
            out["name"][0]["given"].append(self.initial)

        if self.home or self.cell or self.email:
            out["telecom"] = []

        if self.home:
            out["telecom"].append({
                "system": "phone",
                "value" : self.home,
                "use"   : "home"
            })

        if self.cell:
            out["telecom"].append({
                "system": "phone",
                "value" : self.cell,
                "use"   : "mobile"
            })

        if self.email:
            out["telecom"].append({
                "system": "email",
                "value" : self.email
            })

        if self.street:
            out["address"] = [
                {
                    "use"       : "home",
                    "line"      : [self.street],
                    "city"      : self.city,
                    "state"     : self.region,
                    "postalCode": self.pcode,
                    "country"   : self.country
                }
            ]
        elif self.pcode and self.country:
            out["address"] = [
                {
                    "use"       : "home",
                    "postalCode": self.pcode,
                    "country"   : self.country
                }
            ]

        if self.photo_title:
            out["photo"] = [
                {
                    "contentType": self.photo_code,
                    "url"        : "/Binary/" + self.photo_binary_id,
                    "hash"       : self.photo_hash,
                    "title"      : self.photo_title,
                    "size"       : self.photo_size
                }
            ]

        # Patient's nominated care provider.
        if self.gp:
            out["generalPractitioner"] = [
                {
                    "reference": "Practitioner/%sPractitioner-%s" % (prefix, self.gp)
                }
            ]

        return out
