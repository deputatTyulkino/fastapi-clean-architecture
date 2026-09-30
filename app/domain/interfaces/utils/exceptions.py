from typing import Any


class DomainError(Exception):
    """Базовая ошибка всего приложения (domain + service слои)."""

    default_message: str = "Domain error"

    def __init__(self, message: str | None = None, **context: Any) -> None:
        self.message = message or self.default_message
        self.context = context  # доп. данные для логов/ответа
        super().__init__(self.message)


class ValidationError(DomainError):
    """Нарушены инварианты/входные данные (замена ValueError)."""

    default_message = "Validation failed"


class BusinessRuleViolationError(DomainError):
    """Нарушено бизнес-правило (например, недостаточно товара на складе)."""

    default_message = "Business rule violated"


class EntityNotFoundError(DomainError):
    """Сущность не найдена. Базовый класс для всех *NotFoundError."""

    entity_name: str = "Entity"

    def __init__(self, identifier: Any = None, message: str | None = None) -> None:
        self.identifier = identifier
        if message is None:
            message = (
                f"{self.entity_name} not found"
                if identifier is None
                else f"{self.entity_name} with id={identifier!r} not found"
            )
        super().__init__(message, identifier=identifier)


class EntityAlreadyExistsError(DomainError):
    """Сущность уже существует (нарушение уникальности). Базовый класс."""

    entity_name: str = "Entity"

    def __init__(
        self, field: str | None = None, value: Any = None, message: str | None = None
    ) -> None:
        self.field = field
        self.value = value
        if message is None:
            message = (
                f"{self.entity_name} already exists"
                if field is None
                else f"{self.entity_name} with {field}={value!r} already exists"
            )
        super().__init__(message, field=field, value=value)


class PermissionDeniedError(DomainError):
    """Действие запрещено для данного пользователя."""

    default_message = "Permission denied"


class AuthenticationError(DomainError):
    """Не удалось аутентифицировать (неверные креды, истёк токен и т.п.)."""

    default_message = "Authentication failed"


class ProductNotFoundError(EntityNotFoundError):
    entity_name = "Product"


class CategoryNotFoundError(EntityNotFoundError):
    entity_name = "Category"


class UserNotFoundError(EntityNotFoundError):
    entity_name = "User"


class ProductAlreadyExistsError(EntityAlreadyExistsError):
    entity_name = "Product"


class CategoryAlreadyExistsError(EntityAlreadyExistsError):
    entity_name = "Category"


class UserAlreadyExistsError(EntityAlreadyExistsError):
    entity_name = "User"


class InsufficientStockError(BusinessRuleViolationError):
    default_message = "Insufficient stock"
