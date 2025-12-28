import os
import django
import sys
from decimal import Decimal

# Set up Django
sys.path.append('c:\\Ticket-system\\ticket_system')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ticket_system.settings')
django.setup()

from reports.models import SLJobMaster, SLTransactionProduction
from reports.views import get_job_stage_info

def verify_active_jobs():
    print("--- Verifying jobs WITH transactions ---")
    # Finding jobs that appear in production transactions
    active_job_nos = SLTransactionProduction.objects.values_list('job_no', flat=True).distinct()[:10]
    
    for j_no in active_job_nos:
        progress, stage, color = get_job_stage_info(j_no)
        # Get transaction types for this job
        types = list(SLTransactionProduction.objects.filter(job_no=j_no).values_list('trans_type', flat=True).distinct())
        print(f"JobNo: {j_no}, Stage: {stage}, Progress: {progress}%, TransTypes: {types}")

if __name__ == "__main__":
    verify_active_jobs()
