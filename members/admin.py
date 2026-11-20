from django.contrib import admin
from .models import Producto, Pedido, MensajeContacto

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'categoria', 'stock', 'fecha_creacion')
    list_filter = ('categoria',)
    search_fields = ('nombre', 'descripcion')

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'telefono', 'email', 'total', 'metodo_pago', 'entrega', 'fecha')
    list_filter = ('metodo_pago', 'entrega', 'fecha')
    search_fields = ('nombre', 'telefono', 'email')

@admin.register(MensajeContacto)
class MensajeContactoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'telefono', 'asunto', 'fecha', 'respondido')
    list_filter = ('respondido', 'fecha')
    search_fields = ('nombre', 'email', 'asunto', 'mensaje')
