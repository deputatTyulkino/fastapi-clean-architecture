import httpx

from app.domain.interfaces.utils.i_payment_repo import (
    IPaymentRepo,
    IPaymentRequest,
    IPaymentResponse,
)


class PaymentRepo(IPaymentRepo):
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient()

    async def create_payment(
        self, payment_data: IPaymentRequest
    ) -> IPaymentResponse | None:
        async with self.client as c:
            response: httpx.Response = await c.post(
                f"{self.base_url}/v2/Init", data=payment_data
            )
            if response.status_code == httpx.codes.INTERNAL_SERVER_ERROR:
                return None
        return response.json()
