# Flask Support Ticket REST API
A lightweight RESTful backend service built with Python, Flask, and SQLite for logging, filtering, and resolving production support incidents.

## API Endpoints
- `GET /` — Service health check (`200 OK`)
- `GET /tickets` — Retrieve all tickets (supports `?status=open` or `?status=resolved` query filter)
- `POST /tickets` — Create a new incident ticket with input validation (`201 Created` / `400 Bad Request`)
- `PATCH /tickets/<id>/resolve` — Mark an existing ticket as resolved (`200 OK` / `404 Not Found`)

## Setup & Run
1. Install dependencies: `pip install -r requirements.txt`
2. Start the server: `python app.py`
3. Access the API at `http://127.0.0.1:5000`
