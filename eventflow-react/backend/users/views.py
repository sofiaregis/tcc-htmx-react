from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import ensure_csrf_cookie
import json


@ensure_csrf_cookie
def login_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data.get("username")
            password = data.get("password")
        except:
            return JsonResponse({"error": "Dados inválidos"}, status=400)

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return JsonResponse({"message": "Login realizado com sucesso", "username": user.username})
        else:
            return JsonResponse({"error": "Credenciais inválidas"}, status=401)

    elif request.method == "GET":
        return JsonResponse({"detail": "CSRF cookie set"})

    return JsonResponse({"error": "Método não permitido"}, status=405)


def logout_view(request):
    if request.method == "POST":
        logout(request)
        return JsonResponse({"message": "Logout realizado com sucesso"})
    return JsonResponse({"error": "Método não permitido"}, status=405)


@ensure_csrf_cookie
def register_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data.get("username")
            email = data.get("email")
            password = data.get("password")
        except:
            return JsonResponse({"error": "Dados inválidos"}, status=400)

        if not username or not password:
            return JsonResponse({"error": "Usuário e senha são obrigatórios"}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({"error": "Usuário já existe"}, status=400)

        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        return JsonResponse({"message": "Usuário registrado com sucesso", "username": user.username})

    elif request.method == "GET":
        return JsonResponse({"detail": "CSRF cookie set"})

    return JsonResponse({"error": "Método não permitido"}, status=405)


@ensure_csrf_cookie
def user_view(request):
    """Retorna informações do usuário logado (para o React saber se há sessão ativa)."""
    user = request.user
    if user.is_authenticated:
        return JsonResponse({
            "username": user.username,
            "email": user.email,
        })
    return JsonResponse({"error": "Not authenticated"}, status=403)