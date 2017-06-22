SMART on FHIR Test Data Generator
=================================

This generator uses the data files in the `data` directory to generate
FHIR test data. The files in the data directory are tab-delimited tables that
can be edited and extended with new data as needed.

All the Python scripts are in the `bin` directory, and should be run from that
directory.

The main script for general use is `generate.py`, the other files in `bin` 
are basically modules supporting generate.py. The file `testdata.py` contains
most of the constant declarations and utility functions that drive the system
configuration. The file `fhir.py` contains all the FHIR formatting code. 

From the 'bin' directory, run:

    python generate.py --help

To get a general help message.

To generate the test data files in the 'generated-data' directory:

    python generate.py --write-fhir ../out --id-prefix "smart"

The primary purpose of this tool is to generate FHIR STU3 transaction bundles as
JSON files. Once generated these bundles can be inserted into any compatible 
FHIR server using it's API. Since you might want to insert the same data into
multiple servers or to add different tags to that data resources, we have 
delegated these tasks to another tool called Tag Uploader available at
https://github.com/smart-on-fhir/tag-uploader
