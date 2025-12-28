import os
import django
import sys

# Set up Django environment
sys.path.append('c:\\Ticket-system\\ticket_system')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ticket_system.settings')
django.setup()

from reports.models import SLJobMaster, SLTransactionProduction
from django.db.models import Count, Sum

def inspect_data():
    print("\n--- Correlation: Jobs with Slitting (34) vs Status ---")
    slit_jobs = SLTransactionProduction.objects.filter(trans_type='34').values_list('job_no', flat=True).distinct()
    slit_status = SLJobMaster.objects.filter(job_no__in=slit_jobs).values('job_status').annotate(count=Count('job_status'))
    for entry in slit_status:
        print(f"Status for Slitted Jobs: {entry['job_status']}, Count: {entry['count']}")

    print("\n--- Deep Dive: Jobs with status -1 ---")
    neg_one_jobs = SLJobMaster.objects.filter(job_status='-1')
    for j in neg_one_jobs[:5]:
        t_count = SLTransactionProduction.objects.filter(job_no=j.job_no).count()
        print(f"JobNo: {j.job_no}, Transactions: {t_count}, Qty: {j.job_qty}")

    print("\n--- Identifying 'Completed' Jobs (Heuristic) ---")
    # ... existing code ...

    print("\n--- Checking for 'Posted' or 'Locked' flags ---")
    posted_counts = SLJobMaster.objects.values('posted').annotate(count=Count('posted'))
    print(f"JobMaster Posted: {posted_counts}")

if __name__ == "__main__":
    inspect_data()
