from django.http import HttpResponseForbidden

def role_required(*roles):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if hasattr(request.user, 'profile') and request.user.profile.role in roles:
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("You don’t have permission to access this page.")
        return _wrapped_view
    return decorator
