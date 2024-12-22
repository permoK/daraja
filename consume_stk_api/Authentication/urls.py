from django.urls import path
from django.contrib.auth import views as auth_views
# from .views import CustomPasswordResetView

from . import views
from .views import SignUpView
# from .views import CustomLoginView  # Import your custom view

app_name = 'Authentication'

urlpatterns = [
        path('', views.index, name='index'),

        path('signup/', SignUpView.as_view(), name='signup_tutor'),

        # Built-in Django auth views
        path('login/', views.custom_login, name='login_user'),
        path('logout/',views.logout_user, name='logout_user'),
        # path('logout/', auth_views.LogoutView.as_view(), name='logout'),

        # Password reset views
        path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset'),
        path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='auth_app/password_reset_done.html'), name='password_reset_done'),
        path('password_reset_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='auth_app/password_reset_confirm.html'), name='password_reset_confirm'),
        path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='auth_app/password_reset_complete.html'), name='password_reset_complete'),

        ]
