from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Area, Customer, ItemCategory, Item, Machine, Operator
from .forms import AreaForm, CustomerForm, ItemCategoryForm, ItemForm, MachineForm, OperatorForm

# Helper to handle form view logic
def handle_form_view(request, form_class, template_name, instance=None, success_url='/'):
    if request.method == 'POST':
        form = form_class(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, f"{form_class._meta.model._meta.verbose_name} saved successfully.")
            return redirect(success_url)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = form_class(instance=instance)
    
    return render(request, template_name, {'form': form})

# --- Area Views ---
def area_list(request):
    areas = Area.objects.all()
    # Assuming we might want to list them, but for now focusing on form access
    return render(request, 'setup/area_list.html', {'areas': areas})

def area_create(request):
    return handle_form_view(request, AreaForm, 'setup/area_form.html', success_url='area_list')

def area_update(request, pk):
    area = get_object_or_404(Area, pk=pk)
    return handle_form_view(request, AreaForm, 'setup/area_form.html', instance=area, success_url='area_list')


# --- Customer Views ---
def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'setup/customer_list.html', {'customers': customers})

def customer_create(request):
    return handle_form_view(request, CustomerForm, 'setup/customer_form.html', success_url='customer_list')

def customer_update(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    return handle_form_view(request, CustomerForm, 'setup/customer_form.html', instance=customer, success_url='customer_list')


# --- ItemCategory Views ---
def item_category_list(request):
    categories = ItemCategory.objects.all()
    return render(request, 'setup/item_category_list.html', {'categories': categories})

def item_category_create(request):
    return handle_form_view(request, ItemCategoryForm, 'setup/item_category_form.html', success_url='item_category_list')

def item_category_update(request, pk):
    category = get_object_or_404(ItemCategory, pk=pk)
    return handle_form_view(request, ItemCategoryForm, 'setup/item_category_form.html', instance=category, success_url='item_category_list')


# --- Item Views ---
def item_list(request):
    items = Item.objects.all()
    return render(request, 'setup/item_list.html', {'items': items})

def item_create(request):
    return handle_form_view(request, ItemForm, 'setup/item_form.html', success_url='item_list')

def item_update(request, pk):
    item = get_object_or_404(Item, pk=pk)
    return handle_form_view(request, ItemForm, 'setup/item_form.html', instance=item, success_url='item_list')


# --- Machine Views ---
def machine_list(request):
    machines = Machine.objects.all()
    return render(request, 'setup/machine_list.html', {'machines': machines})

def machine_create(request):
    return handle_form_view(request, MachineForm, 'setup/machine_form.html', success_url='machine_list')

def machine_update(request, pk):
    machine = get_object_or_404(Machine, pk=pk)
    return handle_form_view(request, MachineForm, 'setup/machine_form.html', instance=machine, success_url='machine_list')


# --- Operator Views ---
def operator_list(request):
    operators = Operator.objects.all()
    return render(request, 'setup/operator_list.html', {'operators': operators})

def operator_create(request):
    return handle_form_view(request, OperatorForm, 'setup/operator_form.html', success_url='operator_list')

def operator_update(request, pk):
    operator = get_object_or_404(Operator, pk=pk)
    return handle_form_view(request, OperatorForm, 'setup/operator_form.html', instance=operator, success_url='operator_list')
