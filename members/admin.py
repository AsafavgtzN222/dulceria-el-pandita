from django.contrib import admin
from .models import Producto, Pedido, MensajeContacto

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'categoria', 'stock', 'fecha_creacion')
    list_filter = ('categoria',)
    search_fields = ('nombre', 'descripcion')

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'telefono', 'total', 'metodo_pago', 'banco_origen', 'estado', 'fecha')
    list_filter = ('estado', 'metodo_pago', 'banco_origen', 'entrega', 'fecha')
    list_editable = ('estado',)
    search_fields = ('id', 'nombre', 'apellido', 'telefono', 'email', 'folio_transferencia')
    readonly_fields = ('fecha',)

@admin.register(MensajeContacto)
class MensajeContactoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'telefono', 'asunto', 'fecha', 'respondido')
    list_filter = ('respondido', 'fecha')
    search_fields = ('nombre', 'email', 'asunto', 'mensaje')
