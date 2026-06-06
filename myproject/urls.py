# Save this file inside: myproject/myproject/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('erp.urls')),  # Includes the erp paths seamlessly at the root level
]