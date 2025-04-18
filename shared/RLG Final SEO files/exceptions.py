class BaseRLGException(Exception):
    """
    Base class for all custom exceptions in RLG Data and RLG Fans.
    """
    def __init__(self, message=None, code=None):
        self.message = message or "An unknown error occurred."
        self.code = code or 500
        super().__init__(self.message)

    def to_dict(self):
        """
        Converts the exception details to a dictionary for standardized error responses.
        """
        return {
            'error': self.__class__.__name__,
            'message': self.message,
            'code': self.code,
        }


# Authentication & Authorization Exceptions
class AuthenticationFailed(BaseRLGException):
    def __init__(self, message="Authentication failed. Invalid credentials.", code=401):
        super().__init__(message, code)


class PermissionDenied(BaseRLGException):
    def __init__(self, message="Permission denied. You do not have access to this resource.", code=403):
        super().__init__(message, code)


# Validation Exceptions
class ValidationError(BaseRLGException):
    def __init__(self, message="Input validation error.", code=400):
        super().__init__(message, code)


class MissingRequiredField(ValidationError):
    def __init__(self, field_name, message=None, code=400):
        message = message or f"The field '{field_name}' is required and missing."
        super().__init__(message, code)


# Resource Exceptions
class ResourceNotFound(BaseRLGException):
    def __init__(self, resource_name="Resource", code=404):
        message = f"{resource_name} not found."
        super().__init__(message, code)


class ResourceConflict(BaseRLGException):
    def __init__(self, resource_name="Resource", code=409):
        message = f"Conflict with existing {resource_name}."
        super().__init__(message, code)


# Integration Exceptions
class IntegrationError(BaseRLGException):
    def __init__(self, service_name="External Service", message=None, code=502):
        message = message or f"Failed to integrate with {service_name}."
        super().__init__(message, code)


class APIRequestFailed(IntegrationError):
    def __init__(self, service_name="External Service", status_code=None, message=None, code=502):
        status_message = f" (Status Code: {status_code})" if status_code else ""
        message = message or f"The request to {service_name} failed{status_message}."
        super().__init__(service_name, message, code)


# General Server Exceptions
class InternalServerError(BaseRLGException):
    def __init__(self, message="An unexpected error occurred on the server.", code=500):
        super().__init__(message, code)


class ServiceUnavailable(BaseRLGException):
    def __init__(self, service_name="Service", message=None, code=503):
        message = message or f"{service_name} is currently unavailable. Please try again later."
        super().__init__(message, code)


# Usage Example
if __name__ == "__main__":
    try:
        raise ResourceNotFound(resource_name="User")
    except BaseRLGException as e:
        print(e.to_dict())
