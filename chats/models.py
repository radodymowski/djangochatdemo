import uuid

from django.db import models
from solo.models import SingletonModel

from chats.helpers import get_chat_message_media_dir


class Chat(models.Model):
    user_id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_id}, {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class ChatMessage(models.Model):
    chats = models.ManyToManyField(Chat, related_name="messages")
    created_at = models.DateTimeField(auto_now_add=True)

    message_text = models.TextField(blank=True)
    image = models.ImageField(blank=True, upload_to=get_chat_message_media_dir)

    class Meta:
        verbose_name = "Chat message"

    def __str__(self):
        return f"{self.created_at.strftime('%Y-%m-%d %H:%M')}: {self.message_text[:50]}"


class ApiTracker(SingletonModel):
    """Tracking model storing order number of last downloaded image from external API."""
    banner_counter = models.PositiveIntegerField(default=0)

    def count_new_banner(self):
        """Add new banner to counter when it was successfully downloaded."""
        self.banner_counter += 1
        self.save()
