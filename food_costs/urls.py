from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('prices/', include('prices.urls', namespace='prices')),
    path('', lambda request: redirect('prices:home')),  # Redirect root to prices home
]

