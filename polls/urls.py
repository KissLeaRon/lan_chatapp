from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<str:year>_<str:month>_<str:day>',views.log, name='log')
]
