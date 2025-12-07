# cuentas/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

def portal_acceso(request):
    # Primera pantalla: elegir login / registro / invitado
    return render(request, "cuentas/portal.html")

def registro(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()        # guarda el usuario en la BD
            login(request, user)      # inicia sesión automáticamente
            return redirect("inicio") # lo mandamos a la página principal
    else:
        form = UserCreationForm()
    
    return render(request, "cuentas/registro.html", {"form": form})

def continuar_como_invitado(request):
    # Marcamos en la sesión que es invitado
    request.session["invitado"] = True
    return redirect("inicio")