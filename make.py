#!/usr/bin/python3
from src import letters

# Build and send the acceptance letters.
# letters.sendallemails('db/institution-list-2018.csv', 'acceptance', 'institution')
# letters.sendallemails('db/academic-list-2018.csv', 'acceptance', 'academic')
# letters.sendallemails('db/reject-2018.csv', 'reject')
# letters.sendallemails('db/academic-list-2018.csv', 'paypal_academic')
# letters.sendallemails('db/institution-list-2018.csv', 'paypal_institution')
letters.writeletters('db/institution-list-2018.csv', 'acceptance', 'institution')
letters.writeletters('db/academic-list-2018.csv', 'acceptance', 'academic')
