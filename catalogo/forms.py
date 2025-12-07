from django import forms
from .models import Pedido


class PedidoCheckoutForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = [
            "nombre_completo",
            "email",
            "telefono",
            "direccion",
            "ciudad",
            "estado",
            "codigo_postal",
            "metodo_pago",
            "notas",
        ]
        widgets = {
            "nombre_completo": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nombre completo",
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "correo@ejemplo.com",
            }),
            "telefono": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ej: 5512345678",
            }),
            "direccion": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 2,
                "placeholder": "Calle, número, colonia...",
            }),
            "ciudad": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ciudad",
            }),
            "estado": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Estado",
            }),
            "codigo_postal": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "CP",
            }),
            "metodo_pago": forms.Select(attrs={
                "class": "form-select",
            }),
            "notas": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Notas adicionales sobre tu pedido (opcional)",
            }),
        }