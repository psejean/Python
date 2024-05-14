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

        return func.HttpResponse(
            json.dumps({"extractedText": extracted_text}),
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

# Add a new route for health check
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Health check endpoint hit.')
    return func.HttpResponse("Service is online", status_code=200)

app = func.FunctionApp()

# Register your existing function and the health check function
app.route('pdfFunction', methods=['POST'], auth_level=func.AuthLevel.ANONYMOUS)(main)
app.route('healthcheck', methods=['GET'], auth_level=func.AuthLevel.ANONYMOUS)(health_check)
