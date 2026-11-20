import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AvilaSite.settings")
django.setup()

from members.models import Producto

productos = [
    # nombre, descripcion, precio, categoria, imagen
    ("Paleta de Tamarindo", "Sabor intenso con cubierta de chile y sal. La favorita de todos.", 15, "paletas", "Paleta-tamarindo.jpeg"),
    ("Paleta de Mango", "Dulce y refrescante, con toque de chile. ¡No te la puedes perder!", 12, "paletas", "Paleta-mango.jpeg"),
    ("Paleta de Fresa", "Sabor natural de fresa, suave y dulce. Ideal para niños.", 10, "paletas", "Paleta-fresa.jpeg"),

    ("Chocolate Artesanal", "Elaborado con cacao seleccionado. Sabor intenso y cremoso.", 35, "chocolates", "Chocolate-artesanal.jpeg"),
    ("Chocolate con Leche", "Suave, cremoso y dulce. El clásico que nunca falla.", 28, "chocolates", "Chocolate-leche.jpeg"),
    ("Trufas Artesanales", "Hechas a mano, rellenas de ganache y cubiertas en cacao.", 45, "chocolates", "Trufas.jpeg"),

    ("Gomitas de Sandía", "Suaves y jugosas, sabor frutal inigualable. ¡Para toda la familia!", 20, "gomitas", "Gominolas-Sandia.jpeg"),
    ("Ositos de Goma", "Los clásicos de siempre: frutas mixtas en cada osito.", 18, "gomitas", "Panditas.jpeg"),
    ("Serpentinas de Gomita", "Largas, coloridas y con sabor a tutti fruti.", 12, "gomitas", "Serpentinas.jpeg"),

    ("Chilitos de Mango", "La combinación perfecta de dulce, agrio y picante.", 10, "enchilados", "Mango-enchilado.jpeg"),
    ("Pulparindo", "Tamarindo con chile y sal. Un sabor que siempre regresa.", 8, "enchilados", "Pulparindo.jpeg"),
    ("Mazapán Enchilado", "Mazapán de cacahuate con cubierta de chile. ¡Adictivo!", 12, "enchilados", "Mazapan-enchilado.jpeg"),

    ("Paquete Básico", "10 dulces surtidos en bolsa decorada. Ideal para detalles.", 80, "paquetes", "Paquete-basico.jpeg"),
    ("Caja Regalo Surtida", "25 dulces seleccionados en caja decorada con moño. ¡Un regalo perfecto!", 120, "paquetes", "Caja-surtida.jpeg"),
    ("Paquete Personalizado", "¡Tú eliges! Arma tu paquete con los dulces que más te gusten. Desde $50.", 50, "paquetes", "Caja-personalizada.jpeg"),
]

for nombre, desc, precio, cat, img in productos:
    obj, creado = Producto.objects.get_or_create(
        nombre=nombre,
        defaults={
            "descripcion": desc,
            "precio": precio,
            "categoria": cat,
            "imagen": img,
        },
    )
    print(("Creado: " if creado else "Ya existía: ") + nombre)

print("Total en la base de datos:", Producto.objects.count())