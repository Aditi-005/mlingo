"""Contains DTO classes"""


class ResponseDTO:
    """Response DTO"""

    def __init__(self, status, message, data):
        self.status = status
        self.message = message
        self.data = data
