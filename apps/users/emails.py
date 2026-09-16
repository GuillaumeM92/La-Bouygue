import logging

from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def send_quietly(subject, message, recipient):
    """Send one e-mail. A failure is logged and never breaks the page."""
    try:
        send_mail(subject, message, None, [recipient])
    except Exception:
        logger.exception("Could not send %r to %s", subject, recipient)
        return False
    return True
