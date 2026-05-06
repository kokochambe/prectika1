from django.urls import path, include
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('sales/', include('sales.urls')),
    path('reports/', include('reports.urls')),
    path('workorders/', include('workorders.urls')),
]
