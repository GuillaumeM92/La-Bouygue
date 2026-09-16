from .models import Announcement


def announcements(request):
    """Current announcements the member has not marked as read, for the pop-up."""
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return {}
    unread = Announcement.objects.current().exclude(read_by=user).select_related("author")
    return {"unread_announcements": list(unread)}
