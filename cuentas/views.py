# cuentas/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

def portal_acceso(request):
    return render(request, "cuentas/portal.html")

def registro(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("inicio")
    else:
        form = UserCreationForm()
    
    return render(request, "cuentas/registro.html", {"form": form})

def continuar_como_invitado(request):
    request.session["invitado"] = True
    return redirect("inicio")