from .models import Visitor, PageView
import requests

class VisitorStatsMiddleware:
    """Middleware to track page visits and visitor info."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = self.get_client_ip(request)
        page_name = request.resolver_match.view_name if request.resolver_match else request.path
        url = request.build_absolute_uri()

        visitor, created = Visitor.objects.get_or_create(ip_address=ip)

        # Optionally: Get country using a free geolocation API
        if created:
            try:
                response = requests.get(f'https://ipapi.co/{ip}/json/')
                data = response.json()
                visitor.country = data.get('country_name')
                visitor.city = data.get('city')
                visitor.save()
            except:
                pass

        # Record the page view
        PageView.objects.create(visitor=visitor, page_name=page_name, url=url)

        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
