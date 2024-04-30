from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required


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
    if request.method != "POST":
        return render(request, "account/login.html")

    email = request.POST.get("email")
    password = request.POST.get("password")
    user = authenticate(request, username=email, password=password)
    if user is not None:
        login(request, user)
        return redirect("home-home")
    else:
        return render(
            request, "account/login.html", {"error": "Invalid email or password"}
        )


@login_required
def user_logout(request):
    logout(request)
    return redirect("login")
