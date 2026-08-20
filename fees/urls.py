from django.urls import path
from .views import fee_receipt_view, generate_bulk_invoices_view

urlpatterns = [
    path('receipt/<int:fee_id>/', fee_receipt_view, name='fee_receipt'),
    path('generate-invoices/', generate_bulk_invoices_view, name='generate_invoices'),
]