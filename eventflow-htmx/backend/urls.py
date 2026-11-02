"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from events import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("users/", include("users.urls")),
    
    # Event HTML Views
    path('', views.home_view, name='home'),
    path('search/', views.search_view, name='search'),
    path('events/highlighted/', views.highlighted_events_view, name='highlighted-events'),
    path('events/today/', views.today_events_view, name='today-events'),
    path('event/<int:pk>/', views.event_details_view, name='event-details'),
    path('event/<int:pk>/register/', views.event_register_view, name='event-register'),
    path('event/<int:pk>/delete/', views.event_delete_view, name='event-delete'),
    path('event/<int:pk>/edit/', views.event_edit_view, name='event-edit'),
    path('event/<int:pk>/registrations/', views.event_registrations_view, name='event-registrations'),
    path('events/create/', views.event_create_view, name='event-create'),
    path('registrations/me/', views.my_registrations_view, name='my-registrations'),
    path('events/me/', views.my_events_view, name='my-events'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
