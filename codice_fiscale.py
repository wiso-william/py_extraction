import re
from datetime import datetime

def estrai_consonanti_vocali(nome):
    consonanti = re.findall(r'[^AEIOU]', nome, re.I)
    vocali = re.findall(r'[AEIOU]', nome, re.I)
    return consonanti, vocali

def calcola_codice_nome(nome):
    nome = nome.upper().replace(" ", "")
    consonanti, vocali = estrai_consonanti_vocali(nome)
    if len(consonanti) >= 4:
        return consonanti[0] + consonanti[2] + consonanti[3]
    elif len(consonanti) >= 3:
        return "".join(consonanti[:3])
    else:
        return "".join(consonanti + vocali)[:3].ljust(3, 'X')

def calcola_codice_cognome(cognome):
    cognome = cognome.upper().replace(" ", "")
    consonanti, vocali = estrai_consonanti_vocali(cognome)
    return "".join(consonanti + vocali)[:3].ljust(3, 'X')

def calcola_codice_data_nascita(data_nascita, sesso):
    mesi = "ABCDEHLMPRST"
    dt = datetime.strptime(data_nascita, "%d/%m/%Y")
    anno = str(dt.year)[-2:]
    mese = mesi[dt.month - 1]
    giorno = dt.day + (40 if sesso.upper() == 'F' else 0)
    return f"{anno}{mese}{giorno:02d}"

def calcola_carattere_controllo(codice_parziale):
    pari = {str(i): i for i in range(10)}
    dispari = {
        '0': 1, '1': 0, '2': 5, '3': 7, '4': 9, '5': 13, '6': 15, '7': 17,
        '8': 19, '9': 21, 'A': 1, 'B': 0, 'C': 5, 'D': 7, 'E': 9, 'F': 13,
        'G': 15, 'H': 17, 'I': 19, 'J': 21, 'K': 1, 'L': 0, 'M': 5, 'N': 7,
        'O': 9, 'P': 13, 'Q': 15, 'R': 17, 'S': 19, 'T': 21, 'U': 1, 'V': 0,
        'W': 5, 'X': 7, 'Y': 9, 'Z': 13
    }
    somma = sum(dispari[c] if i % 2 == 0 else pari.get(c, ord(c) - ord('A')) for i, c in enumerate(codice_parziale))
    return chr((somma % 26) + ord('A'))

def genera_codice_fiscale(nome, cognome, data_nascita, sesso, codice_comune="XXXX"):
    codice = (
        calcola_codice_cognome(cognome) +
        calcola_codice_nome(nome) +
        calcola_codice_data_nascita(data_nascita, sesso) +
        codice_comune
    )
    if "XXXX" in codice_comune:
        return codice  # Restituisce il codice senza il carattere di controllo se manca il comune
    return codice + calcola_carattere_controllo(codice)

# Esempio di utilizzo:
nome = "Mario"
cognome = "Rossi"
data_nascita = "15/04/1985"
sesso = "M"
codice_comune = ""  # Se non si ha il codice comune, verrà usato 'XXXX'

codice_fiscale = genera_codice_fiscale(nome, cognome, data_nascita, sesso, codice_comune or "XXXX")
print("Codice Fiscale:", codice_fiscale)
