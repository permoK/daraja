from django.urls import path
from . import views


urlpatterns = [
        path('', views.init_stk, name='stk'),
        path('lnmo-callback', views.incoming, name='callback'),
        ]
