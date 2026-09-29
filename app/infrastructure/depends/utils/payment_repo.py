from app.core.config import Settings, get_settings
from app.domain.interfaces.utils.i_payment_repo import IPaymentRepo
from app.infrastructure.utils.payment_repo import PaymentRepo


def get_payment_repo_infr() -> IPaymentRepo:
    settings: Settings = get_settings()
    return PaymentRepo(settings.TBANK_URL)
