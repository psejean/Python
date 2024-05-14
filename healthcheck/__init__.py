import logging
import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Health check endpoint hit.')
    return func.HttpResponse("Service is online", status_code=200)
