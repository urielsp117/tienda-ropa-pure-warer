from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from catalogo import views as catalogo_views
from cuentas import views as cuentas_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("admin/", admin.site.urls),

    # ===========================
    # PORTAL
    # ===========================
    path("", cuentas_views.portal_acceso, name="portal_acceso"),

    # ===========================
    # CATÁLOGO
    # ===========================
    path("inicio/", catalogo_views.inicio, name="inicio"),
    path("productos/", catalogo_views.lista_productos, name="lista_productos"),

    path(
        "productos/<int:producto_id>/",
        catalogo_views.detalle_producto,
        name="detalle_producto",
    ),

    # ===========================
    # CARRITO
    # ===========================
    path("carrito/", catalogo_views.ver_carrito, name="ver_carrito"),

    path(
        "carrito/agregar/<int:producto_id>/",
        catalogo_views.agregar_al_carrito,
        name="agregar_al_carrito",
    ),

    path(
        "carrito/eliminar/<str:item_id>/",
        catalogo_views.eliminar_del_carrito,
        name="eliminar_del_carrito",
    ),

    path(
        "carrito/vaciar/",
        catalogo_views.vaciar_carrito,
        name="vaciar_carrito",
    ),

    # ===========================
    # CHECKOUT / PEDIDOS
    # ===========================
    path(
        "checkout/",
        catalogo_views.checkout_pedido,
        name="checkout_pedido",
    ),

    path(
        "pedido/<int:pedido_id>/",
        catalogo_views.detalle_pedido,
        name="detalle_pedido",
    ),

    path(
        "mis-pedidos/",
        catalogo_views.mis_pedidos,
        name="mis_pedidos",
    ),

    path(
        "pedido/confirmacion/<str:codigo>/",
        catalogo_views.pedido_confirmacion,
        name="pedido_confirmacion",
    ),

    # 🔹 NUEVA RUTA: RASTREAR PEDIDO POR CÓDIGO
    path(
        "trackear-pedido/",
        catalogo_views.trackear_pedido,
        name="trackear_pedido",
    ),

    # ===========================
    # AUTH
    # ===========================
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="cuentas/login.html"),
        name="login",
    ),

    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="portal_acceso"),
        name="logout",
    ),

    path("registro/", cuentas_views.registro, name="registro"),

    # ===========================
    # INVITADO
    # ===========================
    path(
        "invitado/",
        cuentas_views.continuar_como_invitado,
        name="continuar_como_invitado",
    ),
]

# ===========================
# SERVIR MEDIA EN DESARROLLO
# ===========================
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)