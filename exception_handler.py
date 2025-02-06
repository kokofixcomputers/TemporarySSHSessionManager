class DistroValidationError(Exception):
    """Base class for distro validation errors."""

    pass


class MissingFieldError(DistroValidationError):
    """Raised when a required field is missing in a distro."""

    def __init__(self, field, distro_name):
        super().__init__(
            f"Validation Error: '{field}' is required for '{distro_name}'."
        )


class DefaultDistroError(DistroValidationError):
    """Raised when there is not exactly one default distro."""

    def __init__(self, count):
        super().__init__(
            f"Validation Error: There must be exactly one default distro set to True, found: {count}."
        )


class NoDistrosError(DistroValidationError):
    """Raised when no distros are provided."""

    def __init__(self):
        super().__init__("Validation Error: At least one distro must be provided.")
