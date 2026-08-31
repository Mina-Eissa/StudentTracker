import django.dispatch

# Each is sent with keyword args: (session=..., triggered_by=...) or
# (teacher_grade=..., triggered_by=...) for grade_assigned. Senders don't
# need to know or care who's listening — see receivers.py.

session_set = django.dispatch.Signal()       # a session was created (status=Pending)
session_started = django.dispatch.Signal()   # Pending -> Running
session_ended = django.dispatch.Signal()     # -> finished
grade_assigned = django.dispatch.Signal()    # a new teacher_grade row was created
