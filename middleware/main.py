# analytics/middleware.py
import logging
from django.db import transaction
from django.utils import timezone
from analytics.models import VisitorLog
from core.language import TRACKABLE_PATHS
from accounts.models import CustomUser  # adjust if your model path differs
from .tracking import (
    should_track_path,
    get_client_ip,
    get_device_type,
    handle_user_page_visit,
)

logger = logging.getLogger(__name__)


class TrackVisitorMiddleware:
    """
    Middleware that:
    1. Logs the visitor in VisitorLog (existing behaviour)
    2. If user is authenticated, updates their `pages_viewed` JSONField
        (stored on CustomUser.pages_viewed)
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        try:
            path = request.path
            if not should_track_path(path):
                return response

            # Basic visitor log (existing)
            ip = get_client_ip(request)
            user_agent = request.META.get("HTTP_USER_AGENT", "unknown")
            referrer = request.META.get("HTTP_REFERER", "") or "ORGANIC"
            page_url = path
            device_type = get_device_type(user_agent)
            location = "NOT WORKING"  # existing placeholder

            VisitorLog.objects.create(
                ipaddress=ip,
                user_agent=user_agent,
                location=location,
                page_url=page_url,
                referre=referrer,
                device_type=device_type,
            )

            # Per-user tracking (new)
            user = getattr(request, "user", None)
            if user and user.is_authenticated:
                # Use a transaction to reduce race conditions when multiple requests
                # update pages_viewed concurrently for the same user
                try:
                    with transaction.atomic():
                        # NOTE: handle_user_page_visit will fetch, update, save
                        handle_user_page_visit(user, page_url, referrer, timestamp=timezone.now())
                except Exception:
                    logger.exception("Error updating user's pages_viewed")

        except Exception:
            # Don't raise from middleware; log and continue
            logger.exception("Middleware Error while tracking visitor")

        return response
