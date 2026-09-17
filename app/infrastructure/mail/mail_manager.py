import aiofiles
from redis.asyncio import Redis
import resend
import secrets
from app.core.config import Settings
from app.domain.interfaces.mail.i_mail_manager import IMailManager


class MailManager(IMailManager):
    def __init__(self, state_client: Redis, settings: Settings):
        self.state_client = state_client
        self.settings = settings
        self.resend = resend
        self.resend.api_key = self.settings.RESEND_API_KEY

    async def _get_template_message(self, code: str) -> str:
        async with aiofiles.open("/app/templates/verify_email.html") as f:
            template = await f.read()
        return template.replace("{{code}}", code)

    def generate_verification_code(self) -> str:
        return f"{secrets.randbelow(1000000):06d}"

    async def send_mail_for_verify(self, email: str, code: str) -> str:
        template = await self._get_template_message(code)
        params: resend.Emails.SendParams = {
            "from": self.settings.TEST_MAIL,
            "to": [email],
            "subject": f"Код подтверждения: {code}",
            "html": template,
        }
        email_response: resend.Emails.SendResponse = (
            await self.resend.Emails.send_async(params)
        )
        return email_response["id"]
