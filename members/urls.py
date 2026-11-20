from django.urls import path
from . import views

urlpatterns = [
    path('ping/', views.ping, name='ping'),
    path('', views.inicio, name='inicio'),
    path('productos/', views.productos, name='productos'),
    path('servicios/', views.servicios, name='servicios'),
    path('nosotros/', views.nosotros, name='nosotros'),
    path('contacto/', views.contacto, name='contacto'),
    path('pagar/', views.pagar, name='pagar'),

    # Carrito (AJAX)
    path('carrito/agregar/', views.agregar_carrito, name='agregar_carrito'),
    path('carrito/actualizar/', views.actualizar_carrito, name='actualizar_carrito'),
    path('carrito/eliminar/', views.eliminar_carrito, name='eliminar_carrito'),
    path('carrito/json/', views.carrito_json, name='carrito_json'),
]
