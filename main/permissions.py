from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

EDITOR_GROUP = "Editor"


def is_editor(user):
    return user.is_authenticated and user.groups.filter(name=EDITOR_GROUP).exists()


def can_edit(user):
    return user.is_authenticated and (user.is_superuser or is_editor(user))


def can_manage(user):
    return user.is_authenticated and user.is_superuser


def role_required(check):
    def decorator(view):
        @login_required
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            if not check(request.user):
                raise PermissionDenied
            return view(request, *args, **kwargs)
        return wrapper
    return decorator