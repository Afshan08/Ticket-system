import os
import sys
import django
from django.conf import settings
from django.test import RequestFactory

# Setup Django path
project_root = 'c:/Ticket-system/ticket_system'
if project_root not in sys.path:
    sys.path.append(project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ticket_system.settings')
django.setup()

from reports.views import production_report_view

# Construct the request with data using RequestFactory
factory = RequestFactory()
# 'processes' needs to be handled correctly as a list.
# RequestFactory handles lists in the data dict by treating them as multiple values.
data = {
    'start_date': '2023-08-08',
    'end_date': '2023-08-09',
    'processes': ['31', '33', '34', '32'],
    'report_type': 'summary', # Added required field
    'format': 'pdf'
}
request = factory.get('/reports/production_report/', data)

print("Running production_report_view with format='pdf'...")
try:
    response = production_report_view(request)
    print(f"Response Status Code: {response.status_code}")
    print(f"Content-Type: {response.get('Content-Type')}")
    
    if response.status_code == 200 and response.get('Content-Type') == 'application/pdf':
        print("SUCCESS: PDF generated successfully.")
        pdf_content = response.content
        print(f"PDF Size: {len(pdf_content)} bytes")
        with open('test_report.pdf', 'wb') as f:
            f.write(pdf_content)
        print("Saved to test_report.pdf")
    else:
        print("FAILURE: Response was not a PDF.")
        # Print form errors if form is invalid
        if hasattr(response, 'context_data'):
             form = response.context_data.get('form')
             if form and form.errors:
                 print("Form Errors:", form.errors)
        
        # Fallback to check content if it's HTML
        if hasattr(response, 'content'):
            print(f"Content start: {response.content[:100]}...")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
