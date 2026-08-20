from django.urls import path
from .views import dashboard_view, profile_view, enroll_course_view, drop_course_view, pay_fee_view

urlpatterns = [
    path('dashboard/', dashboard_view, name='dashboard'),
    path('profile/', profile_view, name='profile'),
    path('enroll/<int:course_id>/', enroll_course_view, name='enroll_course'),
    path('drop/<int:enrollment_id>/', drop_course_view, name='drop_course'),
    path('pay-fee/<int:fee_id>/', pay_fee_view, name='pay_fee'),
]