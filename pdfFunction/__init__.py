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
            raise

        # Initialize the PDF Reader with the byte stream
        reader = PdfReader()
        reader.stream = pdf_bytes  # Ensure that this assignment is valid
        text_content = []

        # Extract text from each page
        for page_number, page in enumerate(reader.pages, start=1):
            try:
                page_text = page.extract_text()
                if page_text:  # Ensure there's text on the page
                    text_content.append(page_text)
                else:
                    logging.warning(f"No text found on page {page_number}.")
            except Exception as e:
                logging.error(f"Error extracting text from page {page_number}: {e}")
                raise

        # Join all text from all pages
        extracted_text = ' '.join(text_content)

        if not extracted_text.strip():  # Check if the extracted text is not just whitespace
            logging.warning("Extracted text is empty after processing all pages.")
        
        return func.HttpResponse(extracted_text, status_code=200)
    except Exception as e:
        # Log the exception with the stack trace for better diagnosis
        logging.exception("An error occurred while processing the PDF.")
        # It's generally a good practice to return a generic error message to the client, 
        # especially if the details are sensitive or could expose vulnerabilities.
        return func.HttpHttpResponse("An error occurred during processing.", status_code=500)
