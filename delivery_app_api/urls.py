"""
URL configuration for delivery_app_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path,include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('DeliveryApp/', include('DeliveryApp.urls')),
    path('',include('djoser.urls')),
    path('',include('djoser.urls.authtoken')),
    #auth/user --> for seeing users
    #auth/token/login --> for generating token etc....
    path('api/token/',TokenObtainPairView.as_view(),name='token_obtain_pair'),
    # This will generate two tokens refresh and access
    # access token will have a lifetime after that it will expire and can be regenerated with refresh token
    path('api/token/refresh',TokenRefreshView.as_view(),name='token_refresh')
]
