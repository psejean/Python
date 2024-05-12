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
import re

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Processing PDF extraction request")

    try:
        req_body = req.get_json()
        base64_pdf = req_body.get('data')
        
        if not base64_pdf:
            logging.error("No PDF data provided in the request")
            return func.HttpResponse(
                json.dumps({"error": "Missing PDF data"}),
                status_code=400,
                headers={"Content-Type": "application/json"}
            )

        try:
            pdf_bytes = base64.b64decode(base64_pdf)
            pdf_stream = BytesIO(pdf_bytes)
            reader = PdfReader(pdf_stream)
        except Exception as e:
            logging.error(f"PDF processing error: {e}")
            return func.HttpResponse(
                json.dumps({"error": "Unable to process PDF data"}),
                status_code=500,
                headers={"Content-Type": "application/json"}
            )

        text_content = []
        for page in reader.pages:
            try:
                extracted_text = page.extract_text()
                if extracted_text:
                    text_content.append(extracted_text)
            except Exception as e:
                logging.error(f"Error extracting text from page: {e}")
                return func.HttpResponse(
                    json.dumps({"error": "Unable to extract text from PDF page"}),
                    status_code=500,
                    headers={"Content-Type": "application/json"}
                )

        extracted_text = ' '.join(text_content)
        logging.info(f"Extracted Text: {extracted_text}")

        try:
            cleaned_text = clean_extracted_text(extracted_text)  # Add post-processing step
            logging.info(f"Cleaned Text: {cleaned_text}")
        except Exception as e:
            logging.error(f"Error cleaning extracted text: {e}")
            return func.HttpResponse(
                json.dumps({"error": "Unable to clean extracted text"}),
                status_code=500,
                headers={"Content-Type": "application/json"}
            )

        return func.HttpResponse(
            json.dumps({"extractedText": cleaned_text}),
            status_code=200,
            headers={"Content-Type": "application/json"}
        )
    except Exception as e:
        logging.exception("Unhandled exception during PDF processing")
        return func.HttpResponse(
            json.dumps({"error": "Server error"}),
            status_code=500,
            headers={"Content-Type": "application/json"}
        )

def clean_extracted_text(text):
    # Regular expression to remove unintended spaces and newline characters between digits and characters
    cleaned_text = re.sub(r'(\b\w{2,})(?:\s*|\n)(-\d{2})(?:\s*|\n)(-\w+)', r'\1\2\3', text)
    return cleaned_text
