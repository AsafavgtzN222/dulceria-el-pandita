import logging
import threading
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

logger = logging.getLogger(__name__)


def _enviar_correo_en_hilo(msg):
    """Ejecuta el envío de correo en segundo plano sin congelar la web."""
    try:
        msg.send(fail_silently=True)
        logger.info("Correo enviado a %s", msg.to)
    except Exception as e:
        logger.warning("Aviso: no se pudo entregar correo a %s: %s", msg.to, e)


def enviar_correo_pedido(pedido):
    """
    Envía un correo de confirmación de compra al cliente y una copia de aviso a la tienda
    en segundo plano para evitar timeouts del servidor.
    """
    if not pedido.email:
        return False

    try:
        items = pedido.get_items()
        items_texto = "\n".join([f"- {it.get('nombre')} x{it.get('cantidad')} : ${float(it.get('precio', 0)) * int(it.get('cantidad', 1)):.2f} MXN" for it in items])
        items_html = "".join([
            f"<tr>"
            f"<td style='padding:8px 12px;border-bottom:1px solid #eee;'>{it.get('nombre')}</td>"
            f"<td style='padding:8px 12px;border-bottom:1px solid #eee;text-align:center;'>{it.get('cantidad')}</td>"
            f"<td style='padding:8px 12px;border-bottom:1px solid #eee;text-align:right;'>${float(it.get('precio', 0)):.2f}</td>"
            f"<td style='padding:8px 12px;border-bottom:1px solid #eee;text-align:right;font-weight:bold;'>${float(it.get('precio', 0)) * int(it.get('cantidad', 1)):.2f}</td>"
            f"</tr>"
            for it in items
        ])

        nombre_completo = f"{pedido.nombre} {pedido.apellido}".strip()
        direccion_info = f"\nDirección de entrega: {pedido.direccion}" if pedido.direccion else ""

        asunto = f"🐼 ¡Confirmación de Pedido #{pedido.pk}! - El Pandita Dulcería"
        mensaje_texto = f"""¡Hola {nombre_completo}!

¡Muchas gracias por tu compra en El Pandita Dulcería!
Hemos recibido con éxito tu pedido #{pedido.pk}.

RESUMEN DE TU PEDIDO:
{items_texto}

TOTAL: ${pedido.total:.2f} MXN
MÉTODO DE ENTREGA: {pedido.entrega}{direccion_info}
MÉTODO DE PAGO: {pedido.metodo_pago.capitalize()}
TELÉFONO DE CONTACTO: {pedido.telefono}
NOTAS: {pedido.notas or 'Ninguna'}

Nos comunicaremos contigo a la brevedad por WhatsApp o llamada para coordinar la entrega.
WhatsApp oficial: 81 3712 2570

¡Gracias por endulzar tu día con nosotros!
El Pandita Dulcería 🍬
"""

        mensaje_html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{ font-family: 'Segoe UI', Helvetica, Arial, sans-serif; background-color: #FFF8F0; margin: 0; padding: 20px; color: #333; }}
    .container {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }}
    .header {{ background: linear-gradient(135deg, #E63946, #c1121f); padding: 30px 20px; text-align: center; color: white; }}
    .header h1 {{ margin: 0; font-size: 26px; }}
    .header p {{ margin: 8px 0 0; opacity: 0.9; font-size: 15px; }}
    .content {{ padding: 25px 30px; }}
    .badge {{ display: inline-block; background: #FFD166; color: #2D2D2D; font-weight: bold; padding: 4px 12px; border-radius: 50px; font-size: 13px; margin-bottom: 15px; }}
    table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
    th {{ background: #f8f9fa; padding: 10px 12px; text-align: left; font-size: 13px; color: #666; text-transform: uppercase; }}
    .total-box {{ background: #fdf2f2; border: 2px dashed #E63946; border-radius: 12px; padding: 15px; text-align: right; margin: 20px 0; font-size: 18px; font-weight: bold; color: #E63946; }}
    .info-card {{ background: #FFF8F0; border-radius: 12px; padding: 15px; margin-bottom: 20px; font-size: 14px; line-height: 1.6; }}
    .btn-wa {{ display: inline-block; background: #25D366; color: white; text-decoration: none; padding: 12px 24px; border-radius: 50px; font-weight: bold; font-size: 15px; margin: 15px 0; }}
    .footer {{ background: #2D2D2D; color: #aaa; text-align: center; padding: 20px; font-size: 12px; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>¡Gracias por tu pedido! 🍬</h1>
      <p>El Pandita Dulcería</p>
    </div>
    <div class="content">
      <span class="badge">Pedido #{pedido.pk}</span>
      <h2 style="color:#2D2D2D;margin-top:0;">¡Hola {nombre_completo}!</h2>
      <p>Hemos recibido tu pedido con éxito y ya lo estamos preparando con mucho cariño:</p>
      
      <table>
        <thead>
          <tr>
            <th>Producto</th>
            <th style="text-align:center;">Cant.</th>
            <th style="text-align:right;">Precio</th>
            <th style="text-align:right;">Subtotal</th>
          </tr>
        </thead>
        <tbody>
          {items_html}
        </tbody>
      </table>

      <div class="total-box">
        Total a pagar: ${pedido.total:.2f} MXN
      </div>

      <div class="info-card">
        <strong>📦 Modalidad de entrega:</strong> {pedido.entrega}<br>
        {f'<strong>📍 Dirección:</strong> {pedido.direccion}<br>' if pedido.direccion else ''}
        <strong>💳 Método de pago:</strong> {pedido.metodo_pago.capitalize()}<br>
        <strong>📞 Teléfono:</strong> {pedido.telefono}<br>
        {f'<strong>📝 Notas:</strong> {pedido.notas}<br>' if pedido.notas else ''}
      </div>

      <p style="text-align:center;">¿Tienes alguna duda o quieres confirmar detalles?</p>
      <div style="text-align:center;">
        <a href="https://wa.me/528137122570?text=Hola%20El%20Pandita,%20tengo%20una%20duda%20sobre%20mi%20pedido%20%23{pedido.pk}" class="btn-wa" target="_blank">
          💬 Contactar por WhatsApp (81 3712 2570)
        </a>
      </div>
    </div>
    <div class="footer">
      <p style="margin:0 0 5px;">El Pandita Dulcería • Col. San Juan, Xicoténcatl, Tamaulipas</p>
      <p style="margin:0;">Horario: Lunes a Sábado de 9:00 am a 8:00 pm</p>
    </div>
  </div>
</body>
</html>
"""

        remitente = getattr(settings, 'DEFAULT_FROM_EMAIL', 'asaflocouavli@gmail.com')
        tienda_email = getattr(settings, 'TIENDA_NOTIFY_EMAIL', 'asaflocouavli@gmail.com')

        # 1. Enviar al cliente en hilo asíncrono
        msg_cliente = EmailMultiAlternatives(
            subject=asunto,
            body=mensaje_texto,
            from_email=remitente,
            to=[pedido.email],
        )
        msg_cliente.attach_alternative(mensaje_html, "text/html")
        hilo_cli = threading.Thread(target=_enviar_correo_en_hilo, args=(msg_cliente,))
        hilo_cli.daemon = True
        hilo_cli.start()

        # 2. Notificar a la tienda en hilo asíncrono
        if tienda_email and tienda_email.lower() != pedido.email.lower():
            asunto_tienda = f"🚨 [NUEVO PEDIDO #{pedido.pk}] {nombre_completo} - ${pedido.total:.2f} MXN"
            msg_tienda = EmailMultiAlternatives(
                subject=asunto_tienda,
                body=f"Se ha recibido el pedido #{pedido.pk}.\nCliente: {nombre_completo}\nTel: {pedido.telefono}\nEmail: {pedido.email}\n\nDetalle:\n{items_texto}\n\nTotal: ${pedido.total:.2f} MXN",
                from_email=remitente,
                to=[tienda_email],
            )
            msg_tienda.attach_alternative(mensaje_html, "text/html")
            hilo_tienda = threading.Thread(target=_enviar_correo_en_hilo, args=(msg_tienda,))
            hilo_tienda.daemon = True
            hilo_tienda.start()

        return True
    except Exception as e:
        logger.error("Error al preparar correo de pedido #%s: %s", pedido.pk, e)
        return False


def enviar_correo_contacto(mensaje_obj):
    """
    Envía un correo de confirmación de mensaje recibido al cliente y notifica a la tienda
    en segundo plano sin bloquear la página web.
    """
    if not mensaje_obj.email:
        return False

    try:
        nombre_completo = f"{mensaje_obj.nombre} {mensaje_obj.apellido}".strip()
        asunto_tema = mensaje_obj.asunto or "Consulta general"

        asunto_cliente = f"💬 Hemos recibido tu mensaje - El Pandita Dulcería"
        mensaje_texto = f"""¡Hola {nombre_completo}!

Gracias por ponerte en contacto con El Pandita Dulcería.
Hemos recibido tu mensaje con éxito:

Tema: {asunto_tema}
Teléfono: {mensaje_obj.telefono or 'No especificado'}
Mensaje:
"{mensaje_obj.mensaje}"

Nuestro equipo revisará tu solicitud y te responderemos lo más pronto posible.
WhatsApp oficial: 81 3712 2570.

¡Que tengas un excelente día! 🐼
El Pandita Dulcería
"""

        mensaje_html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{ font-family: 'Segoe UI', Helvetica, Arial, sans-serif; background-color: #FFF8F0; margin: 0; padding: 20px; color: #333; }}
    .container {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }}
    .header {{ background: linear-gradient(135deg, #2A9D8F, #21867a); padding: 30px 20px; text-align: center; color: white; }}
    .header h1 {{ margin: 0; font-size: 24px; }}
    .content {{ padding: 25px 30px; }}
    .card-msg {{ background: #FFF8F0; border-left: 4px solid #2A9D8F; border-radius: 8px; padding: 15px 20px; margin: 20px 0; font-style: italic; }}
    .btn-wa {{ display: inline-block; background: #25D366; color: white; text-decoration: none; padding: 12px 24px; border-radius: 50px; font-weight: bold; font-size: 14px; margin: 15px 0; }}
    .footer {{ background: #2D2D2D; color: #aaa; text-align: center; padding: 20px; font-size: 12px; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>¡Hemos recibido tu mensaje! 💌</h1>
      <p style="margin:5px 0 0;opacity:0.9;">El Pandita Dulcería</p>
    </div>
    <div class="content">
      <p>Hola <strong>{nombre_completo}</strong>,</p>
      <p>Muchas gracias por escribirnos. Confirmamos que tu mensaje sobre <strong>"{asunto_tema}"</strong> ha llegado a nuestro equipo:</p>
      
      <div class="card-msg">
        "{mensaje_obj.mensaje}"
      </div>

      <p>Te responderemos a la brevedad posible.</p>

      <div style="text-align:center;margin-top:25px;">
        <p style="margin-bottom:8px;font-size:13px;color:#666;">¿Necesitas respuesta inmediata?</p>
        <a href="https://wa.me/528137122570?text=Hola%20El%20Pandita,%20te%20escrib%C3%AD%20desde%20la%20web" class="btn-wa" target="_blank">
          💬 Escríbenos por WhatsApp (81 3712 2570)
        </a>
      </div>
    </div>
    <div class="footer">
      <p style="margin:0 0 5px;">El Pandita Dulcería • Col. San Juan, Xicoténcatl, Tamaulipas</p>
    </div>
  </div>
</body>
</html>
"""

        remitente = getattr(settings, 'DEFAULT_FROM_EMAIL', 'asaflocouavli@gmail.com')
        tienda_email = getattr(settings, 'TIENDA_NOTIFY_EMAIL', 'asaflocouavli@gmail.com')

        # 1. Enviar al cliente en hilo asíncrono
        msg_cliente = EmailMultiAlternatives(
            subject=asunto_cliente,
            body=mensaje_texto,
            from_email=remitente,
            to=[mensaje_obj.email],
        )
        msg_cliente.attach_alternative(mensaje_html, "text/html")
        hilo_cli = threading.Thread(target=_enviar_correo_en_hilo, args=(msg_cliente,))
        hilo_cli.daemon = True
        hilo_cli.start()

        # 2. Notificar a la tienda en hilo asíncrono
        if tienda_email:
            asunto_tienda = f"📩 [NUEVO CONTACTO] {nombre_completo} - {asunto_tema}"
            msg_tienda = EmailMultiAlternatives(
                subject=asunto_tienda,
                body=f"Nuevo mensaje:\nNombre: {nombre_completo}\nEmail: {mensaje_obj.email}\nTel: {mensaje_obj.telefono}\nAsunto: {asunto_tema}\n\nMensaje:\n{mensaje_obj.mensaje}",
                from_email=remitente,
                to=[tienda_email],
            )
            hilo_tienda = threading.Thread(target=_enviar_correo_en_hilo, args=(msg_tienda,))
            hilo_tienda.daemon = True
            hilo_tienda.start()

        return True
    except Exception as e:
        logger.error("Error al preparar correo de contacto: %s", e)
        return False
