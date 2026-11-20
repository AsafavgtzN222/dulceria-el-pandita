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
        ('transferencia', 'Transferencia'),
        ('whatsapp', 'WhatsApp'),
        ('efectivo', 'Efectivo'),
    ]

    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100, blank=True)
    telefono = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    entrega = models.CharField(max_length=50, choices=ENTREGA_CHOICES)
    direccion = models.CharField(max_length=250, blank=True)
    metodo_pago = models.CharField(max_length=20, choices=PAGO_CHOICES)
    notas = models.TextField(blank=True)
    # Guardamos el carrito como JSON: [{"nombre":..., "precio":..., "cantidad":...}]
    items_json = models.TextField(default='[]')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fecha = models.DateTimeField(auto_now_add=True)

    def get_items(self):
        return json.loads(self.items_json)

    def __str__(self):
        return f"Pedido #{self.pk} - {self.nombre} ({self.fecha:%d/%m/%Y})"
