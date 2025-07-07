from typing import Any, Dict

from rest_framework import serializers, status
from rest_framework_simplejwt.exceptions import ExpiredTokenError
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenViewBase


class CustomTokenRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField(read_only=True)
    token_class = RefreshToken

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, str]:
        refresh = self.token_class(attrs["refresh"])

        data = {
            "access": str(refresh.access_token),
            "access_exp": int(refresh.access_token.payload.get("exp", 0)),
        }

        # Don't rotate refresh tokens - keep the existing one
        # if api_settings.ROTATE_REFRESH_TOKENS:
        #     if api_settings.BLACKLIST_AFTER_ROTATION:
        #         try:
        #             # Attempt to blacklist the given refresh token
        #             refresh.blacklist()
        #         except AttributeError:
        #             # If blacklist app not installed, `blacklist` method will
        #             # not be present
        #             pass

        #     refresh.set_jti()
        #     refresh.set_exp()
        #     refresh.set_iat()

        #     data["refresh"] = str(refresh)

        return data


class CustomTokenRefreshView(TokenViewBase):
    """
    Takes a refresh type JSON web token and returns an access type JSON web
    token if the refresh token is valid.
    """

    serializer_class = CustomTokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        try:
            # Get refresh token from request data or cookies
            refresh_token = request.COOKIES.get("refresh_token")

            if not refresh_token:
                from config.api.response import BaseResponse

                return BaseResponse(
                    status=status.HTTP_400_BAD_REQUEST,
                    message="Refresh token not provided",
                )

            # Prepare data for serializer
            data = {"refresh": refresh_token}
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)

            # Return new tokens as cookies
            from config.api.response import JWTCookieResponse

            return JWTCookieResponse(
                data=None,  # No tokens in response body
                jwt_tokens=serializer.validated_data,
                status=status.HTTP_200_OK,
                message="Token refreshed successfully",
            )
        except ExpiredTokenError:
            # Clear cookies if token is expired
            from config.api.response import clear_jwt_cookies, BaseResponse

            response = BaseResponse(
                status=status.HTTP_401_UNAUTHORIZED, message="Token expired"
            )
            clear_jwt_cookies(response)
            return response
        except Exception as e:
            from config.api.response import BaseResponse

            return BaseResponse(
                status=status.HTTP_400_BAD_REQUEST,
                message=str(e) or "خطای نامشخصی رخ داده است.",
            )
