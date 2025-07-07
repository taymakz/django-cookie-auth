from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError


class JWTCookieAuthentication(JWTAuthentication):
    """
    Custom JWT authentication that reads tokens from cookies instead of headers.
    """

    def authenticate(self, request):
        """
        Returns a two-tuple of `User` and token if a valid signature has been
        supplied using JWT-based authentication. Otherwise returns `None`.
        """
        # First try to get token from cookies
        raw_token = request.COOKIES.get("access_token")

        if raw_token is None:
            # Fall back to default header-based authentication
            return super().authenticate(request)

        try:
            validated_token = self.get_validated_token(raw_token)
            user = self.get_user(validated_token)
            return (user, validated_token)
        except TokenError:
            # If cookie token is invalid, try header-based authentication
            return super().authenticate(request)
