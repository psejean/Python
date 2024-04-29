import logging
import azure.functions as func
import base64
import json
import sys

# Configure logging level (optional, comment out if not needed)
logging.basicConfig(level=logging.INFO)

# Add the 'lib' directory to sys.path so Python knows where to find the module
sys.path.insert(0, './lib')
from PyPDF2 import PdfReader

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        # Attempt to get the request body and decode it from base64
        try:
            req_body = req.get_body().decode('utf-8')
            data = json.loads(req_body)  # Parse request body to JSON
            base64_pdf = data.get('data')  # Extract the 'data' field
        except json.JSONDecodeError as e:
            logging.error(f"JSONDecodeError: {e}")
            return func.HttpResponse("Invalid JSON in request body.", status_code=400)
        except Exception as e:
            logging.error(f"Error processing request body: {e}")
            return func.HttpResponse("Error reading request body.", status_code=400)

        if not base64_pdf:
            logging.error("No PDF data provided in the request.")
            return func.HttpResponse("Missing PDF data in request.", status_code=400)

        # Decode the base64 string to bytes
        try:
            pdf_bytes = base64.b64decode(base64_pdf)
        except base64.binascii.Error as e:
            logging.error(f"Base64 decoding error: {e}")
            return func.HttpResponse("Error decoding base64 PDF data.", status_code=400)

        # Initialize the PDF Reader with the byte stream
        try:
            reader = PdfReader()
            reader.stream = pdf_bytes
        except Exception as e:
            logging.error(f"Failed to initialize PdfReader: {e}")
            return func.HttpResponse("Error initializing PdfReader.", status_code=500)

        text_content = []

        # Extract text from each page
        try:
            for page in reader.pages:
                text_content.append(page.extract_text())
        except Exception as e:
            logging.error(f"Failed to extract text from PDF: {e}")
            return func.HttpResponse("Error extracting text from PDF.", status_code=500)

        # Join all text from all pages
        extracted_text = ' '.join(text_content)

        return func.HttpResponse(extracted_text, status_code=200)
    except Exception as e:
        logging.exception("An unexpected error occurred while processing the PDF.")
        return func.HttpResponse("An unexpected error occurred.", status_code=500)
