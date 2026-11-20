import urllib.request
import urllib.parse
import http.cookiejar
import re

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

print("Iniciando GET para obtener cookies y CSRF token...")
res = opener.open('https://dulceria-el-pandita.onrender.com/contacto/')
html = res.read().decode('utf-8')
match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', html)
token = match.group(1) if match else None
print('CSRF Token obtenido:', token)

data = urllib.parse.urlencode({
    'csrfmiddlewaretoken': token,
    'nombre': 'Prueba Asaf',
    'apellido': 'Avila',
    'telefono': '8137122570',
    'email': 'asaflocouavli@gmail.com',
    'asunto': 'Información sobre productos',
    'mensaje': 'Mensaje de prueba en vivo'
}).encode('utf-8')

req = urllib.request.Request('https://dulceria-el-pandita.onrender.com/contacto/', data=data)
req.add_header('Referer', 'https://dulceria-el-pandita.onrender.com/contacto/')
req.add_header('Origin', 'https://dulceria-el-pandita.onrender.com')

try:
    resp_post = opener.open(req)
    print('POST Status:', resp_post.status)
    body = resp_post.read().decode('utf-8')
    print('Respuesta recibida:', body[:400])
except urllib.error.HTTPError as e:
    print('HTTPError Code:', e.code)
    print('HTTPError Reason:', e.reason)
    error_body = e.read().decode('utf-8', errors='ignore')
    print('Error Body:', error_body[:1000])
except Exception as e:
    print('Exception:', e)
