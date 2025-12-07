from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction

from .models import Producto, Pedido, PedidoItem
from .forms import PedidoCheckoutForm


# ========== PÁGINA DE INICIO ==========

def inicio(request):
    return render(request, "catalogo/inicio.html")


# ========== LISTADO DE PRODUCTOS ==========

def lista_productos(request):
    categoria = request.GET.get("categoria")
    productos = Producto.objects.filter(activo=True).order_by("nombre")

    categorias = (
        Producto.objects.exclude(categoria__isnull=True)
                        .exclude(categoria__exact="")
                        .values_list("categoria", flat=True)
                        .distinct()
    )

    if categoria:
        productos = productos.filter(categoria=categoria)

    context = {
        "productos": productos,
        "categorias": categorias,
        "categoria_actual": categoria,
    }
    return render(request, "catalogo/lista_productos.html", context)


# ========== DETALLE DE PRODUCTO ==========

def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id, activo=True)

    # Convertimos "S,M,L,XL" → ["S", "M", "L", "XL"]
    tallas = []
    if producto.tallas:
        tallas = [t.strip() for t in producto.tallas.split(",") if t.strip()]

    context = {
        "producto": producto,
        "tallas": tallas,
    }
    return render(request, "catalogo/detalle_producto.html", context)


# ========== FUNCIONES AUXILIARES CARRITO ==========

def _obtener_items_carrito(request):
    """
    Lee el carrito de la sesión y regresa:
    - items: lista de dicts
    - total: suma de los subtotales
    """
    carrito = request.session.get("carrito", {})
    items = list(carrito.values())
    total = sum(item.get("subtotal", 0) for item in items)
    return items, total


# ========== CARRITO (USANDO SESIÓN) ==========

def agregar_al_carrito(request, producto_id):
    if request.method != "POST":
        return redirect("detalle_producto", producto_id=producto_id)

    producto = get_object_or_404(Producto, id=producto_id, activo=True)

    talla = request.POST.get("talla", "").strip()
    cantidad_str = request.POST.get("cantidad", "1")

    try:
        cantidad = int(cantidad_str)
    except ValueError:
        cantidad = 1

    if cantidad < 1:
        cantidad = 1

    # Obtenemos el carrito desde la sesión
    carrito = request.session.get("carrito", {})

    # ID único por producto + talla
    clave_item = f"{producto.id}_{talla or 'unica'}"

    precio = float(producto.precio)

    if clave_item in carrito:
        carrito[clave_item]["cantidad"] += cantidad
        carrito[clave_item]["subtotal"] = carrito[clave_item]["cantidad"] * precio
    else:
        carrito[clave_item] = {
            "id": clave_item,
            "producto_id": producto.id,
            "nombre": producto.nombre,
            "talla": talla,
            "cantidad": cantidad,
            "precio": precio,
            "subtotal": precio * cantidad,
            "imagen_url": producto.imagen.url if producto.imagen else "",
        }

    request.session["carrito"] = carrito
    request.session.modified = True

    messages.success(request, f"{producto.nombre} se agregó al carrito.")
    return redirect("ver_carrito")


def ver_carrito(request):
    items, total = _obtener_items_carrito(request)

    context = {
        "items": items,
        "total": total,
    }
    return render(request, "catalogo/carrito.html", context)


def eliminar_del_carrito(request, item_id):
    carrito = request.session.get("carrito", {})
    if item_id in carrito:
        del carrito[item_id]
        request.session["carrito"] = carrito
        request.session.modified = True
        messages.info(request, "Producto eliminado del carrito.")

    return redirect("ver_carrito")


def vaciar_carrito(request):
    request.session["carrito"] = {}
    request.session.modified = True
    messages.info(request, "Carrito vaciado.")
    return redirect("ver_carrito")


# ========== CHECKOUT / PEDIDO ==========

def checkout_pedido(request):
    carrito = request.session.get("carrito", {})
    if not carrito:
        messages.warning(request, "Tu carrito está vacío.")
        return redirect("ver_carrito")

    items, total = _obtener_items_carrito(request)

    if request.method == "POST":
        form = PedidoCheckoutForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Creamos el pedido
                    pedido = form.save(commit=False)
                    if request.user.is_authenticated:
                        pedido.usuario = request.user
                    pedido.total = total
                    pedido.save()  # Aquí se genera automáticamente pedido.codigo

                    # Creamos los items del pedido y actualizamos stock
                    for item in items:
                        producto = get_object_or_404(Producto, id=item["producto_id"])

                        # Validar stock
                        if producto.stock < item["cantidad"]:
                            messages.error(
                                request,
                                f"No hay suficiente stock de {producto.nombre}. "
                                f"Disponible: {producto.stock}, solicitaste: {item['cantidad']}."
                            )
                            # Forzamos rollback de la transacción
                            raise transaction.TransactionManagementError(
                                "Stock insuficiente"
                            )

                        # Descontar stock
                        producto.stock -= item["cantidad"]
                        producto.save()

                        # Crear PedidoItem
                        PedidoItem.objects.create(
                            pedido=pedido,
                            producto=producto,
                            talla=item.get("talla", ""),
                            cantidad=item["cantidad"],
                            precio_unitario=item["precio"],
                        )

                    # Vaciar carrito
                    request.session["carrito"] = {}
                    request.session.modified = True

                    # Mensaje con el código de pedido
                    messages.success(
                        request,
                        f"Tu pedido {pedido.codigo} se registró correctamente. "
                        "Guarda este código para consultar el estado de tu envío."
                    )
                    # Ir a pantalla de confirmación
                    return redirect("pedido_confirmacion", codigo=pedido.codigo)

            except transaction.TransactionManagementError:
                # Si algo falla en la transacción, regresamos al checkout
                return redirect("checkout_pedido")
    else:
        initial = {}
        if request.user.is_authenticated:
            initial["nombre_completo"] = (
                request.user.get_full_name() or request.user.username
            )
            initial["email"] = request.user.email
        form = PedidoCheckoutForm(initial=initial)

    context = {
        "form": form,
        "items": items,
        "total": total,
    }
    return render(request, "catalogo/checkout.html", context)


# ========== DETALLE DE PEDIDO (por ID) ==========

def detalle_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)

    # Protección básica
    if pedido.usuario and request.user != pedido.usuario and not request.user.is_staff:
        messages.error(request, "No tienes permiso para ver este pedido.")
        return redirect("inicio")

    items = list(pedido.items.select_related("producto").all())

    primer_item = items[0] if items else None

    hero_imagen_url = ""
    if (
        primer_item
        and getattr(primer_item, "producto", None)
        and getattr(primer_item.producto, "imagen", None)
        and primer_item.producto.imagen
    ):
        hero_imagen_url = primer_item.producto.imagen.url

    total_pedido = sum(float(it.precio_unitario) * it.cantidad for it in items)

    context = {
        "pedido": pedido,
        "items": items,
        "primer_item": primer_item,
        "hero_imagen_url": hero_imagen_url,
        "total_pedido": total_pedido,
    }
    return render(request, "catalogo/detalle_pedido.html", context)


# ========== LISTADO DE PEDIDOS DEL USUARIO ==========

@login_required
def mis_pedidos(request):
    pedidos = Pedido.objects.filter(usuario=request.user).order_by("-creado_en")
    context = {
        "pedidos": pedidos,
    }
    return render(request, "catalogo/mis_pedidos.html", context)


# ========== CONFIRMACIÓN DE PEDIDO (DESPUÉS DEL CHECKOUT) ==========

def pedido_confirmacion(request, codigo):
    """
    Pantalla de “gracias por tu compra” usando el CÓDIGO del pedido.
    """
    pedido = get_object_or_404(Pedido, codigo=codigo)

    if pedido.usuario and request.user != pedido.usuario and not request.user.is_staff:
        messages.error(request, "No tienes permiso para ver este pedido.")
        return redirect("inicio")

    items = list(pedido.items.select_related("producto").all())
    total_pedido = sum(float(it.precio_unitario) * it.cantidad for it in items)

    context = {
        "pedido": pedido,
        "items": items,
        "total_pedido": total_pedido,
    }
    return render(request, "catalogo/pedido_confirmacion.html", context)


# ========== RASTREAR / TRACKEAR PEDIDO POR CÓDIGO ==========

def trackear_pedido(request):
    """
    Permite a cualquier usuario consultar el estado de su pedido
    escribiendo el CÓDIGO (pedido.codigo) que se le generó.
    """
    pedido_encontrado = None
    codigo_busqueda = ""

    if request.method == "POST":
        codigo_busqueda = request.POST.get("codigo", "").strip()
        if codigo_busqueda:
            try:
                pedido_encontrado = Pedido.objects.get(codigo=codigo_busqueda)
            except Pedido.DoesNotExist:
                messages.error(
                    request,
                    "No encontramos ningún pedido con ese código. "
                    "Revisa que esté bien escrito."
                )

    context = {
        "codigo": codigo_busqueda,
        "pedido": pedido_encontrado,
    }
    return render(request, "catalogo/trackear_pedido.html", context)