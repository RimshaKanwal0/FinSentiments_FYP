from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from .models import ContactMessage
from analysis.models import NewsAnalysis 
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
def home(request):
    return render(request, 'frontend/home.html')  # Make sure 'home.html' exists in the templates/frontend folder

def contact(request):
    return render(request, 'frontend/contact.html')  # Ensure 'contact.html' exists in the templates/frontend folder


def submit_contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email') or None
        message = request.POST.get('message')
        ContactMessage.objects.create(
            name=name,
            email=email,
            message=message
        )
        messages.success(request, "✅ Thank you for contacting us! We'll get back to you soon.")
        return redirect('frontend:contact')
    return HttpResponse("Invalid request", status=400)

def about(request):
    return render(request, 'frontend/about.html')


@login_required
def reports(request):
    results = NewsAnalysis.objects.filter(user=request.user).select_related('news').order_by('-news__published_at')
    return render(request, 'frontend/reports.html', {'results': results})



@login_required
def reports(request):
    
    report_list = NewsAnalysis.objects.filter(user=request.user).select_related('news').order_by('-news__published_at')
    
    paginator = Paginator(report_list, 10)  # Show 10 reports per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, 'frontend/reports.html', {'page_obj': page_obj})

def profile(request):
    return render(request, 'frontend/profile.html')