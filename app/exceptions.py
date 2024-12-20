class ReviewServiceError(Exception):
    """
    Custom exception for review service-related errors.

    Attributes:
        message (str): The error message describing the issue.
        details (Optional[dict]): Additional context or metadata about the error.
    """

    def __init__(self, message: str, details: dict = None):
        """
        Initialize the ReviewServiceError with a message and optional details.

        Args:
            message (str): The error message.
            details (dict, optional): Additional details or context for debugging (default: None).
        """
        super().__init__(message)
        self.message = message
        self.details = details

    def __str__(self):
        """
        Return a string representation of the error.

        Returns:
            str: The error message, along with additional details if provided.
        """
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message
