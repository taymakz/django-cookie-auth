"""
JWT Cookie Response Module

This module provides a custom response class that sets JWT tokens as HTTP-only cookies
instead of returning them in the response body for enhanced security.

Cookie Settings:
- refresh_token: HTTP-only, lifetime from SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'], secure (for production with HTTPS)
- access_token: HTTP-only, lifetime from SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'], secure (for production with HTTPS)
- access_exp: Regular cookie (readable by frontend), same lifetime as access_token, secure

Note: In production, ensure HTTPS is enabled and set secure=True for all cookies.
For development over HTTP, you may need to set secure=False.
"""

from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from datetime import datetime
from django.conf import settings

from config.api.enums import ResponseMessage
from django.core.paginator import EmptyPage


def clear_jwt_cookies(response):
    """
    Utility function to clear all JWT-related cookies from a response.

    Args:
        response: Django Response object to clear cookies from
    """
    cookie_domain = getattr(settings, "JWT_COOKIE_DOMAIN", None)

    response.delete_cookie("refresh_token", domain=cookie_domain)
    response.delete_cookie("access_token", domain=cookie_domain)
    response.delete_cookie("access_exp", domain=cookie_domain)


class BaseResponse(Response):
    def __init__(self, data=None, message: str = "", status: int = 500):
        response_data = {
            "success": True if status // 100 == 2 else False,
            "status": status,
            "message": message,
            "data": data,
        }
        super().__init__(response_data)


class JWTCookieResponse(BaseResponse):
    def __init__(
        self, data=None, message: str = "", status: int = 500, jwt_tokens=None
    ):
        # Remove JWT tokens from response data if they exist
        if data and isinstance(data, dict):
            filtered_data = {
                k: v
                for k, v in data.items()
                if k not in ["refresh", "access", "access_exp"]
            }
            if jwt_tokens:
                # Add only the expiration date to response data (not HTTP-only)
                filtered_data["access_exp"] = jwt_tokens.get("access_exp")
            data = filtered_data if filtered_data else None

        super().__init__(data, message, status)

        # Set JWT tokens as cookies if provided
        if jwt_tokens:
            # Get cookie settings from Django settings
            cookie_secure = getattr(settings, "JWT_COOKIE_SECURE", False)
            cookie_samesite = getattr(settings, "JWT_COOKIE_SAMESITE", "Lax")
            cookie_domain = getattr(settings, "JWT_COOKIE_DOMAIN", None)

            # Get token lifetimes from SIMPLE_JWT settings
            simple_jwt = getattr(settings, "SIMPLE_JWT", {})
            access_token_lifetime = simple_jwt.get("ACCESS_TOKEN_LIFETIME")
            refresh_token_lifetime = simple_jwt.get("REFRESH_TOKEN_LIFETIME")

            # Convert timedelta to seconds, fallback to default values
            access_max_age = (
                int(access_token_lifetime.total_seconds())
                if access_token_lifetime
                else 60
            )
            refresh_max_age = (
                int(refresh_token_lifetime.total_seconds())
                if refresh_token_lifetime
                else 365 * 24 * 60 * 60
            )

            # Set refresh token as HTTP-only cookie
            if "refresh" in jwt_tokens:
                self.set_cookie(
                    "refresh_token",
                    jwt_tokens["refresh"],
                    max_age=refresh_max_age,
                    httponly=True,
                    secure=cookie_secure,
                    samesite=cookie_samesite,
                    domain=cookie_domain,
                )

            # Set access token as HTTP-only cookie
            if "access" in jwt_tokens:
                self.set_cookie(
                    "access_token",
                    jwt_tokens["access"],
                    max_age=refresh_max_age,
                    httponly=True,
                    secure=cookie_secure,
                    samesite=cookie_samesite,
                    domain=cookie_domain,
                )

            # Set access token expiration as regular cookie (not HTTP-only)
            if "access_exp" in jwt_tokens:
                self.set_cookie(
                    "access_exp",
                    str(jwt_tokens["access_exp"]),
                    max_age=access_max_age,  # Same as access token
                    httponly=False,  # Not HTTP-only so frontend can read it
                    secure=cookie_secure,
                    samesite=cookie_samesite,
                    domain=cookie_domain,
                )


class PaginationApiResponse(PageNumberPagination):
    page_size_query_param = "take"
    page_query_param = "page"
    page_size = 20
    max_page_size = 100

    def get_paginated_response(self, data) -> BaseResponse:
        current_page = self.page.number
        page_count = self.page.paginator.num_pages
        pagination = {
            "entity_count": self.page.paginator.count,
            "current_page": self.page.number,
            "page_count": self.page.paginator.num_pages,
            "start_page": max(current_page - 2, 1),
            "end_page": min(current_page + 2, page_count),
            "take": self.page.paginator.per_page,
            "has_next": self.page.has_next(),
            "has_previous": self.page.has_previous(),
            "data": data,
        }
        return BaseResponse(
            data=pagination,
            status=status.HTTP_200_OK,
            message=ResponseMessage.SUCCESS.value,
        )

    def paginate_queryset(self, queryset, request, view=None):
        """
        Paginate a queryset if required, either returning a
        page object, or `None` if pagination is not configured for this view.
        """
        page_size = self.get_page_size(request)
        if not page_size:
            return None

        # Ensure page_size is an integer
        if isinstance(page_size, (list, tuple)):
            page_size = page_size[0] if page_size else self.page_size
        page_size = int(page_size) if page_size else self.page_size

        paginator = self.django_paginator_class(queryset, page_size)
        page_number = self.get_page_number(request, paginator)

        try:
            self.page = paginator.page(page_number)
        except EmptyPage:
            self.page = paginator.page(paginator.num_pages)

        if paginator.num_pages > 1 and self.template is not None:
            # The browsable API should display pagination controls.
            self.display_page_controls = True

        self.request = request
        return list(self.page)
