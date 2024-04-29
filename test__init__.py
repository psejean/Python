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
            return func.HttpResponse("Missing PDF data", status_code=400)

        # Decode the base64 string to bytes
        pdf_bytes = base64.b64decode(base64_pdf)
        
        # Read the PDF
        reader = PdfReader()
        reader.stream = pdf_bytes
        text_content = []

        # Extract text from each page
        for page in reader.pages:
            text_content.append(page.extract_text())

        # Join all text from all pages
        extracted_text = ' '.join(text_content)

        return func.HttpResponse(extracted_text, status_code=200)
    except Exception as e:
        return func.HttpResponse(f"Error processing PDF: {str(e)}", status_code=500)
