from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from django.http import JsonResponse
import json


def user_register(request):
    if request.method != "POST":
        form = UserCreationForm()
    else:
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")

    return render(request, "account/register.html", {"form": form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect("ddr-home")
    
    if request.method != "POST":
        return render(request, "account/login.html")

    username = request.POST.get("username")
    password = request.POST.get("password")
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect("ddr-home")
    else:
        return render(
            request, "account/login.html", {"error": "Invalid username or password", "username":username}
        )


@login_required
def user_logout(request):
    logout(request)
    return redirect("login")


@login_required
def change_color_theme(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=405)

    try:
        theme = json.loads(request.body).get("color_theme")
    except:
        return JsonResponse({"error": "Invalid payload"}, status=400)

    if not theme:
        return JsonResponse({"error": "payload missing"}, status=400)

    available_themes = dict(UserProfile.AVAILABLE_THEME).keys()
    if theme not in available_themes:
        return JsonResponse({"error": f"Invalid theme values"}, status=400)

    user_profile = get_object_or_404(UserProfile, user=request.user)

    user_profile.color_theme = theme
    user_profile.save()

    return JsonResponse(
        {"message": "Theme updated successfully.", "theme": user_profile.color_theme},
        status=200,
    )


@login_required
def profile(request):
    return render(
        request,
        "account/profile.html",
        {"theme": UserProfile.objects.get(user=request.user).color_theme},
    )
