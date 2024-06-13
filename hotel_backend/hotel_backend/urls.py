"""
URL configuration for hotel_backend project.

The `urlpatterns` list routes URLs to the_API_views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function the_API_views
    1. Add an import:  from my_app import the_API_views
    2. Add a URL to urlpatterns:  path('', the_API_views.home, name='home')
Class-based the_API_views
    1. Add an import:  from other_app.the_API_views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

from hotel_backend import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('rooms/', include('hotel_reservation.urls')),
    path('feedback/', include('feedback.urls')),
    path('contact/', include("contact_us.urls"))
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)