from django.contrib import admin
from django.urls import path, include

from website import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about', views.about, name='about'),
    path('product', views.product, name='product'),
    path('registration', views.registration, name='registration'),
    path('status', views.status, name='status'),
    path('contact', views.contact, name='contact'),
    path('terms-and-conditions', views.terms_and_conditions, name='terms_and_conditions'),
    path('perivacy-policy', views.perivacy_policy, name='perivacy_policy')
]
