from django.test import TestCase, Client
from django.urls import reverse
from datetime import date
from decimal import Decimal
from .models import SLTransactionProduction

class ProductionReportTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('production_report')
        
        # Create Dummy Data
        # Record 1: Printing, Machine P1, 1000m, 100kg, 60min
        SLTransactionProduction.objects.create(
            trans_date=date(2023, 7, 1),
            trans_type='31', # Printing
            machine_code='P1',
            job_no='JOB-001',
            posted='True',
            meters=Decimal('1000.00'),
            final_farword_wt=Decimal('100.00'), # Production Kg
            wastage=Decimal('5.00'),
            total_production_minute=Decimal('60.00')
        )
        
        # Record 2: Printing, Machine P1, 2000m, 200kg, 60min
        SLTransactionProduction.objects.create(
            trans_date=date(2023, 7, 1),
            trans_type='31', # Printing
            machine_code='P1',
            job_no='JOB-002',
            posted='True',
            meters=Decimal('2000.00'),
            final_farword_wt=Decimal('200.00'), # Production Kg
            wastage=Decimal('10.00'),
            total_production_minute=Decimal('60.00')
        )
        
        # Record 3: Slitting, Machine S1
        SLTransactionProduction.objects.create(
            trans_date=date(2023, 7, 1),
            trans_type='34', # Slitting
            machine_code='S1',
            job_no='JOB-003',
            posted='True',
            meters=Decimal('500.00'),
            final_farword_wt=Decimal('50.00'),
            wastage=Decimal('2.00'),
            total_production_minute=Decimal('30.00')
        )

    def test_report_view_status(self):
        """Test if the view returns 200 OK"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_report_filtering(self):
        """Test filtering by date and process"""
        # Filter for Printing only
        response = self.client.get(self.url, {
            'start_date': '2023-07-01',
            'end_date': '2023-07-01',
            'processes': ['31'], # Printing
            'report_type': 'summary'
        })
        
        context_data = response.context['report_data']
        self.assertEqual(len(context_data), 1) # Only one process group
        self.assertEqual(context_data[0]['name'], 'Printing')
        
        # Check totals
        # Total meters = 1000 + 2000 = 3000
        # Total minutes = 60 + 60 = 120
        # Avg speed = 3000 / 120 = 25 m/min
        self.assertEqual(context_data[0]['total_meters'], Decimal('3000.00'))
        self.assertEqual(context_data[0]['total_minutes'], Decimal('120.00'))
        self.assertEqual(context_data[0]['avg_speed'], Decimal('25.00'))
        
        # Verify it's NOT checking Slitting
        response_slitting = self.client.get(self.url, {
            'start_date': '2023-07-01',
            'end_date': '2023-07-01',
            'processes': ['34'], # Slitting
            'report_type': 'summary'
        })
        context_slitting = response_slitting.context['report_data']
        self.assertEqual(context_slitting[0]['name'], 'Slitting')
        self.assertEqual(context_slitting[0]['total_meters'], Decimal('500.00'))

    def test_average_logic(self):
        """Verify Average Speed is calculated from Totals, not avg of averages"""
        # P1 Run 1 Speed = 1000/60 = 16.66
        # P1 Run 2 Speed = 2000/60 = 33.33
        # Average of Speeds = (16.66 + 33.33) / 2 = 25.00
        # Total calculation = 3000 / 120 = 25.00
        
        # Let's add a skewed record to really test it
        # Record 4: Printing, P1, 100m in 100 mins (Speed = 1)
        SLTransactionProduction.objects.create(
            trans_date=date(2023, 7, 1),
            trans_type='31',
            machine_code='P1',
            meters=Decimal('100.00'),
            total_production_minute=Decimal('100.00'),
            posted='True'
        )
        
        # New Totals:
        # Meters: 3000 + 100 = 3100
        # Minutes: 120 + 100 = 220
        # True Avg Speed = 3100 / 220 = 14.09
        
        # Wrong Avg of Avg:
        # (16.66 + 33.33 + 1) / 3 = 17.0
        
        response = self.client.get(self.url, {
            'start_date': '2023-07-01',
            'end_date': '2023-07-01',
            'processes': ['31'],
            'report_type': 'summary'
        })
        
        if not response.context['report_data']:
             print("Form Errors:", response.context['form'].errors)

        data = response.context['report_data'][0]['machines'][0] # P1
        
        # Using AlmostEqual because of potential float/decimal precision nuance
        self.assertAlmostEqual(float(data['avg_speed']), 14.09, places=1)
