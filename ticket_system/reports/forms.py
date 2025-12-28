from django import forms
from datetime import date

class ProductionReportForm(forms.Form):
    PROCESS_CHOICES = [
        ('31', 'Printing'),
        ('33', 'Lamination'),
        ('34', 'Slitting'),
        ('32', 'Rewinding'),
    ]

    REPORT_TYPE_CHOICES = [
        ('summary', 'Summary'),
        ('detail', 'Detail'),
        ('job_wise', 'Job-wise'),
        ('machine_wise', 'Machine-wise'),
    ]

    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        initial=date.today
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        initial=date.today
    )
    processes = forms.MultipleChoiceField(
        choices=PROCESS_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label="Select Processes",
        initial=['31', '33', '34', '32']
    )
    report_type = forms.ChoiceField(
        choices=REPORT_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        initial='summary'
    )
    # Optional Filters
    job_no = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional Job No'})
    )
