
from datetime import datetime
import json
import re
import time
from datetime import datetime
from dateutil import relativedelta

#from constants import *


def storejson(datas, fname="sample"):
    json_object = json.dumps(datas, indent=4)
    with open(f"./data/{fname}.json", "w") as outfile:
        outfile.write(json_object)

def readjson(fname):
    with open(f"./data/{fname}.json", 'r') as openfile:
        json_object = json.load(openfile)
        return json_object
    
COLUMNS = readjson("columns")
CODES   = readjson("codes")
REGLES  = readjson("regles")

def is_valid_text(value, nletters=100):
    valid, message= False, ""

    if isinstance(value,str):
        if len(value) <= nletters:
            valid = True
        else: message = f"La valeur text {value} doit avoir au plus {nletters} caractères"
    else: message = f"La valeur {value} n'est pas un texte"

    return valid, message

def is_valid_date(value, separator='/'):
    valid, message= False, ""

    v, m = is_valid_text(value,10)
    if v:
        date_format = f'%d{separator}%m{separator}%Y'
        try:
            dateObject = datetime.strptime(value, date_format)
            valid = True
            #print(dateObject)
        except ValueError:
            message = f"Format de date incorrect pour la valeur {value}"
    else: message = m

    return valid, message

def is_valid_email(value):
    valid, message= False, ""

    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    v, m = is_valid_text(value)
    if v:
        if(re.fullmatch(regex, value)):
            valid = True
        else: message = f"L'adresse {value} est invalide"
    else: message = m

    return valid, message

def is_valid_value(value, type_validation: str, nletters: int =100):
    valid, message= False, ""
    if type_validation in ["text","date","email"]:
        if type_validation == "text":
            valid, message = is_valid_text(value, nletters)
        elif type_validation == "date":
            valid, message = is_valid_date(value)
        elif type_validation == "email":
            valid, message = is_valid_email(value)
    else:
        message = "Validation's type is incorrect"
    return valid, message


def is_valid_row(row: dict[str,any], columns: list[str], regles: dict[str,str]) -> tuple[bool, list[str]]:
    validation, messages = True, []
    for c in columns:
        vc = True
        regle_of_c = regles[c]
        r1, r2 = "", ""
        if "text" in regle_of_c:
            r1, r2 = tuple(list(regle_of_c.split(',')))
        else:
            r1 = regle_of_c
        nlt = 0 if r2 == "" else int(r2)
        vlc = row[c]
        #print(vlc)
        vc, mc = is_valid_value(str(vlc), r1, nlt)
        if not vc:
            message = f"Colonne <{c}> : "+mc
            messages.append(message)
            validation = False
    return validation, messages


def crw1(row: dict[str,any]) -> tuple[bool,str]:
    valid, message = False, ""

    date_effet = str(row["date_effet"])
    date_editn = str(row["date_demande_edition"])
    dat1 = time.strptime(date_effet, "%d/%m/%Y")
    dat2 = time.strptime(date_editn, "%d/%m/%Y")
    if dat1 > dat2:
        valid = True
    else: message = "La date d'effet est inferieure à la date d'edition"

    return valid, message

def crw2(row: dict[str,any]) -> tuple[bool,str]:
    valid, message = False, ""

    date_effet = str(row["date_effet"])
    date_echea = str(row["date_expiration"])
    dat1 = time.strptime(date_effet, "%d/%m/%Y")
    dat2 = time.strptime(date_echea, "%d/%m/%Y")
    if dat1 < dat2:
        valid = True
    else: message = "La date d'effet est superieure à la date d'echeance"

    return valid, message

def crw3(row: dict[str,any]) -> tuple[bool,str]:
    valid, message = False, ""

    date_effet = str(row["date_effet"])
    date_echea = str(row["date_expiration"])

    dat1 = datetime.strptime(date_effet, '%d/%m/%Y')
    dat2 = datetime.strptime(date_echea, '%d/%m/%Y')
    r = relativedelta.relativedelta(dat2, dat1)

    if r.months <= 12:
        valid = True
    else: message = "La durée du contrat excède 12 mois"

    return valid, message


def crw9(row: dict[str,any]) -> tuple[bool,str]:
    valid, message = False, ""

    couleur = str(row["code_nature_attestation"])

    if couleur in CODES:
        valid = True
    else: message = "Le code nature attestation est incorrect"

    return valid, message

def control_row(index: int, row: dict[str,any]):
    valid, messages = is_valid_row(row, COLUMNS, REGLES)
    if valid:
        v1, m1 = crw1(row)
        v2, m2 = crw2(row)
        v3, m3 = crw3(row)
        v9, m9 = crw9(row)
        valid = v1 and v2 and v3 and v9
        if m1 != '': messages.append(m1)
        if m2 != '': messages.append(m2)
        if m3 != '': messages.append(m3)
        if m3 != '': messages.append(m9)
        if not valid:
            messages = [f"Ligne {index+1} => "+m for m in messages]
    else:
        messages = [f"Ligne {index+1} => "+m for m in messages]
    return valid, messages
    