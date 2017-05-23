from random import randint, choice
from string import ascii_uppercase, lower
import datetime

# Constants for building test data from data

# Paths relative source data and mapping files
DATA_PATH = "../data/"
MAP_PATH = "../maps/"
RI_PATH = "../ri-data/"

# Data file names:
PATIENTS_FILE = DATA_PATH+'patients.txt'
LABS_FILE = DATA_PATH + 'labs.txt'
IMMUNIZATIONS_FILE = DATA_PATH+'immunizations.txt'
VITALS_FILE = DATA_PATH+'vitals.txt'
MEDS_FILE = DATA_PATH + 'meds.txt'
PROBLEMS_FILE = DATA_PATH + 'problems.txt'
PROCEDURES_FILE = DATA_PATH + 'procedures.txt'
ALLERGIES_FILE = DATA_PATH + 'allergies.txt'
SOCIALHISTORY_FILE = DATA_PATH + 'socialhistory.txt'
FAMILYHISTORY_FILE = DATA_PATH + 'familyhistory.txt'
NOTES_PATH = DATA_PATH + 'notes'
DOCUMENTS_PATH = DATA_PATH + 'documents'
REFILLS_FILE = DATA_PATH + 'refills.txt'
RI_PATIENTS_FILE = RI_PATH + 'ri-patients.txt'
CLINICAL_NOTES_FILE = DATA_PATH + 'clinicalnotes.txt'
DOCUMENTS_FILE = DATA_PATH + 'documents.txt'
IMAGINGSTUDIES_FILE = DATA_PATH + 'imagingstudies.txt'
PRACTITIONERS_FILE = DATA_PATH + 'practitioners.txt'

# Mapping file names:
LOINC_FILE = MAP_PATH + 'short_loinc.txt'

# Define some values for generating random demographics data
# These values can be freely altered to change locations and names

# Postal Data Choices
# Note weighting for population density by repeats:
POSTAL_INDEX_CHOICES = (
    0, 0, 0, # repeated three times--largest population
    1, 1,    # repeated twice, less population
    2, 3, 4, 5, 6, 7, 8
)

POSTAL_DATA = (
    {'city': 'Bixby', 'region': 'OK', 'pcode': '74008', 'country': 'USA'},
    {'city': 'Mounds', 'region': 'OK', 'pcode': '74047', 'country': 'USA'},
    {'city': 'Sapulpa', 'region': 'OK', 'pcode': '74066', 'country': 'USA'},
    {'city': 'Sand Springs', 'region': 'OK', 'pcode': '74063', 'country': 'USA'},
    {'city': 'Broken Arrow', 'region': 'OK', 'pcode': '74014', 'country': 'USA'},
    {'city': 'Tulsa', 'region': 'OK', 'pcode': '74126', 'country': 'USA'},
    {'city': 'Tulsa', 'region': 'OK', 'pcode': '74117', 'country': 'USA'},
    {'city': 'Tulsa', 'region': 'OK', 'pcode': '74116', 'country': 'USA'},
    {'city': 'Tulsa', 'region': 'OK', 'pcode': '74108', 'country': 'USA'}
)

# Street names for randomization, roughly adapted from USPS most common street names
STREET_NAMES = (
    'Park', 'Main', 'Oak', 'Pine', 'Elm', 'Washington', 'Lake', 'Hill', 'Walnut',
    'Spring', 'North', 'Ridge', 'Church', 'Willow', 'Mill', 'Sunset', 'Railroad',
    'Jackson', 'West', 'South', 'Center', 'Highland', 'Forest', 'River', 'Meadow',
    'East', 'Chestnut'
)

STREET_TYPES = ('St', 'Rd', 'Ave')

# Names for randomization, roughly adapted from US Census most common names:
MALES = (
    'James', 'John', 'Robert', 'Michael', 'William', 'David', 'Richard', 'Charles',
    'Joseph', 'Thomas', 'Christopher', 'Daniel', 'Paul', 'Mark', 'Donald', 'George',
    'Kenneth', 'Steven', 'Edward', 'Brian', 'Ronald', 'Anthony', 'Kevin', 'Jason',
    'Frank', 'Scott', 'Eric', 'Stephan', 'Joshua', 'Patrick', 'Harold', 'Carl'
)

FEMALES = (
    'Mary', 'Patricia', 'Linda', 'Barbara', 'Elizabeth', 'Jennifer', 'Maria',
    'Susan', 'Margaret', 'Dorothy', 'Lisa', 'Nancy', 'Karen', 'Betty', 'Helen',
    'Sandra', 'Donna', 'Carol', 'Ruth', 'Sharon', 'Michelle', 'Laura', 'Sarah',
    'Kimberly', 'Jessica', 'Shirley', 'Cynthia', 'Melissa', 'Brenda', 'Amy'
)

SURNAMES = (
    'Smith', 'Johnson', 'Williams', 'Jones', 'Brown', 'Davis', 'Miller', 'Wilson',
    'Moore', 'Taylor', 'Anderson', 'Thomas', 'Jackson', 'White', 'Harris', 'Gracia',
    'Robinson', 'Clark', 'Lewis', 'Lee', 'Hall', 'Allen', 'Young', 'Hill', 'Green',
    'Adams', 'Baker', 'Nelson', 'Campbell', 'Parker', 'Collins', 'Rodgers', 'Reed',
    'Cook', 'Morgan', 'Brooks', 'Kelly', 'James', 'Bennett', 'Woods', 'Ross', 'Long',
    'Hughes', 'Butler', 'Coleman', 'Jenkins', 'Barnes', 'Ford', 'Graham', 'Owens',
    'Cole', 'West', 'Diaz', 'Gibson', 'Rice', 'Shaw', 'Hunt', 'Black', 'Palmer'
)

# Utility Functions for generating randomized data

def rndDate(y):
    """Returns a random date within a given year."""

    # Start with Jan 1st
    d = datetime.date(y, 1, 1)

    # Adjust year length for leap years
    ylen = 366 if y % 400 == 0 or (y % 4 == 0 and y % 100 != 0) else 365

    # Generate random day in year
    r = randint(0, ylen - 1)
    return datetime.date.fromordinal(d.toordinal() + r)

def rndName(gender):
    """Returns a random, gender appropriate, common name tuple: (fn,ln)"""
    fnames = MALES if gender == 'M' else FEMALES
    return (
        fnames[randint(0, len(fnames) - 1)],
        choice(ascii_uppercase),
        SURNAMES[randint(0, len(SURNAMES) - 1)]
    )

def toEmail(name):
    return "%s.%s@example.com"%(lower(name[0]), lower(name[2]))

def rndAddress():
    """
    Returns a random address"""
    index = POSTAL_INDEX_CHOICES[randint(0, len(POSTAL_INDEX_CHOICES) - 1)]
    street = ' '.join((
        str(randint(1, 100)),
        STREET_NAMES[randint(0, len(STREET_NAMES) - 1)],
        STREET_TYPES[randint(0, len(STREET_TYPES) - 1)]
    ))
    address = POSTAL_DATA[index]
    address['street'] = street
    address['apartment'] = '' if randint(0, 1) else ' '.join(('Apt', str(randint(1, 30))))
    return address

def rndTelephone():
    """
    Returns a random telephone"""
    telephone = '-'.join(("800", str(randint(100, 999)), str(randint(1000, 9999))))
    return telephone

def rndGestAge():
    """
    Returns a random gestational age"""
    gestage = '.'.join((str(randint(30, 45)), str(randint(0, 9))))
    return gestage

def rndAccNum():
    """ Returns a random accession number """
    return "A%d"%randint(100000000, 999999999)

