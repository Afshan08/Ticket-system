import os
import django
import sys

# Setup Django Environment
sys.path.append('c:\\Ticket-system\\ticket_system')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ticket_system.settings')
django.setup()

from reports.models import SLTransactionProduction

print("--- Inspecting SLTransactionProduction Data ---")

print("\n1. Distinct 'posted' values:")
try:
    posted_values = SLTransactionProduction.objects.values_list('posted', flat=True).distinct()
    print(list(posted_values))
except Exception as e:
    print(f"Error fetching posted: {e}")

print("\n2. Distinct 'trans_type' values:")
try:
    trans_types = SLTransactionProduction.objects.values_list('trans_type', flat=True).distinct()
    print(list(trans_types))
except Exception as e:
    print(f"Error fetching trans_type: {e}")

print("\n3. Sample Data (First 5 records):")
try:
    sample = SLTransactionProduction.objects.all().order_by('-trans_date')[:5]
    for p in sample:
        print(f"Date: {p.trans_date}, Type: {p.trans_type}, Posted: '{p.posted}', Job: {p.job_no}")
except Exception as e:
    print(f"Error fetching sample: {e}")
