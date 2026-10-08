# Bulk Certificate Generator Backend

This is a beginner-friendly backend API built with **Python**, **FastAPI**, **SQLite**, and **ReportLab**. It accepts bulk requests to generate PDF certificates, processes them asynchronously, and provides endpoints to track status and download the final files.

## Project Structure Explained

*   `app/main.py`: The entry point. Contains the FastAPI app, API routing logic, and the `BackgroundTasks` function that generates PDFs without making the user wait.
*   `app/models.py`: Uses SQLAlchemy to define our database tables (`bulk_requests` and `recipients`). It creates the SQLite database automatically.
*   `app/schemas.py`: Uses Pydantic to validate data. For example, it ensures that every recipient submitted has a valid email format.
*   `app/database.py`: Handles connecting to the local `certificates.db` SQLite database and managing sessions.
*   `app/generator.py`: Uses the `ReportLab` library to programmatically draw and save the PDF certificate.
*   `requirements.txt`: Lists the Python libraries required to run this project.
*   `certificates/`: A folder that will be automatically created to store the output PDFs.

## How to Run

1.  **Open your terminal** and navigate to this project folder.
2.  **(Optional but recommended)** Create a virtual environment:
    ```bash
    python -m venv venv
    venv\Scripts\activate   # On Windows
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Start the Server:**
    ```bash
    uvicorn app.main:app --reload
    ```
    The server will start at `http://127.0.0.1:8000`.

## Interactive Documentation (Swagger UI)

FastAPI automatically generates interactive API documentation. Once the server is running, you can test everything directly in your browser by going to:
**[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

---

## Testing with Postman (Sample Requests)

If you prefer using Postman, here is how you can test the APIs:

### 1. Submit a Bulk Request
*   **Method:** `POST`
*   **URL:** `http://127.0.0.1:8000/api/requests/`
*   **Body Type:** `raw` -> `JSON`
*   **JSON Payload:**
    ```json
    {
      "title": "Python Basics Bootcamp 2024",
      "recipients": [
        {
          "name": "Alice Smith",
          "email": "alice@example.com"
        },
        {
          "name": "Bob Jones",
          "email": "bob@example.com"
        },
        {
          "name": "Charlie Brown",
          "email": "charlie@example.com"
        }
      ]
    }
    ```
*   **What it does:** Saves the data and immediately returns the request ID while generating PDFs in the background.

### 2. Check Request Status
*   **Method:** `GET`
*   **URL:** `http://127.0.0.1:8000/api/requests/1` *(replace `1` with the ID from step 1)*
*   **What it does:** Returns the current status (`PENDING`, `PROCESSING`, or `COMPLETED`) of the bulk request and every individual recipient.

### 3. Download a Certificate
*   **Method:** `GET`
*   **URL:** `http://127.0.0.1:8000/api/certificates/1/download` *(replace `1` with the recipient's ID found in step 2)*
*   **What it does:** Directly downloads the generated PDF file.
