import logging

from rest_framework.views import exception_handler

from config.api.response import BaseResponse

logger = logging.getLogger("django")


def drf_base_exception_handler(exc, context):
    """
    The function `custom_exception_handler` handles custom exceptions by mapping them to specific
    handlers and returning a response with the appropriate status code and message.

    :param exc: The `exc` parameter is the exception object that was raised. It contains information
    about the exception, such as its type, message, and traceback
    :param context: The `context` parameter in the `custom_exception_handler` function is a dictionary
    that contains information about the current request and view that raised the exception. It typically
    includes the following keys:
    :return: a response object.
    """
    try:
        exception_class = exc.__class__.__name__

        handlers = {
            "NotAuthenticated": _handler_authentication_error,
            "InvalidToken": _handler_invalid_token_error,
        }
        res = exception_handler(exc, context)
        if exception_class in handlers:
            # calling hanlder based on the custom
            message = handlers[exception_class](exc, context, res)
        else:
            # if there is no hanlder is presnet
            message = str(exc)

        return BaseResponse(status=res.status_code, message=message)
    except Exception as e:
        logger.error(str(e))


def _handler_authentication_error(exc, context, response):
    """
    The function returns a message indicating that an authorization token is not provided.

    :param exc: The `exc` parameter is the exception object that was raised during the authentication
    process
    :param context: The `context` parameter is a dictionary that contains additional information about
    the error that occurred. It can include details such as the request that caused the error, the user
    who made the request, or any other relevant information
    :param response: The `response` parameter is the HTTP response object that will be returned to the
    client. It contains information such as the status code, headers, and body of the response
    :return: the string "An authorization token is not provided."
    """
    # UnAuthorized
    return "شما دسترسی ندارید"


def _handler_invalid_token_error(exc, context, response):
    """
    The function handles an invalid token error by returning a specific error message.

    :param exc: The `exc` parameter represents the exception that was raised. In this case, it would be
    an invalid token error
    :param context: The `context` parameter is a dictionary that contains additional information about
    the error that occurred. It can include details such as the request that caused the error, the user
    who made the request, or any other relevant information
    :param response: The `response` parameter is the HTTP response object that will be returned to the
    client. It contains information such as the status code, headers, and body of the response
    :return: the string "An authorization token is not valid."
    """
    return "توکن نا معتبر است"
