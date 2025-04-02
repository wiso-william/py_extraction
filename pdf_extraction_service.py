from flask import Flask, request, jsonify
import pdfplumber
import re
import os

app = Flask(__name__)

# Define regex patterns for data extraction
patterns = {
    "Nome": r"(?:Nome|Nominativo)[:\s]+([A-Z][a-z]+\s[A-Z][a-z]+)",
    "Data di nascita": r"(?:Data di nascita)\s*[:\s]*([\d]{2}/[\d]{2}/(?:[\d]{2}|[\d]{4}))",
    "Sesso": r"(?:Sesso)[:\s]+(Maschio|Femmina|Uomo|Donna|M|F)",
    "Codice Fiscale": r"(?:Cd fiscale|Codice Fiscale)[:\s]+([A-Z0-9]{16})"
}

def extract_first_page_text(pdf_path, char_limit=380):
    """Extracts text from the first page of a PDF, limited to a certain number of characters"""
    with pdfplumber.open(pdf_path) as pdf:
        first_page = pdf.pages[0] if pdf.pages else None
        text = first_page.extract_text() if first_page else ""
        return text[:char_limit]

def extract_info(text):
    """Extracts data based on regex patterns"""
    extracted_data = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        extracted_data[key] = match.group(1) if match else "Non trovato"
    return extracted_data

@app.route("/extract", methods=["POST"])
def upload_pdf():
    """Handles PDF upload, extracts text, and returns JSON"""
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    pdf_file = request.files["file"]
    
    if pdf_file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    temp_path = f"temp_{pdf_file.filename}"
    pdf_file.save(temp_path)  # Save the uploaded file temporarily

    try:
        text = extract_first_page_text(temp_path)
        extracted_data = extract_info(text)

        response = {
            "filename": pdf_file.filename,
            "data": extracted_data
        }
        return jsonify(response)

    finally:
        os.remove(temp_path)  # Clean up the temp file

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)