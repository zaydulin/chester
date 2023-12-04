from django.contrib import messages
from django.contrib.auth import logout
from django.urls import reverse
from django.shortcuts import redirect

class BlockedUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the user is authenticated and blocked
        if request.user.is_authenticated and request.user.blocked:
            # Log the user out
            logout(request)

            # Add a message to indicate that the user is blocked
            messages.error(request, "Ваш аккаунт заблокирован.")

            # Redirect the user to a suitable page (e.g., home)
            return redirect(reverse('home'))

        response = self.get_response(request)
        return response
