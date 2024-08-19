import requests
from django.contrib import admin, messages
import timeout_decorator

from chats.exceptions import BannerAPIUnexpectedError, BannerAPINoPhotosException, BannerAPIInvalidPhotoDataException
from chats.models import ChatMessage, Chat
from chats.services.send_banner_from_api import send_banner_from_api


@admin.action(description="Send API banner to all Chats")
def send_api_banner(modeladmin, request, queryset):
    try:
        send_banner_from_api()
        messages.success(request, "New banner successfully sent to all chats.")
    except timeout_decorator.TimeoutError:
        messages.error(request, "Could not perform an action - timeout")
    except (
            BannerAPIUnexpectedError,
            BannerAPINoPhotosException,
            BannerAPIInvalidPhotoDataException,
            requests.exceptions.HTTPError
    ) as exc:
        messages.error(request, f"Could not perform an action - {str(exc)}")


class ChatAdmin(admin.ModelAdmin):
    readonly_fields = (
        "user_id",
        "created_at"
    )

    actions = [send_api_banner]


class ChatMessageAdmin(admin.ModelAdmin):
    readonly_fields = (
        "created_at",
    )

admin.site.register(Chat, ChatAdmin)
admin.site.register(ChatMessage, ChatMessageAdmin)
