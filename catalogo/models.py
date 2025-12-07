from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class Producto(models.Model):
    CATEGORIAS_CHOICES = [
        ("Camisas", "Camisas"),
        ("Pantalones", "Pantalones"),
        ("Accesorios", "Accesorios"),
        ("Suéteres", "Suéteres"),
        ("Otros", "Otros"),
    ]

    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)

    categoria = models.CharField(
        max_length=50,
        choices=CATEGORIAS_CHOICES,
        default="Otros",
    )

    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)

    imagen = models.ImageField(
        upload_to="productos/",
        blank=True,
        null=True,
    )

    tallas = models.CharField(
        max_length=150,
        blank=True,
        help_text="Escribe tallas separadas por coma. Ejemplo: S,M,L,XL o 30,32,34"
    )

    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class Pedido(models.Model):
    METODO_PAGO_CHOICES = [
        ("tarjeta", "Tarjeta (simulado)"),
        ("transferencia", "Transferencia bancaria"),
        ("contra_entrega", "Pago contra entrega"),
    ]

    ESTADO_CHOICES = [
        ("pendiente", "Pendiente de pago"),
        ("procesando", "Preparando pedido"),
        ("enviado", "Enviado"),
        ("entregado", "Entregado"),
        ("cancelado", "Cancelado"),
    ]

    # ============================
    # CÓDIGO ÚNICO DEL PEDIDO
    # ============================
    codigo = models.CharField(
        max_length=25,
        unique=True,
        editable=False,
        null=True,   # ✅ permite NULL en pedidos viejos
        blank=True   # ✅ no exige formulario
    )

    usuario = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="pedidos",
    )

    # Datos personales
    nombre_completo = models.CharField(max_length=150)
    email = models.EmailField()
    telefono = models.CharField(max_length=20)

    # Envío
    direccion = models.CharField(max_length=255)
    ciudad = models.CharField(max_length=100)
    estado = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=15)

    # Pago
    metodo_pago = models.CharField(
        max_length=20,
        choices=METODO_PAGO_CHOICES,
        default="tarjeta",
    )

    notas = models.TextField(blank=True)

    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Estado del pedido
    estado_pedido = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default="pendiente",
    )

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pedido {self.codigo or self.id}"

    def save(self, *args, **kwargs):
        # Solo generar código si el pedido es nuevo
        if not self.codigo:
            fecha = timezone.now().strftime("%Y%m%d")
            sufijo = uuid.uuid4().hex[:4].upper()
            self.codigo = f"PW-{fecha}-{sufijo}"

        super().save(*args, **kwargs)


class PedidoItem(models.Model):
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name="items",
    )
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)

    talla = models.CharField(max_length=10, blank=True)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad}"