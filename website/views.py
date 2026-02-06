from django.shortcuts import render

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def product(request):
    return render(request, 'product.html')

def registration(request):
    return render(request, 'warranty_registration.html')

def status(request):
    return render(request, 'warranty_status.html')

def contact(request):
    return render(request, 'contact.html')

def terms_and_conditions(request):
    return render(request, 'terms_and_conditions.html')

def perivacy_policy(request):
    return render(request, 'privacy_policy.html')

