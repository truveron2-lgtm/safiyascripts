from django.db.utils import ProgrammingError, OperationalError
from .models import Visitor, PageView
import requests

class VisitorStatsMiddleware:
    """Middleware to track page visits and visitor info safely."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get IP and page details
        ip = self.get_client_ip(request)
        page_name = request.resolver_match.view_name if request.resolver_match else request.path
        url = request.build_absolute_uri()

        try:
            # Ensure database tables exist before accessing
            visitor, created = Visitor.objects.get_or_create(ip_address=ip)

            # Optionally get country/city on first visit
            if created:
                try:
                    response = requests.get(f'https://ipapi.co/{ip}/json/', timeout=3)
                    if response.status_code == 200:
                        data = response.json()
                        visitor.country = data.get('country_name')
                        visitor.city = data.get('city')
                        visitor.save()
                except Exception:
                    # Skip if API call fails (no crash)
                    pass

            # Record the page view
            PageView.objects.create(visitor=visitor, page_name=page_name, url=url)

        except (ProgrammingError, OperationalError):
            # Happens if tables don't exist (e.g., before migrate)
            pass

        # Continue request-response cycle
        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        """Extract client IP from headers."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
