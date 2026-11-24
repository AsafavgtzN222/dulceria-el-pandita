from django.db import models
import json


class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.CharField(max_length=50, blank=True)
    imagen = models.CharField(max_length=200, blank=True)
    stock = models.PositiveIntegerField(default=10, help_text="Cantidad disponible en inventario")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    @property
    def disponible(self):
        return self.stock > 0

    def __str__(self):
        return f"{self.nombre} (Stock: {self.stock})"


class Pedido(models.Model):
    ENTREGA_CHOICES = [
        ('Recoger en tienda', 'Recoger en tienda'),
        ('Envío a domicilio', 'Envío a domicilio'),
    ]
    PAGO_CHOICES = [
        ('transferencia', 'Transferencia bancaria (SPEI)'),
        ('whatsapp', 'WhatsApp'),
        ('efectivo', 'Efectivo'),
    ]
    ESTADO_CHOICES = [
        ('recibido', '🟡 Pedido recibido'),
        ('verificando_pago', '🏦 Verificando transferencia / SPEI'),
        ('en_preparacion', '🍬 En preparación'),
        ('en_camino', '🚚 Listo para recoger / En camino'),
        ('entregado', '✅ Entregado'),
        ('cancelado', '❌ Cancelado'),
    ]

    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100, blank=True)
    telefono = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    entrega = models.CharField(max_length=50, choices=ENTREGA_CHOICES)
    direccion = models.CharField(max_length=250, blank=True)
    metodo_pago = models.CharField(max_length=20, choices=PAGO_CHOICES)
    
    # Datos específicos para pago con transferencia bancaria (SPEI)
    banco_origen = models.CharField(max_length=60, blank=True, verbose_name="Banco emisor")
    titular_transferencia = models.CharField(max_length=100, blank=True, verbose_name="Titular emisor")
    cuenta_digitos = models.CharField(max_length=30, blank=True, verbose_name="Dígitos / Cuenta emisora")
    folio_transferencia = models.CharField(max_length=50, blank=True, verbose_name="Folio / Clave de rastreo SPEI")

    estado = models.CharField(max_length=30, choices=ESTADO_CHOICES, default='recibido', verbose_name="Estado del pedido")
    notas = models.TextField(blank=True)
    # Guardamos el carrito como JSON: [{"nombre":..., "precio":..., "cantidad":...}]
    items_json = models.TextField(default='[]')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fecha = models.DateTimeField(auto_now_add=True)

    def get_items(self):
        return json.loads(self.items_json)

    def __str__(self):
        return f"Pedido #{self.pk} - {self.nombre} ({self.get_estado_display()}) - ${self.total:.2f}"


class MensajeContacto(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField()
    asunto = models.CharField(max_length=100, blank=True)
    mensaje = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    respondido = models.BooleanField(default=False)

    def __str__(self):
        return f"Mensaje de {self.nombre} - {self.asunto} ({self.fecha:%d/%m/%Y %H:%M})"

