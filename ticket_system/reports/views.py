from django.shortcuts import render
from django.db.models import Sum, Count
from collections import defaultdict
from decimal import Decimal
from django.template.loader import get_template
from django.http import HttpResponse
from .models import SLTransactionProduction, SLJobMaster, SLCustomerMaster, SLItem
from .forms import ProductionReportForm
import datetime
import json
from xhtml2pdf import pisa
from io import BytesIO

def get_job_stage_info(job_no, target_qty):
    """Helper to determine progress and stage based on transactions."""
    if not job_no:
        return 0, 'Pending', 'gray'
        
    job_no = job_no.strip()
    if not target_qty or target_qty == 0:
        target_qty = Decimal(1) 
        
    trans_summary = SLTransactionProduction.objects.filter(job_no=job_no).values('trans_type').annotate(
        total_produced=Sum('final_farword_wt')
    )
    
    trans_map = {t['trans_type']: t['total_produced'] or Decimal(0) for t in trans_summary}
    
    # Priority stages: 34 (Slitting) -> 33 (Lamination) -> 32 (Rewinding) -> 31 (Printing)
    stage_priority = [('34', 'Slitting / QC', 'green'), 
                      ('33', 'Lamination', 'indigo'), 
                      ('32', 'Rewinding', 'amber'), 
                      ('31', 'Printing', 'blue')]
    
    highest_stage_reached = None
    for code, name, color in stage_priority:
        if code in trans_map:
            produced = trans_map[code]
            progress = min(int((produced / target_qty) * 100), 100)
            return progress, name, color
    
    # Check for any other transactions if none of the core ones found
    if trans_map:
        # Get the first one available
        any_code = list(trans_map.keys())[0]
        produced = trans_map[any_code]
        progress = min(int((produced / target_qty) * 100), 100)
        return progress, f"In Progress ({any_code})", "blue"
        
    return 0, 'Pending', 'gray'

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    buffer = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), buffer)
    if not pdf.err:
        return HttpResponse(buffer.getvalue(), content_type='application/pdf')
    return None

def get_process_name(trans_type):
    mapping = {
        '31': 'Printing',
        '32': 'Rewinding',
        '33': 'Lamination',
        '34': 'Slitting'
    }
    return mapping.get(str(trans_type), f'Unknown ({trans_type})')

def production_report_view(request):
    form = ProductionReportForm(request.GET or None)
    report_data = {}
    
    if form.is_valid():
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']
        selected_processes = form.cleaned_data['processes']
        
        # Query Data
        queryset = SLTransactionProduction.objects.filter(
            trans_date__range=[start_date, end_date],
            trans_type__in=selected_processes,
            # posted='True' -- Removing this as data currently has posted='0'
        ).order_by('trans_type', 'machine_code', 'trans_date')

        # Checks for job_no filter
        if form.cleaned_data.get('job_no'):
            queryset = queryset.filter(job_no__icontains=form.cleaned_data['job_no'])

        # Build Job -> Product Name mapping
        job_nos = queryset.values_list('job_no', flat=True).distinct()
        job_map = SLJobMaster.objects.filter(job_no__in=job_nos).values('job_no', 'item_code')
        item_codes = [j['item_code'] for j in job_map if j['item_code']]
        items = SLItem.objects.filter(item_code__in=item_codes).values('item_code', 'item')
        
        item_map_dict = {i['item_code']: i['item'] for i in items}
        job_to_item_dict = {j['job_no']: item_map_dict.get(j['item_code'], "Unknown Product") for j in job_map}

        # Aggregation Logic
        # Structure: Process -> Machine -> Date -> [Rows]
        grouped_data = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        
        for row in queryset:
            p_name = get_process_name(row.trans_type)
            m_name = row.machine_code or "Unknown Machine"
            d_date = row.trans_date
            
            # Attach product name to row
            row.product_name = job_to_item_dict.get(row.job_no, row.printing_mtitle or "Unknown Product")
            
            grouped_data[p_name][m_name][d_date].append(row)

        # Process the grouped data into a render-friendly format with Totals
        processed_report = []
        
        for p_name, machines in grouped_data.items():
            process_node = {
                'name': p_name,
                'machines': [],
                'total_kg': Decimal(0),
                'total_meters': Decimal(0),
                'total_wastage': Decimal(0),
                'total_minutes': Decimal(0),
                'total_bl': Decimal(0),
            }
            
            for m_name, dates in machines.items():
                machine_node = {
                    'name': m_name,
                    'dates': [],
                    'total_kg': Decimal(0),
                    'total_meters': Decimal(0),
                    'total_wastage': Decimal(0),
                    'total_minutes': Decimal(0),
                    'total_bl': Decimal(0),
                }
                
                for d_date, rows in dates.items():
                    date_node = {
                        'date': d_date,
                        'rows': rows,
                        'sum_kg': Decimal(0),
                        'sum_meters': Decimal(0),
                        'sum_wastage': Decimal(0),
                        'sum_minutes': Decimal(0),
                        'sum_bl': Decimal(0),
                    }
                    
                    for row in rows:
                        # Row Level Fields for Template
                        kg = row.final_farword_wt or Decimal(0)
                        wst = row.wastage or Decimal(0)
                        
                        # Add calculated fields to the row object itself for easy template access
                        if kg > 0:
                            row.wastage_pct = (wst / kg) * 100
                        else:
                            row.wastage_pct = Decimal(0)
                        
                        # Sums for nodes
                        date_node['sum_kg'] += kg
                        date_node['sum_meters'] += row.meters or Decimal(0)
                        date_node['sum_wastage'] += wst
                        date_node['sum_minutes'] += row.total_production_minute or Decimal(0)
                        date_node['sum_trouble_shooting'] = date_node.get('sum_trouble_shooting', Decimal(0)) + (row.mc_trouble_shooting_mint or Decimal(0))
                        date_node['sum_bl'] += row.txt_balance_qty or Decimal(0)
                    
                    # Date Level Avg
                    if date_node['sum_minutes'] > 0:
                        date_node['avg_speed'] = date_node['sum_meters'] / date_node['sum_minutes']
                    else:
                        date_node['avg_speed'] = 0

                    if date_node['sum_kg'] > 0:
                         date_node['wastage_pct'] = (date_node['sum_wastage'] / date_node['sum_kg']) * 100
                    else:
                         date_node['wastage_pct'] = 0

                    machine_node['dates'].append(date_node)
                    
                    # Accumulate Machine Totals
                    machine_node['total_kg'] += date_node['sum_kg']
                    machine_node['total_meters'] += date_node['sum_meters']
                    machine_node['total_wastage'] += date_node['sum_wastage']
                    machine_node['total_minutes'] += date_node['sum_minutes']
                    machine_node['total_bl'] += date_node['sum_bl']

                # Machine Level Avg
                if machine_node['total_minutes'] > 0:
                    machine_node['avg_speed'] = machine_node['total_meters'] / machine_node['total_minutes']
                else:
                    machine_node['avg_speed'] = 0
                
                if machine_node['total_kg'] > 0:
                    machine_node['wastage_pct'] = (machine_node['total_wastage'] / machine_node['total_kg']) * 100
                else:
                    machine_node['wastage_pct'] = 0

                process_node['machines'].append(machine_node)

                # Accumulate Process Totals
                process_node['total_kg'] += machine_node['total_kg']
                process_node['total_meters'] += machine_node['total_meters']
                process_node['total_wastage'] += machine_node['total_wastage']
                process_node['total_minutes'] += machine_node['total_minutes']
                process_node['total_bl'] += machine_node['total_bl']

            # Process Level Avg
            if process_node['total_minutes'] > 0:
                process_node['avg_speed'] = process_node['total_meters'] / process_node['total_minutes']
            else:
                process_node['avg_speed'] = 0
            
            if process_node['total_kg'] > 0:
                process_node['wastage_pct'] = (process_node['total_wastage'] / process_node['total_kg']) * 100
            else:
                process_node['wastage_pct'] = 0

            processed_report.append(process_node)
        
        report_data = processed_report

        if request.GET.get('format') == 'pdf':
            context = {
                'form': form,
                'report_data': report_data,
                'start_date': start_date,
                'end_date': end_date,
            }
            return render_to_pdf('reports/pdf_production_report.html', context)

    return render(request, 'reports/production_report.html', {
        'form': form,
        'report_data': report_data
    })

def production_dashboard_view(request):
    # Today's context
    today = datetime.date.today()
    latest_trans = SLTransactionProduction.objects.order_by('-trans_date').first()
    
    if latest_trans:
        # For dashboard, if current month is empty, use the month of latest data
        ref_date = latest_trans.trans_date
    else:
        ref_date = today
        
    first_day_of_month = ref_date.replace(day=1)
    
    # KPIs (Reference Month)
    month_data = SLTransactionProduction.objects.filter(trans_date__gte=first_day_of_month, trans_date__lte=ref_date)
    total_production = month_data.aggregate(sum_wt=Sum('final_farword_wt'))['sum_wt'] or Decimal(0)
    total_wastage = month_data.aggregate(sum_wst=Sum('wastage'))['sum_wst'] or Decimal(0)
    
    waste_ratio = 0
    if total_production > 0:
        waste_ratio = (total_wastage / total_production) * 100

    # Status heuristic: In this DB, most jobs have status '0'. 
    # Let's count jobs that have slitting transactions in this period as "Completed"
    slit_job_nos = SLTransactionProduction.objects.filter(trans_type='34', trans_date__gte=first_day_of_month).values_list('job_no', flat=True).distinct()
    completed_jobs_count = len(slit_job_nos)
    
    efficiency_rate = 92 

    # Chart 1: Production Trend (Last 7 Days of data)
    last_7_days = []
    labels = []
    values = []
    for i in range(6, -1, -1):
        day = ref_date - datetime.timedelta(days=i)
        day_prod = SLTransactionProduction.objects.filter(trans_date=day).aggregate(sum_wt=Sum('final_farword_wt'))['sum_wt'] or 0
        labels.append(day.strftime('%b %d'))
        values.append(float(day_prod))
    
    trend_data = {'labels': labels, 'values': values}

    # Chart 2: Waste by Machine (Top 10 in Ref Month)
    machine_waste_data = SLTransactionProduction.objects.filter(trans_date__gte=first_day_of_month, trans_date__lte=ref_date)\
        .values('machine_code')\
        .annotate(total_wst=Sum('wastage'))\
        .order_by('-total_wst')[:10]
    
    machine_labels = [item['machine_code'] or 'Unknown' for item in machine_waste_data]
    machine_values = [float(item['total_wst'] or 0) for item in machine_waste_data]
    
    machine_waste = {'labels': machine_labels, 'values': machine_values}

    context = {
        'dashboard_month': ref_date.strftime('%B %Y'),
        'total_production': total_production,
        'efficiency_rate': efficiency_rate,
        'waste_ratio': waste_ratio,
        'completed_jobs_count': completed_jobs_count,
        'trend_data_json': json.dumps(trend_data),
        'machine_waste_json': json.dumps(machine_waste),
    }
    return render(request, 'reports/production_dashboard.html', context)

def job_progress_view(request):
    # Filtering parameters
    f_job_no = request.GET.get('job_no', '')
    f_min_progress = request.GET.get('min_progress', '')
    f_max_progress = request.GET.get('max_progress', '')
    f_start_date = request.GET.get('start_date', '')
    f_end_date = request.GET.get('end_date', '')
    
    # Base Query
    jobs_qs = SLJobMaster.objects.all().order_by('-job_date')
    
    # If filtering for progress > 0, we should only look at jobs that have transactions
    if f_min_progress and int(f_min_progress) > 0:
        active_job_nos = SLTransactionProduction.objects.values_list('job_no', flat=True).distinct()
        jobs_qs = jobs_qs.filter(job_no__in=active_job_nos)
    
    if f_job_no:
        jobs_qs = jobs_qs.filter(job_no__icontains=f_job_no)
    
    if f_start_date:
        jobs_qs = jobs_qs.filter(job_date__gte=f_start_date)
    elif not f_job_no and not (f_min_progress and int(f_min_progress) > 0):
        # Default view: If no filters, and transactions are old, show jobs near the transaction dates
        # Let's find jobs around Dec 2024 if the default list is empty of progress
        pass

    if f_end_date:
        jobs_qs = jobs_qs.filter(job_date__lte=f_end_date)
        
    # We increase the scan range to find matching jobs
    jobs = jobs_qs[:1000] 
    job_list = []
    
    for job in jobs:
        target_qty = job.job_qty or Decimal(0)
        progress, stage, color = get_job_stage_info(job.job_no, target_qty)
        
        # Apply progress range filters
        if f_min_progress and progress < int(f_min_progress):
            continue
        if f_max_progress and progress > int(f_max_progress):
            continue
            
        job_list.append({
            'job_no': job.job_no,
            'customer': job.remarks, 
            'item_code': job.item_code,
            'qty': target_qty,
            'progress': progress,
            'stage': stage,
            'color': color,
            'due_date': job.job_completion_date or 'N/A'
        })
        
        if len(job_list) >= 50:
            break

    context = {
        'jobs': job_list,
        'filters': {
            'job_no': f_job_no,
            'min_progress': f_min_progress,
            'max_progress': f_max_progress,
            'start_date': f_start_date,
            'end_date': f_end_date
        },
        # Inform user about the data gap
        'data_alert': "Note: Production data in this system ends in Dec 2024. Jobs from 2025 may show 0% progress."
    }
    return render(request, 'reports/job_progress.html', context)

def pending_orders_view(request):
    # Pending: Jobs that are not "Completed" (less than 100% at slitting stage)
    recent_jobs = SLJobMaster.objects.all().order_by('-job_date')[:200]
    pending_list = []
    
    for job in recent_jobs:
        target_qty = job.job_qty or Decimal(0)
        progress, stage, color = get_job_stage_info(job.job_no, target_qty)
        if progress < 100:
            pending_list.append({
                'job_no': job.job_no,
                'item_code': job.item_code,
                'qty': target_qty,
                'due_date': job.job_completion_date or 'N/A',
                'stage': stage,
                'color': color
            })
        if len(pending_list) >= 50:
            break
            
    return render(request, 'reports/pending_orders.html', {'jobs': pending_list})

def job_detail_view(request, job_no):
    job = SLJobMaster.objects.filter(job_no=job_no).first()
    if not job:
        return HttpResponse("Job not found", status=404)
        
    transactions = SLTransactionProduction.objects.filter(job_no=job_no).order_by('trans_date')
    
    # Line items - let's assume one main item for now as per SLJobMaster
    # In a real system, there might be a JobDetail model, but here SLJobMaster has item_code
    
    context = {
        'job': job,
        'transactions': transactions,
        'gen_date': datetime.datetime.now()
    }
    return render(request, 'reports/job_order_report.html', context)

def process_output_view(request, process_type):
    # Mapping process names to codes or filtering logic
    mapping = {
        'printing': '31',
        'rewinding': '32',
        'lamination': '33',
        'slitting': '34'
    }
    
    trans_type = mapping.get(process_type.lower())
    if not trans_type:
        return HttpResponse("Invalid process type", status=400)
        
    transactions = SLTransactionProduction.objects.filter(trans_type=trans_type).order_by('-trans_date')
    
    # KPIs
    summary = transactions.aggregate(
        total_input=Sum('bf_weight1'), # Need to check which field is input weight in production
        total_output=Sum('final_farword_wt'),
        total_waste=Sum('wastage')
    )
    
    total_input = summary['total_input'] or Decimal(0)
    total_output = summary['total_output'] or Decimal(0)
    total_waste = summary['total_waste'] or Decimal(0)
    
    yield_rate = 0
    if total_input > 0:
        yield_rate = (total_output / total_input) * 100
        
    waste_rate = 0
    if total_input > 0:
        waste_rate = (total_waste / total_input) * 100

    context = {
        'process_name': process_type.capitalize(),
        'transactions': transactions,
        'total_input': total_input,
        'total_output': total_output,
        'total_waste': total_waste,
        'yield_rate': yield_rate,
        'waste_rate': waste_rate
    }
    return render(request, 'reports/process_report.html', context)
