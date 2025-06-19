# Image to PDF Converter Azure Function

This project provides an HTTP-triggered Azure Function to convert one or more uploaded image files into a single PDF document. It's designed to be a secure and straightforward solution for server-side PDF generation from images.

## Features

*   Converts one or more images to a single PDF.
*   Supports various common image formats (thanks to the underlying Pillow library used by `img2pdf`).
*   Secure endpoint using Bearer Token authentication.
*   Returns the generated PDF as a downloadable attachment.
*   Provides informative error messages for common issues.

## Requirements

*   Python 3.9+ (or as supported by Azure Functions)
*   Azure Functions Core Tools (for local development)
*   Dependencies:
    *   `azure-functions`
    *   `img2pdf`

## Setup and Deployment

This is an Azure Function App project.

1.  **Deployment:** Deploy the function to Azure using your preferred method (e.g., Azure CLI, VS Code Azure Functions extension, Azure DevOps/GitHub Actions).
2.  **Configure Authentication Token:**
    *   In the Azure portal, navigate to your Function App's configuration settings.
    *   Add a new Application Setting named `EXPECTED_BEARER_TOKEN`.
    *   Set its value to your desired secret bearer token. This token will be required by clients to access the function.

## Usage

To use the function, make a POST request to the `/img2pdf` endpoint.

**Headers:**

*   `Authorization`: `Bearer YOUR_TOKEN_HERE` (Replace `YOUR_TOKEN_HERE` with the actual configured bearer token)
*   `Content-Type`: `multipart/form-data` (usually handled by the client, like `curl`, automatically when sending files)

**Body:**

*   Send one or more image files as parts of the `multipart/form-data` request. Each part should be a file.

**Example using `curl`:**

```bash
curl -X POST \
     -H "Authorization: Bearer YOUR_SECRET_TOKEN" \
     -F "image1=@/path/to/your/first_image.jpg" \
     -F "image2=@/path/to/your/second_image.png" \
     -o "output.pdf" \
     <YOUR_FUNCTION_APP_URL>/api/img2pdf
```

Replace `/path/to/your/first_image.jpg`, `/path/to/your/second_image.png`, `YOUR_SECRET_TOKEN`, and `<YOUR_FUNCTION_APP_URL>` with your actual values. The output PDF will be saved to `output.pdf`.

## Error Handling

The function returns standard HTTP status codes for errors:

*   **400 Bad Request:**
    *   No image files provided in the request.
    *   Uploaded files are empty or not valid images.
    *   One or more images contain an alpha channel (transparency), which `img2pdf` does not support directly. Convert to JPG or remove transparency first.
*   **401 Unauthorized:**
    *   Missing `Authorization` header.
    *   `Authorization` header does not use the `Bearer` scheme.
    *   The provided token is invalid or does not match the `EXPECTED_BEARER_TOKEN`.
*   **500 Internal Server Error:**
    *   `EXPECTED_BEARER_TOKEN` is not configured on the server.
    *   The resulting PDF would be too large (`img2pdf.PdfTooBigError`).
    *   An unexpected error occurred during processing. Check the function logs for details.

## How to Run Locally

1.  **Clone the repository.**
2.  **Install Azure Functions Core Tools** if you haven't already.
3.  **Navigate to the project directory.**
4.  **Create `local.settings.json` file:**
    This file is used to store local environment settings and is not checked into source control (ensure it's in your `.gitignore`).
    ```json
    {
      "IsEncrypted": false,
      "Values": {
        "AzureWebJobsStorage": "", // Optional: for other Azure Functions features, not strictly needed for this HTTP trigger
        "FUNCTIONS_WORKER_RUNTIME": "python",
        "EXPECTED_BEARER_TOKEN": "YOUR_LOCAL_TEST_TOKEN" // Replace with a token for local testing
      }
    }
    ```
5.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
6.  **Run the function app:**
    ```bash
    func start
    ```
    The function will be available at `http://localhost:7071/api/img2pdf` by default.
