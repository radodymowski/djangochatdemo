def get_chat_message_media_dir(instance, filename):
    """Return upload path for ChatMessage images in media directory."""
    return "chats/{0}/{1}".format(instance.pk, filename)
