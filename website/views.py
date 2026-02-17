from django.shortcuts import render

def home(request):
    return render(request, 'website/home.html')

def about(request):
    return render(request, 'website/about.html')

def product(request):
    return render(request, 'website/product.html')

def registration(request):
    return render(request, 'website/warranty_registration.html')

def status(request):
    return render(request, 'website/warranty_status.html')

def contact(request):
    return render(request, 'website/contact.html')

def terms_and_conditions(request):
    return render(request, 'website/terms_and_conditions.html')

def perivacy_policy(request):
    return render(request, 'website/privacy_policy.html')

