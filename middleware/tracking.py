
from django.utils import timezone
from django.conf import settings
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

# If TRACKABLE_PATHS is a list in core.language, using that here is fine.
from core.language import TRACKABLE_PATHS  # already referenced in middleware


def should_track_path(path: str) -> bool:
    """
    Return True if path is in the trackable list (or meets rules).
    Centralized here in case you want to add prefixes, regex, etc later.
    """
    return path in TRACKABLE_PATHS


def get_client_ip(request) -> str:
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        # First IP in X-Forwarded-For is the originating IP
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR") or "0.0.0.0"
    return ip


def get_device_type(user_agent: str) -> str:
    ua = (user_agent or "").lower()
    if "mobile" in ua:
        return "Mobile"
    if "tablet" in ua:
        return "Tablet"
    if "windows" in ua or "macintosh" in ua or "linux" in ua:
        return "Desktop"
    return "Unknown"


def _find_page_entry(pages_list: list, page_url: str):
    for entry in pages_list:
        if entry.get("page") == page_url:
            return entry
    return None


def handle_user_page_visit(user, page_url: str, referrer_url: str = "", timestamp=None):
    """
    Update `user.pages_viewed` JSONField with:
    [
      {
        "page": "/",
        "times": 5,
        "timestamps": ["2025-09-16T21:00:00Z", ...],
        "referrer_urls": ["https://...", ...]
      },
      ...
    ]
    Ensures:
    - Uses a defensive read-modify-write pattern within a transaction to reduce races.
    - Saves only the pages_viewed field.
    """
    if not user or not getattr(user, "is_authenticated", False):
        return

    if timestamp is None:
        timestamp = timezone.now()

    # Ensure pages_viewed field exists and is a list
    pages = getattr(user, "pages_viewed", None)
    if pages is None:
        pages = []

    if not isinstance(pages, list):
        # Defensive: if stored something else, reset to empty list
        logger.warning("pages_viewed for user %s is not a list. Resetting.", getattr(user, "pk", "<unknown>"))
        pages = []

    # Find existing entry
    page_entry = _find_page_entry(pages, page_url)

    iso_ts = timestamp.isoformat()

    if page_entry:
        # update counters and append timestamps/referrers
        page_entry["times"] = int(page_entry.get("times", 0)) + 1
        page_entry.setdefault("timestamps", []).append(iso_ts)
        page_entry.setdefault("referrer_urls", []).append(referrer_url or "ORGANIC")
    else:
        # create a new entry
        new_entry = {
            "page": page_url,
            "times": 1,
            "timestamps": [iso_ts],
            "referrer_urls": [referrer_url or "ORGANIC"],
        }
        pages.append(new_entry)

    # Write back safely using transaction (important if callers didn't wrap)
    # It's usually better to re-fetch user from DB, but here we assume caller provides a fresh user object (request.user).
    # To reduce staleness, fetch the instance from DB and update it.
    from django.contrib.auth import get_user_model

    User = get_user_model()

    # Reload user from db with a lock when supported
    try:
        with transaction.atomic():
            fresh_user = User.objects.select_for_update().get(pk=user.pk)
            fresh_user.pages_viewed = pages
            fresh_user.save(update_fields=["pages_viewed"])
    except Exception:
        # Best-effort fallback: try to save without select_for_update
        try:
            user.pages_viewed = pages
            user.save(update_fields=["pages_viewed"])
        except Exception:
            logger.exception("Failed to save pages_viewed for user %s", getattr(user, "pk", "<unknown>"))
            raise
