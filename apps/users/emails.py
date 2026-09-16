import logging

from django.core.mail import EmailMessage

logger = logging.getLogger(__name__)


def send_quietly(subject, message, recipient, reply_to=None):
    """Send one e-mail. A failure is logged and never breaks the page."""
    try:
        EmailMessage(subject, message, None, [recipient], reply_to=[reply_to] if reply_to else None).send()
    except Exception:
        logger.exception("Could not send %r to %s", subject, recipient)
        return False
    return True
