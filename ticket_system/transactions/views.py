from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from django.core.exceptions import ValidationError
from django.db import IntegrityError, DatabaseError
from .models import (
    SalesOrder, JobOrder, PrintingTransaction, RewindingTransaction, 
    SlittingTransaction, LaminationTransaction, CoreTransaction
)
from .forms import (
    SalesOrderForm, JobOrderForm, PrintingTransactionForm, RewindingTransactionForm, 
    SlittingTransactionForm, LaminationTransactionForm, CoreTransactionForm
)

def handle_transaction_create(request, form_class, template_name, success_url='/'):
    """
    Generic handler for creating transaction records with proper error handling.
    Catches ValidationError and database exceptions to provide user-friendly messages.
    """
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Transaction recorded successfully.")
                return redirect(success_url)
            except ValidationError as e:
                # Catch model.clean() validation errors
                if hasattr(e, 'message_dict'):
                    for field, errors in e.message_dict.items():
                        for error in errors:
                            messages.error(request, f"{field}: {error}")
                else:
                    messages.error(request, str(e))
            except IntegrityError as e:
                # Catch database constraint violations (unique, foreign key, etc.)
                messages.error(request, "Database constraint violation. Please check your data and try again.")
            except DatabaseError as e:
                # Catch other database errors
                messages.error(request, f"Database error: {str(e)}")
            except Exception as e:
                # Catch any other unexpected errors
                messages.error(request, f"Unexpected error: {str(e)}")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = form_class()
    return render(request, template_name, {'form': form})

# --- Sales Order Views ---
def sales_order_list(request):
    orders = SalesOrder.objects.all().order_by('-created_at')
    return render(request, 'transactions/sales_order_list.html', {'orders': orders})

def sales_order_create(request):
    if request.method == 'POST':
        form = SalesOrderForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Sales Order created.")
            return redirect('sales_order_create') # Redirect to list or self
    else:
        form = SalesOrderForm()
    return render(request, 'transactions/sales_order_form.html', {'form': form})

def sales_order_update(request, pk):
    so = get_object_or_404(SalesOrder, pk=pk)
    
    # Strict Lock: Cannot edit if Approved or further
    if so.status in [SalesOrder.Status.APPROVED, SalesOrder.Status.IN_PRODUCTION, SalesOrder.Status.CLOSED]:
        messages.warning(request, f"Sales Order {so.order_number} is locked ({so.status}). Cannot edit.")
        return redirect('sales_order_create') # Should redirect to detail/list view

    if request.method == 'POST':
        form = SalesOrderForm(request.POST, instance=so)
        if form.is_valid():
            form.save()
            messages.success(request, "Sales Order updated.")
            return redirect('sales_order_create')
    else:
        form = SalesOrderForm(instance=so)
    return render(request, 'transactions/sales_order_form.html', {'form': form})


# --- Job Order Views ---
def job_order_list(request):
    orders = JobOrder.objects.all().order_by('-created_at')
    return render(request, 'transactions/job_order_list.html', {'orders': orders})

def job_order_create(request):
    # Requirement: "Prevent multiple JobOrders from same SalesOrder unless explicitly allowed"
    # Logic handled in Model/Form clean, View just renders
    return handle_transaction_create(request, JobOrderForm, 'transactions/job_order_form.html', success_url='job_order_create')

# --- Production Transaction Views ---
# These are typically immutable logs, so usually only Create views exist, or Update is restricted.

def printing_transaction_list(request):
    transactions = PrintingTransaction.objects.all().order_by('-created_at')
    return render(request, 'transactions/printing_transaction_list.html', {'transactions': transactions})

def printing_transaction_create(request):
    return handle_transaction_create(
        request, PrintingTransactionForm, 'transactions/printing_transaction_form.html', success_url='printing_transaction_create'
    )

def rewinding_transaction_list(request):
    transactions = RewindingTransaction.objects.all().order_by('-created_at')
    return render(request, 'transactions/rewinding_transaction_list.html', {'transactions': transactions})

def rewinding_transaction_create(request):
    return handle_transaction_create(
        request, RewindingTransactionForm, 'transactions/rewinding_transaction_form.html', success_url='rewinding_transaction_create'
    )

def slitting_transaction_list(request):
    transactions = SlittingTransaction.objects.all().order_by('-created_at')
    return render(request, 'transactions/slitting_transaction_list.html', {'transactions': transactions})

def slitting_transaction_create(request):
    return handle_transaction_create(
        request, SlittingTransactionForm, 'transactions/slitting_transaction_form.html', success_url='slitting_transaction_create'
    )

def lamination_transaction_list(request):
    transactions = LaminationTransaction.objects.all().order_by('-created_at')
    return render(request, 'transactions/lamination_transaction_list.html', {'transactions': transactions})

def lamination_transaction_create(request):
    return handle_transaction_create(
        request, LaminationTransactionForm, 'transactions/lamination_transaction_form.html', success_url='lamination_transaction_create'
    )

def core_transaction_list(request):
    transactions = CoreTransaction.objects.all().order_by('-created_at')
    return render(request, 'transactions/core_transaction_list.html', {'transactions': transactions})

def core_transaction_create(request):
    return handle_transaction_create(
        request, CoreTransactionForm, 'transactions/core_transaction_form.html', success_url='core_transaction_create'
    )


# --- Lookup API Views (JSON) ---
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from setup.models import Customer, Machine, Operator

@login_required
def job_order_lookup(request):
    """
    JSON API endpoint for Job Order autocomplete lookup.
    Searches by Job Order ID or Sales Order number.
    Returns up to 15 results for performance.
    """
    query = request.GET.get('q', '').strip()
    
    if not query:
        return JsonResponse({'results': []})
    
    # Search by ID or Sales Order number
    job_orders = JobOrder.objects.select_related('sales_order').filter(
        Q(id__icontains=query) | 
        Q(sales_order__order_number__icontains=query)
    )[:15]
    
    results = [
        {
            'id': jo.id,
            'text': f"JO-{jo.id} ({jo.sales_order.order_number if jo.sales_order else 'No SO'})",
            'sales_order': jo.sales_order.order_number if jo.sales_order else None,
            'status': jo.status
        }
        for jo in job_orders
    ]
    
    return JsonResponse({'results': results})


@login_required
def customer_lookup(request):
    """
    JSON API endpoint for Customer autocomplete lookup.
    Searches by name or code.
    Returns up to 15 results for performance.
    """
    query = request.GET.get('q', '').strip()
    
    if not query:
        return JsonResponse({'results': []})
    
    # Search by name or code (assuming Customer has these fields)
    customers = Customer.objects.filter(
        Q(name__icontains=query) | 
        Q(code__icontains=query)
    )[:15]
    
    results = [
        {
            'id': customer.id,
            'text': f"{customer.name} ({customer.code})",
            'name': customer.name,
            'code': customer.code
        }
        for customer in customers
    ]
    
    return JsonResponse({'results': results})


@login_required
def machine_lookup(request):
    """
    JSON API endpoint for Machine autocomplete lookup.
    Searches active machines by name or code.
    Returns up to 15 results for performance.
    """
    query = request.GET.get('q', '').strip()
    
    if not query:
        return JsonResponse({'results': []})
    
    # Only search active machines
    machines = Machine.objects.filter(
        status='active'
    ).filter(
        Q(name__icontains=query) | 
        Q(code__icontains=query)
    )[:15]
    
    results = [
        {
            'id': machine.id,
            'text': f"{machine.name} ({machine.code})",
            'name': machine.name,
            'code': machine.code,
            'status': machine.status
        }
        for machine in machines
    ]
    
    return JsonResponse({'results': results})


@login_required
def operator_lookup(request):
    """
    JSON API endpoint for Operator autocomplete lookup.
    Searches active operators by name.
    Returns up to 15 results for performance.
    """
    query = request.GET.get('q', '').strip()
    
    if not query:
        return JsonResponse({'results': []})
    
    # Only search active operators
    operators = Operator.objects.filter(
        is_active=True,
        name__icontains=query
    )[:15]
    
    results = [
        {
            'id': operator.id,
            'text': operator.name,
            'name': operator.name,
            'is_active': operator.is_active
        }
        for operator in operators
    ]
    
    return JsonResponse({'results': results})