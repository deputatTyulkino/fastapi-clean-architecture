from abc import ABC, abstractmethod
from typing import TypedDict


class IItem(TypedDict):
    Name: str
    Price: int
    Quantity: int
    Amount: int
    Tax: str


class IReceipt(TypedDict):
    Items: list[IItem]
    Email: str
    Taxation: str


class IPaymentRequest(TypedDict):
    TerminalKey: str
    Amount: int
    OrderId: str
    Token: str
    Description: str
    CustomerKey: str
    Recurrent: str
    NotificationURL: str
    Receipt: IReceipt


class IPaymentWebhookRequest(IPaymentRequest):
    Success: bool
    Status: str
    PaymentId: str
    ErrorCode: int
    Message: str
    Token: str


class IPaymentResponse(TypedDict):
    Success: bool
    Status: str
    PaymentId: str
    OrderId: str
    PaymentURL: str


class IPaymentRepo(ABC):
    @abstractmethod
    async def create_payment(
        self, payment_data: IPaymentRequest
    ) -> IPaymentResponse | None:
        raise NotImplementedError()
