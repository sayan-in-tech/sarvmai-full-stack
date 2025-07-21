import csv
from fastapi import FastAPI, Request, UploadFile, Form
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from starlette.background import BackgroundTask
from pathlib import Path
from typing import List
import io

app = FastAPI()

# Static files
app.mount("/static/boarding", StaticFiles(directory="boarding/static/boarding"), name="static-boarding")

# Templates
templates = Jinja2Templates(directory="boarding/templates/boarding")

# Boarding logic
ROW_ORDER = ['A', 'B', 'C', 'D']

def seat_key(seat: str):
    if not seat:
        return (len(ROW_ORDER), 100)
    row = seat[0].upper()
    try:
        row_idx = ROW_ORDER.index(row)
    except ValueError:
        row_idx = len(ROW_ORDER)
    try:
        num = int(seat[1:])
    except ValueError:
        num = 100
    return (row_idx, num)

def booking_sort_key(booking):
    # booking: (Booking_ID, [seats])
    seats = booking[1]
    if not seats:
        return (len(ROW_ORDER), 100, int(booking[0]))
    closest_seat = min(seats, key=seat_key)
    return (*seat_key(closest_seat), int(booking[0]))

def parse_csv(file: UploadFile) -> List[List[str]]:
    content = file.file.read().decode('utf-8')
    reader = csv.reader(io.StringIO(content))
    rows = list(reader)
    return rows

def process_bookings(rows: List[List[str]]):
    # Expects header: Booking_ID,Seats
    bookings = []
    for row in rows[1:]:
        if not row or not row[0]:
            continue
        booking_id = row[0]
        seats = [s.strip() for s in row[1:] if s.strip()]
        bookings.append((booking_id, seats))
    bookings = sorted(bookings, key=booking_sort_key)
    return bookings

def generate_csv(bookings):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Seq", "Booking_ID"])
    for i, (booking_id, _) in enumerate(bookings, 1):
        writer.writerow([i, booking_id])
    output.seek(0)
    return output

@app.get("/", response_class=HTMLResponse)
async def upload_form(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

@app.post("/", response_class=HTMLResponse)
async def upload_file(request: Request, file: UploadFile = Form(...)):
    rows = parse_csv(file)
    bookings = process_bookings(rows)
    # Save to session-like object (simulate with in-memory for now)
    request.state.bookings = bookings
    # Prepare data for template
    result = [(i+1, b[0]) for i, b in enumerate(bookings)]
    # Store CSV in memory for download
    csv_content = generate_csv(bookings).getvalue()
    request.state.csv_content = csv_content
    return templates.TemplateResponse("result.html", {"request": request, "result": result, "csv_ready": True})

@app.get("/result/", response_class=HTMLResponse)
async def result_page(request: Request):
    # This would normally use session or DB; here, just show upload page
    return RedirectResponse("/")

@app.get("/download/", response_class=StreamingResponse)
async def download_csv(request: Request):
    # In a real app, use session or DB; here, just return a sample
    bookings = [("103", ["A2"]), ("101", ["A1", "B1"]), ("120", ["A20", "C2"]), ("102", ["B2", "B3"])]
    output = generate_csv(bookings)
    response = StreamingResponse(iter([output.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=boarding_sequence.csv"
    return response 