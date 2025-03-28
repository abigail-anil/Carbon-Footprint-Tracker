"""CarbonTrack URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('signup/', include('users.urls')),
    path('signin/', auth_views.LoginView.as_view(template_name='users/signin.html'), name='sign_in'),
    path('signout/', auth_views.LogoutView.as_view(template_name='users/signout.html'), name='sign_out'),
    path('admin/', admin.site.urls), 
    path('', include('CarbonTracker.urls')), 
    # Password Reset URLs
    path('password-reset/',
         auth_views.PasswordResetView.as_view( #to Display a form where the user enters their email.
             template_name='users/password_reset_form.html'
         ),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view( #to inform the user that a reset link has been sent.
             template_name='users/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view( #to let the user enter a new password once they click the email link.
             template_name='users/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view( #to inform the user that the password has been successfully reset.
             template_name='users/password_reset_complete.html'
         ),
         name='password_reset_complete'),
]