import logging
import azure.functions as func
import base64
from PyPDF2 import PdfReader

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Get PDF data from the request body
        req_body = req.get_json()
        base64_pdf = req_body.get('data')

        if not base64_pdf:
            logging.error("No PDF data provided in the request.")
            return func.HttpResponse("Missing PDF data", status_code=400)

        # Decode the base64 string to bytes
        try:
            pdf_bytes = base64.b64decode(base64_pdf)
        except Exception as e:
            logging.error(f"Failed to decode base64 PDF data: {e}")
            return func.HttpResponse("Error decoding base64 data", status_code=500)

        # Initialize the PDF Reader with the byte stream
        try:
            reader = PdfReader()
            reader.stream = pdf_bytes
        except Exception as e:
            logging.error(f"Failed to initialize PdfReader: {e}")
            return func.HttpResponse("Error initializing PdfReader", status_code=500)

        text_content = []

        # Extract text from each page
        try:
            for page in reader.pages:
                text_content.append(page.extract_text())
        except Exception as e:
            logging.error(f"Failed to extract text from page: {e}")
            return func.HttpResponse("Error extracting text from PDF", status_code=500)

        # Join all text from all pages
        extracted_text = ' '.join(text_content)

        return func.HttpResponse(extracted_text, status_code=200)
    except Exception as e:
        logging.exception("An unexpected error occurred while processing the PDF.")
        return func.HttpResponse("An unexpected error occurred.", status_code=500)
