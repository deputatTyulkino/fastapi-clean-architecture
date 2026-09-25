import hashlib
import secrets

import aiofiles
import resend
from redis.asyncio import Redis

from app.core.config import Settings
from app.domain.interfaces.logging.i_logger import ILogger
from app.domain.interfaces.mail.i_mail_manager import IMailManager

_TEMPLATE_PATH = "/app/templates/verify_email.html"


class MailManager(IMailManager):
    def __init__(self, state_client: Redis, settings: Settings, logger: ILogger):
        self.state_client = state_client
        self.settings = settings
        self.resend = resend
        self.resend.api_key = self.settings.RESEND_API_KEY
        self.logger = logger.bind(component="MailManager")

    async def _get_template_message(self, code: str) -> str:
        try:
            async with aiofiles.open(_TEMPLATE_PATH) as f:
                template = await f.read()
        except OSError:
            self.logger.exception(
                "verification_email_template_missing", template_path=_TEMPLATE_PATH
            )
            raise
        return template.replace("{{code}}", code)

    def generate_verification_code(self) -> str:
        return f"{secrets.randbelow(1000000):06d}"

    async def send_mail_for_verify(self, email: str, code: str) -> str:
        email_ref = hashlib.sha256(email.encode()).hexdigest()[:12]
        template = await self._get_template_message(code)
        params: resend.Emails.SendParams = {
            "from": self.settings.TEST_MAIL,
            "to": [email],
            "subject": f"Код подтверждения: {code}",
            "html": template,
        }
        try:
            email_response: resend.Emails.SendResponse = (
                await self.resend.Emails.send_async(params)
            )
        except Exception:
            self.logger.exception("verification_email_send_failed", email_ref=email_ref)
            raise
        self.logger.info(
            "verification_email_sent",
            email_ref=email_ref,
            message_id=email_response["id"],
        )
        return email_response["id"]
