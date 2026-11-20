import traceback
import logging
from django.http import HttpResponse

logger = logging.getLogger('django')


class ExceptionLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)
        except Exception as e:
            tb = traceback.format_exc()
            logger.error("EXCEPCION GLOBAL CAPTURADA:\n%s", tb)
            return HttpResponse(
                f"<html><body><h2>Error del Servidor Detallado:</h2><pre style='background:#f4f4f4;padding:15px;border:1px solid #ccc;'>{tb}</pre></body></html>",
                status=500,
                content_type="text/html"
            )
