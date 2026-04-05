from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        error_message = "An error occurred."

        # Extract readable message from DRF's response data
        data = response.data
        if isinstance(data, dict):
            # Grab first meaningful error message
            for key, value in data.items():
                if isinstance(value, list):
                    error_message = f"{key}: {value[0]}" if key != 'non_field_errors' else str(value[0])
                else:
                    error_message = str(value)
                break
        elif isinstance(data, list):
            error_message = str(data[0])
        elif isinstance(data, str):
            error_message = data

        return Response({
            "success": False,
            "error": error_message,
            "code": response.status_code
        }, status=response.status_code)

    # Unhandled server errors
    return Response({
        "success": False,
        "error": "Something went wrong. Please try again later.",
        "code": 500
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)