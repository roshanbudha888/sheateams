"""
URL configuration for mrs_shea project.

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
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.logo, name='logo'),
    path('', RedirectView.as_view(url='shea_home/', permanent=True), name='root_redirect'),
    # path('', RedirectView.as_view(url='/shea_home/', permanent=True)),
    # path('', RedirectView.as_view(url='shea_home/', permanent=True)),
    path('shea-home/', include('home.urls', namespace='home')),
    path('games/', include('games.urls', namespace='games')),
    path('chat/', include('chat.urls', namespace='chat')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
     path('accounts/', include('django.contrib.auth.urls')),
    path('payment/', include('payment.urls', namespace='payment')),
    path('support/', include('support.urls', namespace='support')),
    path('rules/', include('rules.urls', namespace='rules')),
    path('admin_panel/', include('admin_panel.urls', namespace='admin_panel')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)