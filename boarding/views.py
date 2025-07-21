from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import UploadCSVForm
import csv
from io import TextIOWrapper, StringIO
from django.http import HttpResponse

# Create your views here.

def upload_csv(request):
    warning = None
    if request.method == 'POST':
        form = UploadCSVForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = form.cleaned_data['csv_file']
            decoded_file = TextIOWrapper(csv_file, encoding='utf-8')
            reader = csv.reader(decoded_file)
            header = next(reader, None)
            bookings = []
            for row in reader:
                if len(row) < 2 or not row[1].strip():
                    warning = 'Some bookings had empty seat lists and were skipped.'
                    continue
                booking_id = int(row[0])
                seats = [s.strip() for s in row[1].split(',') if s.strip()]
                if not seats:
                    warning = 'Some bookings had empty seat lists and were skipped.'
                    continue
                bookings.append({'booking_id': booking_id, 'seats': seats})
            request.session['bookings'] = bookings
            return redirect(reverse('boarding:result'))
    else:
        form = UploadCSVForm()
    return render(request, 'boarding/upload.html', {'form': form, 'warning': warning})

def get_row_label(seat):
    # Extract row letter (A-Z) from seat label like A1, B4, etc.
    return seat[0].upper() if seat and seat[0].isalpha() else 'Z'

def result(request):
    bookings = request.session.get('bookings', [])
    sequence = []
    for booking in bookings:
        # Find the closest seat row for this booking
        min_row = min([get_row_label(seat) for seat in booking['seats']])
        sequence.append({'booking_id': booking['booking_id'], 'row': min_row})
    # Sort: first by row (A-Z), then by booking_id
    sequence.sort(key=lambda x: (x['row'], x['booking_id']))
    # Add sequence number
    for idx, item in enumerate(sequence, 1):
        item['seq'] = idx
    return render(request, 'boarding/result.html', {'sequence': sequence})

def download_csv(request):
    bookings = request.session.get('bookings', [])
    sequence = []
    for booking in bookings:
        min_row = min([get_row_label(seat) for seat in booking['seats']])
        sequence.append({'booking_id': booking['booking_id'], 'row': min_row})
    sequence.sort(key=lambda x: (x['row'], x['booking_id']))
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Seq', 'Booking_ID'])
    for idx, item in enumerate(sequence, 1):
        writer.writerow([idx, item['booking_id']])
    response = HttpResponse(output.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=boarding_sequence.csv'
    return response
