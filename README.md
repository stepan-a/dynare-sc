This repository contains a set of scripts for the administration of the Dynare Summer School. For instance, to send the attendance certificate, open a python shell in the root folder of the project and do:

```python
>>> from src import letters
>>> letters.sendallattendancemails('db/list.csv')
```
where `db/list.csv` is a csv file containing a list of participants (on each row we have the first name, the last name, the institution and the email).