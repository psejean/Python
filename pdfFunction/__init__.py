import logging
import azure.functions as func
import base64
import json
import sys
from io import BytesIO

# Configure logging level (optional, comment out if not needed)
logging.basicConfig(level=logging.INFO)

# Add the 'lib' directory to sys.path so Python knows where to find the module
sys.path.insert(0, './lib')
from PyPDF2 import PdfReader

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Get the PDF data from the request body
        req_body = req.get_json()
        base64_pdf = req_body.get('data')

        if not base64_pdf:
            logging.error("No PDF data provided in the request.")
            return func.HttpResponse(json.dumps({"error": "Missing PDF data"}), status_code=400, headers={"Content-Type": "application/json"})

        # Decode the base64 string to bytes and create a stream
        try:
            pdf_bytes = base64.b64decode(base64_pdf)
            pdf_stream = BytesIO(pdf_bytes)
            reader = PdfReader(pdf_stream)
        except Exception as e:
            logging.error(f"Failed to decode base64 PDF data or initialize PdfReader: {e}")
            return func.HttpResponse(json.dumps({"error": "Error decoding base64 data or initializing PdfReader"}), status_code=500, headers={"Content-Type": "application/json"})

        text_content = []

        # Extract text from each page
        try:
            for page in reader.pages:
                extracted_text = page.extract_text()
                if extracted_text:
                    text_content.append(extracted_text)
        except Exception as e:
            logging.error(f"Failed to extract text from PDF: {e}")
            return func.HttpResponse(json.dumps({"error": "Error extracting text from PDF"}), status_code=500, headers={"Content-Type": "application/json"})

        # Join all text from all pages
        extracted_text = ' '.join(text_content)
        return func.HttpResponse(json.dumps({"extractedText": extracted_text}), status_code=200, headers={"Content-Type": "application/json"})
    except Exception as e:
        logging.exception("An unexpected error occurred while processing the PDF.")
        return func.HttpResponse(json.dumps({"error": str(e)}), status_code=500, headers={"Content-Type": "application/json"})