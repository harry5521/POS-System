from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from products.models import Product
from django.db.models import F

# Create your views here.

class LoginView(View):
    def get(self, request):
        return render(request, 'users/login.html')
    
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')

        # print(username, password)
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('users:dashboard_view')
        else:
            messages.error(request, 'Invalid username or password.')
            return redirect('users:login_view')
        

class LogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        return redirect('users:login_view')
        

class DashboardView(LoginRequiredMixin, View):
    def get(self, request):
        products = Product.objects.filter(quantity__lte=F('low_stock'))
        context = {"products": products}
        return render(request, 'users/dashboard.html', context)