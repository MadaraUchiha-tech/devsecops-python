"""Business metrics exported next to the HTTP metrics on /metrics."""

from prometheus_client import Counter

appointments_booked = Counter(
    "careslot_appointments_booked_total",
    "Appointments booked, labelled by doctor specialty",
    ["specialty"],
)
appointment_transitions = Counter(
    "careslot_appointment_status_changes_total",
    "Appointment status transitions",
    ["to_status"],
)
booking_conflicts = Counter(
    "careslot_booking_conflicts_total",
    "Bookings rejected because the doctor was already booked",
)
