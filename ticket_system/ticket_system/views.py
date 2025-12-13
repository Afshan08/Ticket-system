from django.shortcuts import render

def dashboard(request):
    """Main dashboard view showing cards for all modules"""
    return render(request, 'dashboard.html')
