# catalogo/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Inicio
    path("", views.inicio, name="inicio"),

    # Productos
    path("productos/", views.lista_productos, name="lista_productos"),
    path(
        "productos/<int:producto_id>/",
        views.detalle_producto,
        name="detalle_producto",
    ),

    # Carrito
    path("carrito/", views.ver_carrito, name="ver_carrito"),
    path(
        "carrito/agregar/<int:producto_id>/",
        views.agregar_al_carrito,
        name="agregar_al_carrito",
    ),
    path(
        "carrito/eliminar/<str:item_id>/",
        views.eliminar_del_carrito,
        name="eliminar_del_carrito",
    ),
    path("carrito/vaciar/", views.vaciar_carrito, name="vaciar_carrito"),

    # Checkout / pedidos
    path("checkout/", views.checkout_pedido, name="checkout_pedido"),
    path("mis-pedidos/", views.mis_pedidos, name="mis_pedidos"),
    path(
        "pedido/<int:pedido_id>/",
        views.detalle_pedido,
        name="detalle_pedido",
    ),

    # ✅ Confirmación por CÓDIGO (esta es la que faltaba)
    path(
        "pedido/confirmacion/<str:codigo>/",
        views.pedido_confirmacion,
        name="pedido_confirmacion",
    ),

    # Tracking por CÓDIGO
    path(
        "trackear-pedido/",
        views.trackear_pedido,
        name="trackear_pedido",
    ),
]