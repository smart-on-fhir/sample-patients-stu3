import csv
from testdata import LABS_FILE, rndAccNum
from codes import Loinc



class Lab(object):
    """Create instances of lab results;
       also maintains complete results list (by patient)
       and a dictionary of loinc code frequencies"""

    codes   = {} # Dictionary of code frequency indexed by loinc code
    results = {} # Dictionary of result lists, by patient id

    @classmethod
    def load(cls):
        """Loads patient lab observations"""

        # First build the codes and frequency dictionary:
        _labs  = csv.reader(file(LABS_FILE,'U'), dialect='excel-tab')
        header = _labs.next()
        cIndex = header.index('LOINC')  # Locate the LOINC index field
        for lab in _labs:
            code = lab[cIndex] # Get the loinc code from the result record
            if code in cls.codes:  # Update the codes dictionary with the count
                cls.codes[code] += 1
            else:
                cls.codes[code] = 1

        # And initialize Loinc.info dictionary to handle these codes:
        Loinc.load(cls.codes.keys())

        # Now loop back through labs and build patient results lists:
        _labs = csv.reader(file(LABS_FILE,'U'), dialect='excel-tab')
        header = _labs.next()
        for lab in _labs:
            cls(dict(zip(header, lab))) # Create a result instance (saved in Lab.results)

    @classmethod
    def stats(cls):
        """Prints statistics, including a sorted frequency list"""

        # loop through a code list (sorted [desc] by frequency count:
        code_list = sorted(cls.codes.keys(), key=lambda c: -cls.codes[c])
        total_results = 0
        for code in code_list:
            total_results += cls.codes[code]
            print "%s\t%d\t%s,\t%s\t%s"%(
                code,                        #loinc code
                cls.codes[code],             #frequency
                Loinc.info[code].scale,      #scale of test
                Loinc.info[code].ucum,       #UCUM code (if any)
                Loinc.info[code].name        #Name of test
            )
        print "%d lab results"%total_results
        print "%d patients with lab results"%len(cls.results)
        print "%d unique tests (LOINC codes)"%len(cls.codes)


    def toJSON(self):

        out = {
            "id"   : self.id,
            "pid"  : self.pid,
            "code" : self.code,
            "date" : self.date,
            "name" : self.name,
            "value": self.value,
            "units": self.units,
            "scale": self.scale
        }

        if hasattr(self, "high"):
            out["high"] = self.high

        if hasattr(self, "low"):
            out["low"] = self.low

        return out

    def __init__(self,o):
        self.id   = o['ID']
        self.pid  = o['PID']
        self.code = o['LOINC']
        self.date = o['DATE']

        if self.code in Loinc.info.keys():
            self.name = Loinc.info[self.code].name
        else:
            self.name = o['NAME']

        self.scale = o['SCALE']#Loinc.info[self.code].scale

        # Handle value and ranges:
        self.value = o['VALUE']
        if self.scale == 'Qn':
            self.low=o['LOW']
            self.high=o['HIGH']

        if self.scale=='Ord':
            # The Ord choices are stored in the low value field, separated by ';'
            self.low = o['LOW'].split('; ')
            if len(self.low[0]) > 0 and not self.value in self.low:
                # Print out error msg if Ord values not formatted properly:
                print "%s -> Error for code %s: value=%s not in %s"%(
                    self.pid, self.code, self.value, self.low
                )

        # Handle units, update to UCUM if possible:
        if self.code in Loinc.info.keys() and Loinc.info[self.code].ucum: #if there is a ucum unit available
            self.units = Loinc.info[self.code].ucum  # Then use it
        else:
            self.units = o['UNITS'] # Otherwise, use result units

        self.acc_num = rndAccNum()
        #self.scale = Loinc.info[self.code].scale

        # Append result to the results dictionary of lists
        if self.pid in  self.__class__.results:
            self.__class__.results[self.pid].append(self)
        else:
            self.__class__.results[self.pid] = [self]

