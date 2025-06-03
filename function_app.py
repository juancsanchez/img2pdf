import azure.functions as func
import logging
import img2pdf
import io
import os # Import the 'os' module to access environment variables

# This initializes your Function App.
# We keep http_auth_level=func.AuthLevel.ANONYMOUS because we are implementing
# our own custom bearer token authentication logic within the function code.
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="img2pdf", methods=["POST"])
def image_to_pdf_converter(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function (v2 model) received a request for img2pdf.')

    # --- Bearer Token Authentication ---
    expected_token = os.environ.get("EXPECTED_BEARER_TOKEN")

    if not expected_token:
        logging.error("CRITICAL: EXPECTED_BEARER_TOKEN is not configured in application settings.")
        # This is a server configuration issue.
        return func.HttpResponse("Server configuration error: Authentication token not set.", status_code=500)

    auth_header = req.headers.get("Authorization")

    if not auth_header:
        logging.warning("Unauthorized: Missing Authorization header.")
        return func.HttpResponse("Unauthorized: Authorization header is required.", status_code=401)

    if not auth_header.startswith("Bearer "):
        logging.warning("Unauthorized: Authorization header must start with 'Bearer '.")
        return func.HttpResponse("Unauthorized: Invalid token format. Expected Bearer token.", status_code=401)

    provided_token = auth_header[len("Bearer "):] # Extract the token part after "Bearer "

    if provided_token != expected_token:
        logging.warning(f"Unauthorized: Invalid token provided.")
        return func.HttpResponse("Unauthorized: Invalid token.", status_code=401)
    
    logging.info('Bearer token validated successfully.')
    # --- End Bearer Token Authentication ---

    # If authentication is successful, proceed with the rest of the function logic
    try:
        uploaded_files = req.files.values()

        if not uploaded_files:
            logging.warning("No files were uploaded after successful authentication.")
            return func.HttpResponse(
                 "Please pass one or more image files in the request body using multipart/form-data.",
                 status_code=400
            )

        image_bytes_list = []
        image_filenames = []

        for file_storage in uploaded_files:
            filename = file_storage.filename
            file_bytes = file_storage.read()

            if not file_bytes:
                logging.warning(f"Uploaded file {filename} is empty.")
                continue

            image_bytes_list.append(file_bytes)
            image_filenames.append(filename)
            logging.info(f"Successfully read file: {filename}, size: {len(file_bytes)} bytes")

        if not image_bytes_list:
            logging.error("No valid image data could be read from the uploaded files.")
            return func.HttpResponse(
                "No valid image data found in the uploaded files.",
                status_code=400
            )

        logging.info(f"Attempting to convert {len(image_bytes_list)} image(s) to PDF.")
        pdf_bytes = img2pdf.convert(image_bytes_list)

        if len(image_filenames) == 1:
            base_filename = image_filenames[0].rsplit('.', 1)[0] if '.' in image_filenames[0] else image_filenames[0]
        else:
            base_filename = "converted_document"
        pdf_filename = f"{base_filename}.pdf"

        logging.info(f"PDF conversion successful. Output size: {len(pdf_bytes)} bytes. Suggested filename: {pdf_filename}")

        return func.HttpResponse(
            pdf_bytes,
            status_code=200,
            mimetype="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=\"{pdf_filename}\""
            }
        )

    except img2pdf.PdfTooBigError:
        logging.error("Error converting to PDF: The resulting PDF would be too large.")
        return func.HttpResponse(
            "Error converting to PDF: The resulting PDF would be too large.",
            status_code=500
        )
    except img2pdf.AlphaChannelError:
        logging.error("Error converting to PDF: One or more images have an alpha channel (transparency).")
        return func.HttpResponse(
            "Error converting to PDF: One or more images have an alpha channel. Try converting to JPG or removing transparency.",
            status_code=400
        )
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True)
        return func.HttpResponse(
             f"An unexpected error occurred processing your request.",
             status_code=500
        )