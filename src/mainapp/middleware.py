from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class BlockedUserAuthenticationBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        User = get_user_model()

        try:
            user = User.objects.get(username=username)

            # Check if the user is blocked
            if user.blocked:
                return None  # Return None to indicate blocked user

            # Check the user's password
            if user.check_password(password):
                return user  # Return the user if password is correct
        except User.DoesNotExist:
            return None  # Return None if user does not exist

    def get_user(self, user_id):
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
