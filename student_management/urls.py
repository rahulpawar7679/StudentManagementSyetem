from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static
from students.views import dashboard_view  # <--- Make sure this is imported from students.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('dashboard'), name='root'),
    path('dashboard/', dashboard_view, name='dashboard'),  # <--- Ensure this route is active
    path('accounts/', include('accounts.urls')),
    path('attendance/', include('attendance.urls')),
    path('fees/', include('fees.urls')),
    path('courses/', include('courses.urls')),
    path('', include('students.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)