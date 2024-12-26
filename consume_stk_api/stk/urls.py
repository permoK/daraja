from django.urls import path
from . import views


urlpatterns = [
        path('init_stk/', views.init_stk, name='stk'),
        path('', views.stkpush, name='stkpush'),
        path('lnmo-callback', views.incoming, name='callback'),
        ]
