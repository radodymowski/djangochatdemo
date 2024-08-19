import requests
from django.contrib import admin, messages
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME

from chats.exceptions import BannerAPIUnexpectedError, BannerAPINoPhotosException, BannerAPIInvalidPhotoDataException
from chats.models import ChatMessage, Chat
from chats.services.send_banner_from_api import send_banner_from_api


@admin.action(description="Send API banner to all Chats")
def send_api_banner(modeladmin, request, queryset):
    """Action for calling send_banner_from_api service from Chat admin."""
    try:
        send_banner_from_api()
        messages.success(request, "New banner successfully sent to all chats.")
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

    # this is a kind of hack to allow running action without need to select any Chat in admin
    def changelist_view(self, request, extra_context=None):
        if "action" in request.POST and request.POST["action"] == "send_api_banner":
            if not request.POST.getlist(ACTION_CHECKBOX_NAME):
                post = request.POST.copy()
                for obj in Chat.objects.all():
                    post.update({ACTION_CHECKBOX_NAME: str(obj.user_id)})
                request._set_post(post)
        return super().changelist_view(request, extra_context)


class ChatMessageAdmin(admin.ModelAdmin):
    readonly_fields = (
        "created_at",
    )

admin.site.register(Chat, ChatAdmin)
admin.site.register(ChatMessage, ChatMessageAdmin)
