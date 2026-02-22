class InvalidStateTransition(Exception):
    pass


class PermissionDenied(Exception):
    pass


class RuleViolation(Exception):
    def __init__(self, message: str, failure_codes: list[str] | None = None):
        super().__init__(message)
        self.failure_codes: list[str] = failure_codes or []


class PaymentError(Exception):
    pass
