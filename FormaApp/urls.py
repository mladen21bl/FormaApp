from django.urls import path
from . import views
from .views import index, test


urlpatterns = [
    path('', views.index, name='index'),
    path("test/", views.test, name="test"),
    path('success/', views.success, name='success'),
  ]
