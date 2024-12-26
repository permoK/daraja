from django.urls import path
from . import views

app_name = 'stk'

urlpatterns = [
        path('init_stk/', views.init_stk, name='stk'),
        path('', views.stkpush, name='stkpush'),
        path('lnmo-callback', views.incoming, name='callback'),
        ]
