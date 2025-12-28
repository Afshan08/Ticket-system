import os
import django
import sys

# Setup Django Environment
sys.path.append('c:\\Ticket-system')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ticket_system.settings')
django.setup()

try:
    print("Attempting to import reports.forms...")
    from ticket_system.reports.forms import ProductionReportForm
    print("Success: Imported ProductionReportForm")

    print("Attempting to import reports.views...")
    from ticket_system.reports import views
    print("Success: Imported reports.views")

    print("Attempting to resolve URL...")
    from django.urls import resolve
    match = resolve('/reports/production/')
    print(f"Success: Resolved URL /reports/production/ to {match.func.__name__}")

    print("Verification Passed!")
except Exception as e:
    print(f"Verification Failed: {e}")
