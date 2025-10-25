from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.LoginView.as_view(), name="login_view"),
    path('dashboard/', views.DashboardView.as_view(), name="dashboard_view"),
    path('logout/', views.LogoutView.as_view(), name="logout_view"),
]
