from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse


class FullAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.allowed_paths = ['/login_user/', ] # '/logout_user/', '/admin/', '/static/', '/media/,

    def __call__(self, request):
        """Will check if user us authenticated and db is connected"""

        if request.path.startswith(tuple(self.allowed_paths)):
            return self.get_response(request)

        if not request.user.is_authenticated:
            messages.warning(request, "გთხოვთ გაიაროთ ავტორიზაცია!")
            return redirect(f'{reverse("login_user")}?next={request.path}')

        if not request.session.get('db_connected'):
            messages.warning(request, "საჭიროა ბაზასთან კავშირი")
            return redirect(f'{reverse("login_user")}?next={request.path}')

        return self.get_response(request)