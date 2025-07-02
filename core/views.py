from django.shortcuts import render
import logging

logger = logging.getLogger(__name__)

def custom_404(request, exception):
    try:
        return render(request, "core/404.html", status=404)
    except Exception as e:
        logger.error(f"404 view error: {e}")
        return render(request, "core/error_fallback.html", {"message": str(e)}, status=500)

def home(request):
    return render(request, 'core/home.html')

def custom_404(request, exception):
    return render(request, "core/404.html", status=404)