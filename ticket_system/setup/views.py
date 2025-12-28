from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Area, Customer, ItemCategory, Item, Machine, Operator
from .forms import AreaForm, CustomerForm, ItemCategoryForm, ItemForm, MachineForm, OperatorForm

# TODO: Write a function to display area form in the front end and make an html file with the same styling as the area form in the frontend directory and than the forms directory. Also make it save in the db.