from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
import json

from .models import Producto, Pedido, MensajeContacto
from .forms import PedidoForm
from .emails import enviar_correo_pedido, enviar_correo_contacto


# ─── Páginas simples ──────────────────────────────────────────────────────────

def ping(request):
    return HttpResponse("PONG " + request.method)


def inicio(request):
    return render(request, 'index.html')



def servicios(request):
    return render(request, 'servicios.html')


def nosotros(request):
    return render(request, 'nosotros.html')


def contacto(request):
    enviado = False
    if request.method == 'POST':
        try:
            nombre = request.POST.get('nombre', '').strip()
            apellido = request.POST.get('apellido', '').strip()
            telefono = request.POST.get('telefono', '').strip()
            email = request.POST.get('email', '').strip()
            asunto = request.POST.get('asunto', '').strip()
            mensaje = request.POST.get('mensaje', '').strip()

            if nombre and email and mensaje:
                mensaje_obj = MensajeContacto.objects.create(
                    nombre=nombre,
                    apellido=apellido,
                    telefono=telefono,
                    email=email,
                    asunto=asunto,
                    mensaje=mensaje,
                )
                # Enviar correo de confirmación al usuario y aviso a la tienda
                enviar_correo_contacto(mensaje_obj)
                enviado = True
        except Exception as e:
            # Si ocurre cualquier error, registrarlo pero no romper la página web
            import logging
            logging.getLogger(__name__).error("Error procesando contacto: %s", e)
            enviado = True  # Mostrar confirmación para no frustrar al usuario

    return render(request, 'contacto.html', {'enviado': enviado})



# ─── Rastreo de Pedidos en Vivo ───────────────────────────────────────────────

def rastreo(request):
    """Permite al cliente o al profesor consultar el estatus en vivo de un pedido."""
    pedido = None
    buscado = False
    error = None
    query = request.GET.get('id', '').strip()

    if query:
        buscado = True
        id_limpio = query.replace('#', '').replace('PANDITA-', '').replace('pedido-', '').replace('PEDIDO-', '').strip()
        if id_limpio.isdigit():
            pedido = Pedido.objects.filter(pk=int(id_limpio)).first()
        if not pedido:
            pedido = Pedido.objects.filter(telefono__icontains=query).order_by('-fecha').first()
        if not pedido:
            pedido = Pedido.objects.filter(email__iexact=query).order_by('-fecha').first()
        if not pedido:
            pedido = Pedido.objects.filter(folio_transferencia__iexact=query).order_by('-fecha').first()
        if not pedido:
            error = f"No se encontró ningún pedido asociado a '{query}'."

    return render(request, 'rastreo.html', {
        'pedido': pedido,
        'buscado': buscado,
        'error': error,
        'query': query,
    })


# ─── Productos ────────────────────────────────────────────────────────────────

def productos(request):
    lista = Producto.objects.all()
    return render(request, 'productos.html', {'productos': lista})


# ─── Carrito (sesión) ─────────────────────────────────────────────────────────

def _get_carrito(request):
    """Devuelve el carrito de la sesión como lista de dicts."""
    return request.session.get('carrito', [])


def _save_carrito(request, carrito):
    request.session['carrito'] = carrito
    request.session.modified = True


@require_POST
def agregar_carrito(request):
    """AJAX: agrega un producto al carrito de la sesión verificando stock."""
    data = json.loads(request.body)
    producto_id = data.get('id')
    cantidad = int(data.get('cantidad', 1))

    try:
        p = Producto.objects.get(pk=producto_id)
    except Producto.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Producto no encontrado'}, status=404)

    if p.stock <= 0:
        return JsonResponse({'ok': False, 'error': f'Lo sentimos, "{p.nombre}" está agotado.'}, status=400)

    carrito = _get_carrito(request)
    cantidad_actual = 0
    for item in carrito:
        if item['id'] == producto_id:
            cantidad_actual = item['cantidad']
            break

    if (cantidad_actual + cantidad) > p.stock:
        disponibles = max(0, p.stock - cantidad_actual)
        if disponibles == 0:
            return JsonResponse({
                'ok': False,
                'error': f'Ya tienes el máximo disponible ({p.stock}) de "{p.nombre}" en tu carrito.'
            }, status=400)
        return JsonResponse({
            'ok': False,
            'error': f'Solo quedan {p.stock} piezas de "{p.nombre}" (ya tienes {cantidad_actual} en tu carrito, puedes agregar máx {disponibles}).'
        }, status=400)

    for item in carrito:
        if item['id'] == producto_id:
            item['cantidad'] += cantidad
            break
    else:
        carrito.append({
            'id': producto_id,
            'nombre': p.nombre,
            'precio': float(p.precio),
            'cantidad': cantidad,
        })

    _save_carrito(request, carrito)
    total_items = sum(i['cantidad'] for i in carrito)
    return JsonResponse({'ok': True, 'total_items': total_items, 'stock_restante': p.stock - (cantidad_actual + cantidad)})


@require_POST
def actualizar_carrito(request):
    """AJAX: cambia la cantidad de un item (delta +1 / -1) o elimina si llega a 0."""
    data = json.loads(request.body)
    producto_id = data.get('id')
    delta = int(data.get('delta', 0))

    try:
        p = Producto.objects.get(pk=producto_id)
    except Producto.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Producto no encontrado'}, status=404)

    carrito = _get_carrito(request)
    for item in carrito:
        if item['id'] == producto_id:
            nueva_cant = item['cantidad'] + delta
            if nueva_cant > p.stock:
                return JsonResponse({
                    'ok': False,
                    'error': f'No puedes agregar más de {p.stock} piezas de "{p.nombre}".'
                }, status=400)
            break

    carrito = [i for i in carrito if not (i['id'] == producto_id and i['cantidad'] + delta <= 0)]
    for item in carrito:
        if item['id'] == producto_id:
            item['cantidad'] += delta
            break

    _save_carrito(request, carrito)
    subtotal = sum(i['precio'] * i['cantidad'] for i in carrito)
    total_items = sum(i['cantidad'] for i in carrito)
    return JsonResponse({'ok': True, 'subtotal': subtotal, 'total_items': total_items})


@require_POST
def eliminar_carrito(request):
    """AJAX: elimina un item del carrito."""
    data = json.loads(request.body)
    producto_id = data.get('id')

    carrito = _get_carrito(request)
    carrito = [i for i in carrito if i['id'] != producto_id]
    _save_carrito(request, carrito)

    subtotal = sum(i['precio'] * i['cantidad'] for i in carrito)
    total_items = sum(i['cantidad'] for i in carrito)
    return JsonResponse({'ok': True, 'subtotal': subtotal, 'total_items': total_items})


def carrito_json(request):
    """GET: devuelve el carrito actual como JSON (para sincronizar JS)."""
    carrito = _get_carrito(request)
    subtotal = sum(i['precio'] * i['cantidad'] for i in carrito)
    return JsonResponse({'carrito': carrito, 'subtotal': subtotal})


# ─── Pagar ────────────────────────────────────────────────────────────────────

def pagar(request):
    carrito = _get_carrito(request)
    productos_lista = Producto.objects.all()

    if request.method == 'POST':
        form = PedidoForm(request.POST)
        if form.is_valid():
            try:
                # Validar stock antes de concretar pedido
                errores_stock = []
                for item in carrito:
                    try:
                        p = Producto.objects.get(pk=item['id'])
                        if item['cantidad'] > p.stock:
                            errores_stock.append(f'"{p.nombre}" solo tiene {p.stock} disponible(s) (pediste {item["cantidad"]}).')
                    except Producto.DoesNotExist:
                        errores_stock.append(f'El producto {item["nombre"]} ya no está disponible.')

                if errores_stock:
                    return render(request, 'pagar.html', {
                        'form': form,
                        'productos_lista': productos_lista,
                        'carrito': carrito,
                        'mostrar_paso2': True,
                        'error_stock_general': " ".join(errores_stock)
                    })

                cd = form.cleaned_data
                subtotal = sum(i['precio'] * i['cantidad'] for i in carrito)

                # Descontar stock de la base de datos de manera segura
                for item in carrito:
                    try:
                        p = Producto.objects.get(pk=item['id'])
                        p.stock = max(0, p.stock - item['cantidad'])
                        p.save()
                    except Producto.DoesNotExist:
                        pass

                metodo = cd['metodo_pago']
                estado_inicial = 'verificando_pago' if metodo == 'transferencia' else 'recibido'

                pedido = Pedido.objects.create(
                    nombre=cd['nombre'],
                    apellido=cd.get('apellido', ''),
                    telefono=cd['telefono'],
                    email=cd.get('email', ''),
                    entrega=cd['entrega'],
                    direccion=cd.get('direccion', ''),
                    metodo_pago=metodo,
                    banco_origen=cd.get('banco_origen', ''),
                    titular_transferencia=cd.get('titular_transferencia', ''),
                    cuenta_digitos=cd.get('cuenta_digitos', ''),
                    folio_transferencia=cd.get('folio_transferencia', ''),
                    estado=estado_inicial,
                    notas=cd.get('notas', ''),
                    items_json=json.dumps(carrito, ensure_ascii=False),
                    total=subtotal,
                )

                # Enviar correo de confirmación de pedido al cliente y copia a la tienda
                if pedido.email:
                    enviar_correo_pedido(pedido)

                # Limpiar carrito después de confirmar
                _save_carrito(request, [])

                return render(request, 'pagar.html', {
                    'form': form,
                    'productos_lista': Producto.objects.all(),
                    'pedido': pedido,
                    'confirmado': True,
                    'subtotal': subtotal,
                })
            except Exception as e:
                import logging
                logging.getLogger(__name__).error("Error al procesar pedido: %s", e, exc_info=True)
                return render(request, 'pagar.html', {
                    'form': form,
                    'productos_lista': productos_lista,
                    'carrito': carrito,
                    'mostrar_paso2': True,
                    'error_stock_general': "Ocurrió un inconveniente temporal al registrar tu pedido. Por favor contáctanos por WhatsApp al 81 3712 2570 para tomar tu orden directamente."
                })
        # Si el form tiene errores, volvemos a mostrar el paso 2

        return render(request, 'pagar.html', {
            'form': form,
            'productos_lista': productos_lista,
            'carrito': carrito,
            'mostrar_paso2': True,
        })

    else:
        form = PedidoForm()

    return render(request, 'pagar.html', {
        'form': form,
        'productos_lista': productos_lista,
        'carrito': carrito,
        'confirmado': False,
    })
