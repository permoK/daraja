import resend
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend

class ResendEmailBackend(BaseEmailBackend):
    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently)
        resend.api_key = settings.RESEND_API_KEY

    def send_messages(self, email_messages):
        for message in email_messages:
            try:
                resend.Emails.send({
                    "from":"admin@wilfredeveloper.me",
                    "to": message.to,
                    "subject": message.subject,
                    "html": message.body,
                })
            except Exception as e:
                if not self.fail_silently:
                    raise e
        return len(email_messages)
