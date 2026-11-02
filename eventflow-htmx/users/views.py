from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from events.views import render_htmx

def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")
        
    next_url = request.GET.get("next", "home")
    
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        
        if not username or not password:
            return render_htmx(request, "login.html", {"next": next_url, "username": username, "error": "Por favor, preencha todos os campos."})
            
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Bem-vindo de volta, {user.username}!")
            return redirect(next_url if next_url.startswith("/") else "home")
        else:
            return render_htmx(request, "login.html", {"next": next_url, "username": username, "error": "Credenciais inválidas"})
            
    return render_htmx(request, "login.html", {"next": next_url})

def register_view(request):
    if request.user.is_authenticated:
        return redirect("home")
        
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        
        if not username or not password or not email:
            messages.error(request, "Todos os campos são obrigatórios.")
            return render(request, "register.html", {"username": username, "email": email})
            
        if User.objects.filter(username=username).exists():
            messages.error(request, "Este nome de usuário já está em uso.")
            return render(request, "register.html", {"username": username, "email": email})
            
        if User.objects.filter(email=email).exists():
            messages.error(request, "Este e-mail já está em uso.")
            return render(request, "register.html", {"username": username, "email": email})
            
        # Cria o usuário
        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        messages.success(request, "Cadastro realizado com sucesso! Bem-vindo ao EventFlow.")
        return redirect("home")
        
    return render(request, "register.html")

def logout_view(request):
    logout(request)
    messages.success(request, "Sessão encerrada com sucesso.")
    return redirect("home")