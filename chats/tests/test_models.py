from django.test import TestCase
from freezegun import freeze_time
from uuid import UUID
from chats.models import Chat, ChatMessage


class ChatTestCase(TestCase):
    @freeze_time("2024-07-15 12:13")
    def test__created_default_values(self):
        # when
        chat = Chat.objects.create()

        # then
        self.assertTrue(UUID(str(chat.user_id), version=4))
        self.assertEqual(chat.created_at.year, 2024)
        self.assertEqual(chat.created_at.month, 7)
        self.assertEqual(chat.created_at.day, 15)
        self.assertEqual(chat.created_at.hour, 12)
        self.assertEqual(chat.created_at.minute, 13)

    @freeze_time("2024-07-15 12:13")
    def test__display(self):
        # when
        chat = Chat.objects.create()

        # then
        self.assertEqual(chat.__str__(), f"{chat.user_id}, 2024-07-15 12:13")


class ChatMessageTestCase(TestCase):
    def setUp(self):
        self.chat = Chat.objects.create()

    @freeze_time("2024-07-15 12:13")
    def test__created_default_values(self):
        # when
        chat_message = ChatMessage.objects.create()
        chat_message.chats.add(self.chat)

        # then
        self.assertIn(self.chat, chat_message.chats.all())
        self.assertEqual(chat_message.created_at.year, 2024)
        self.assertEqual(chat_message.created_at.month, 7)
        self.assertEqual(chat_message.created_at.day, 15)
        self.assertEqual(chat_message.created_at.hour, 12)
        self.assertEqual(chat_message.created_at.minute, 13)

    @freeze_time("2024-07-15 12:13")
    def test__display(self):
        # when
        chat_message = ChatMessage.objects.create(
            message_text="test message"
        )

        # then
        self.assertEqual(chat_message.__str__(), "2024-07-15 12:13: test message")

    @freeze_time("2024-07-15 12:13")
    def test__display_long_message(self):
        # when
        chat_message = ChatMessage.objects.create(
            message_text="this is longer message which exceeds display characters limit, "
                         "written for testing chat message display"
        )

        # then
        self.assertEqual(chat_message.__str__(),
                         "2024-07-15 12:13: this is longer message which exceeds display chara")
