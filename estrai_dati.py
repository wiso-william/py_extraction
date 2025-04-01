import os
import pdfplumber

# Cartella contenente i PDF
pdf_folder = "pdf"
char_limit = 380  # Numero massimo di caratteri da estrarre

def extract_first_page_text(pdf_path):
    """Estrae il testo della prima pagina di un PDF e lo limita a un certo numero di caratteri"""
    with pdfplumber.open(pdf_path) as pdf:
        first_page = pdf.pages[0]  # Prima pagina
        text = first_page.extract_text() if first_page else ""
        return text[:char_limit]  # Limita la lunghezza del testo

# Scansiona tutti i file nella cartella "pdf"
for filename in os.listdir(pdf_folder):
    if filename.endswith(".pdf"):
        pdf_path = os.path.join(pdf_folder, filename)
        text = extract_first_page_text(pdf_path)
        print(f"--- {filename} ---")
        print(text)
        print("\n" + "="*50 + "\n")
