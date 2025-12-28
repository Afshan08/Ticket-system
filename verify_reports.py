import os
import django
import sys
import unittest
from unittest.mock import patch
from django.test import RequestFactory
from decimal import Decimal

# Set up Django
sys.path.append('c:\\Ticket-system\\ticket_system')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ticket_system.settings')
django.setup()

from reports.models import SLJobMaster, SLTransactionProduction
from reports.views import production_dashboard_view, job_progress_view
from django.db.models import Sum

class TestReportDataAccuracy(unittest.TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_dashboard_kpis(self):
        """Verify that dashboard KPIs match direct DB sums."""
        # We mock render to intercept the context passed to the template
        with patch('reports.views.render') as mocked_render:
            request = self.factory.get('/reports/dashboard/')
            production_dashboard_view(request)
            
            # Get context from the render call: render(request, template, context)
            args, kwargs = mocked_render.call_args
            context = args[2] if len(args) > 2 else kwargs.get('context')
            
            # Calculate expected values manually
            latest_trans = SLTransactionProduction.objects.order_by('-trans_date').first()
            ref_date = latest_trans.trans_date
            first_day = ref_date.replace(day=1)
            
            expected_prod = SLTransactionProduction.objects.filter(
                trans_date__gte=first_day, trans_date__lte=ref_date
            ).aggregate(s=Sum('final_farword_wt'))['s'] or Decimal(0)
            
            print(f"DEBUG: Produced in {ref_date.strftime('%B %Y')}: {expected_prod}")
            self.assertAlmostEqual(float(context['total_production']), float(expected_prod), places=2)

    def test_job_progress_stages(self):
        """Verify that job progress logic correctly identifies stages."""
        with patch('reports.views.render') as mocked_render:
            request = self.factory.get('/reports/progress/')
            job_progress_view(request)
            
            args, kwargs = mocked_render.call_args
            context = args[2] if len(args) > 2 else kwargs.get('context')
            
            for item in context['jobs'][:5]:
                job_no = item['job_no']
                trans = SLTransactionProduction.objects.filter(job_no=job_no).values_list('trans_type', flat=True)
                
                if '34' in trans:
                    self.assertEqual(item['stage'], 'Completed')
                    self.assertEqual(item['progress'], 100)
                elif '31' in trans:
                    # If it has printing but not slitting, it should be at some stage > 0 but < 100
                    self.assertTrue(0 < item['progress'] < 100)
                
                print(f"DEBUG: Job {job_no} -> Stage: {item['stage']}, Progress: {item['progress']}%")

if __name__ == "__main__":
    unittest.main()
