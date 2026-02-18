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



from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache

@never_cache
def dashboard_login_page(request):
    """
    Renders the dashboard login page.
    If already authenticated via Django session, redirect (optional).
    For JWT localStorage auth, redirect is handled by JS too.
    """
    return render(request, "dashboard/login.html")


@never_cache
def dashboard_page(request):
    """
    Renders dashboard shell page (frontend).
    Protection is done client-side using JWT in localStorage,
    and server-side on API endpoints using DRF IsAuthenticated.
    """
    return render(request, "dashboard/index.html")


