import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from rest_framework.exceptions import ValidationError

from hotel_reservation.models import Room
from django.db.models import Q

from datetime import datetime

#Returns the rooms that are occupied for these dates
def get_the_room_for_diferent_days(start_date, end_date, key=None):
    return Room.objects.filter(
        Q(room_reservations__reservation__start_date__gte=start_date,
          room_reservations__reservation__start_date__lt=end_date) |
        Q(room_reservations__reservation__end_date__gt=start_date,
          room_reservations__reservation__end_date__lte=end_date) |
        Q(room_reservations__reservation__start_date__lte=start_date,
          room_reservations__reservation__end_date__gte=end_date),
        room_type_id=key
    ) if key else Room.objects.filter(
        Q(room_reservations__reservation__start_date__gte=start_date,
          room_reservations__reservation__start_date__lt=end_date) |
        Q(room_reservations__reservation__end_date__gt=start_date,
          room_reservations__reservation__end_date__lte=end_date) |
        Q(room_reservations__reservation__start_date__lte=start_date,
          room_reservations__reservation__end_date__gte=end_date))

def check_if_specific_room_is_reserved(room_id, start_date, end_date, reservation_id):
    return Room.objects.filter(
        Q(room_reservations__reservation__start_date__gte=start_date,
          room_reservations__reservation__start_date__lt=end_date) |
        Q(room_reservations__reservation__end_date__gt=start_date,
          room_reservations__reservation__end_date__lte=end_date) |
        Q(room_reservations__reservation__start_date__lte=start_date,
          room_reservations__reservation__end_date__gte=end_date),
        ~Q(room_reservations__reservation_id=reservation_id), id=room_id).exists()


def check_if_room_is_free(room_types: [], start_date: str, end_date: str):
    for element in room_types:
        query_set_size = len(Room.objects.filter(room_type_id=element['id']))

        # reservation_query_set = Reservation.objects.filter(
        #     Q(start_date__gte=start_date, start_date__lt=end_date) |
        #     Q(end_date__gte=start_date,
        #       end_date__lt=end_date) |
        #     Q(start_date__lte=start_date, end_date__gt=end_date),
        #     room_reservations__room__room_type__type_name=key
        # ).values_list('room_reservations__room_id', flat=True)

        room_query_set = get_the_room_for_diferent_days(start_date, end_date, element.get('id'))

        if (len(room_query_set) + element.get('count')) > query_set_size:
            raise ValidationError("No Rooms in these days")

def parse_to_date_time_dd_mm_yy_version(date_in_string: str):
    return datetime.strptime(date_in_string, "%d/%m/%Y").date()

def send_email(receiver):
    # Email configuration
    sender_email = "erlikuka025@gmail.com"
    sender_password = "ohfxgzueyqzyzdqs"
    recipient_email = receiver
    subject = "Welcome!!!"
    message_body = '''
        Mireseerdhet!!! Faleminderit qe jeni pjese e Tirana Bars! 
    '''

    # Create the MIME object
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message_body, 'plain'))

    # Connect to Gmail's SMTP server
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)

        # Send email
        server.sendmail(sender_email, recipient_email, msg.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print("Error sending email:", str(e))