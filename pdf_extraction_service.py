from flask import Flask, request, jsonify
import pdfplumber
import re
import os
import requests
from datetime import datetime

app = Flask(__name__)

# Espressioni regolari per l'estrazione dei dati
patterns = {
    "Nome": r"(?:Nome|Nominativo)[:\s]+([A-Z][a-z]+\s[A-Z][a-z]+)",
    "Data di nascita": r"(?:Data di nascita)\s*[:\s]*([\d]{2}/[\d]{2}/([\d]{4}|[\d]{2}))",
    "Sesso": r"(?:Sesso)[:\s]+(Maschio|Femmina|Uomo|Donna|M|F)",
    "Codice Fiscale": r"(?:Cd fiscale|Codice Fiscale)[:\s]+([A-Z0-9]{16})"
}

def extract_first_page_text(pdf_path, char_limit=380):
    """Estrae il testo dalla prima pagina del PDF, limitato a un certo numero di caratteri"""
    with pdfplumber.open(pdf_path) as pdf:
        first_page = pdf.pages[0] if pdf.pages else None
        text = first_page.extract_text() if first_page else ""
        return text[:char_limit]

def extract_info(text):
    """Estrae i dati grezzi dal testo"""
    extracted = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        extracted[key] = match.group(1) if match else "Non trovato"
        # Converti il Codice Fiscale in maiuscolo se trovato
    if extracted.get("Codice Fiscale") != "Non trovato":
        extracted["Codice Fiscale"] = extracted["Codice Fiscale"].upper()
    return extracted

def convert_date(date_str):
    if date_str == "Non trovato":
        return ""
    
    try:
        day, month, year = date_str.split('/')
        if len(year) == 2:  # Anno a 2 cifre (es. '66')
            year = f"19{year}"
        elif len(year) == 4:  # Anno a 4 cifre (es. '1966')
            pass  # Usa l'anno così com'è
        else:
            return ""  # Formato non supportato
        
        iso_date = f"{year}-{month}-{day}"
        datetime.strptime(iso_date, "%Y-%m-%d")  # Validazione
        return iso_date
    except Exception as e:
        print(f"⚠️ Errore conversione data '{date_str}': {e}")
        return ""

def normalize_sex(sex_value):
    """Normalizza il sesso in 'M' o 'F'"""
    if not sex_value:
        return ""
    if sex_value.lower() in ["maschio", "uomo", "m"]:
        return "M"
    if sex_value.lower() in ["femmina", "donna", "f"]:
        return "F"
    return ""

@app.route("/extract", methods=["POST"])
def upload_pdf():
    """Gestisce l'upload del PDF, estrae i dati e li invia a Spring Boot"""
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    pdf_file = request.files["file"]
    
    if pdf_file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    temp_path = f"temp_{pdf_file.filename}"
    pdf_file.save(temp_path)

    try:
        text = extract_first_page_text(temp_path)
        raw_data = extract_info(text)

        # Adatta i campi al backend Spring Boot
        nome_completo = raw_data["Nome"] if raw_data["Nome"] != "Non trovato" else ""
        nome_parts = nome_completo.split()
        name = nome_parts[0] if len(nome_parts) >= 1 else ""
        surname = nome_parts[1] if len(nome_parts) >= 2 else ""

        extracted_data = {
            "name": name,
            "surname": surname,
            "codiceFiscale": raw_data["Codice Fiscale"] if raw_data["Codice Fiscale"] != "Non trovato" else "",
            "birthDate": convert_date(raw_data["Data di nascita"]),
            "sex": normalize_sex(raw_data["Sesso"]),
            "age": None,
            "height": None,
            "weight": None
        }

        # 🔽 MODIFICA QUI CON IL TUO ENDPOINT SPRING BOOT CORRETTO
        springboot_api_url = "http://localhost:8080/api/v1/profiles"

        # Invia i dati al backend Spring Boot
        spring_response = requests.post(
            springboot_api_url,
            json=extracted_data,
            headers={"Content-Type": "application/json"}
        )

        if spring_response.status_code in [200, 201]:
            print("✅ Dati inviati con successo a Spring Boot")
        else:
            print(f"⚠️ Errore nell'invio a Spring Boot: {spring_response.status_code} - {spring_response.text}")

        return jsonify({
            "filename": pdf_file.filename,
            "estratti": extracted_data,
            "spring_response": spring_response.status_code
        })

    finally:
        os.remove(temp_path)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)