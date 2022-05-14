from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('search/', views.search_bar, name='search'),
    path('currencyconversion/', views.conversion, name="currencyconversion"),
    path('graphicpage/',views.graph,name="rate_of_increase")
]
