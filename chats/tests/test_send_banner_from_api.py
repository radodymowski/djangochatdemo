from unittest import mock
from unittest.mock import MagicMock, ANY

import requests.exceptions
from django.test import TestCase

from chats.exceptions import BannerAPINoPhotosException, BannerAPIUnexpectedError, BannerAPIInvalidPhotoDataException
from chats.models import Chat, ApiTracker
from chats.services.send_banner_from_api import send_banner_from_api


class SendBannerFromApiTest(TestCase):
    def setUp(self):
        self.chat_1 = Chat.objects.create()
        self.chat_2 = Chat.objects.create()

        self.mock_response_success = {
            "success": True,
            "photos": [
                {
                    "id": 1,
                    "description": "test description 1",
                    "url": "https://example.com/photo/1.jpeg",
                    "title": "test photo 1",
                    "user": 1
                },
            ]
        }

        self.mock_response_no_photos = {
            "success": True,
            "photos": []
        }

        self.mock_response_invalid_photo_data = {
            "success": True,
            "photos": [
                {
                    "id": 2,
                    "description": "description, but no title!",
                    "user": 2
                }
            ]
        }

    @mock.patch("requests.get")
    @mock.patch("os.path.basename")
    @mock.patch("django.db.models.fields.files.FieldFile.save")
    def test_send_banner_from_api(self, mock_image_save, mock_basename, mock_get):
        # given
        mock_get.side_effect = [
            MagicMock(status_code=200, json=MagicMock(return_value=self.mock_response_success)),
            MagicMock(status_code=200, content=b"test image content")
        ]
        mock_basename.return_value = "1.jpeg"

        # when
        send_banner_from_api()

        # then
        self.assertEqual(self.chat_1.messages.count(), 1)
        self.assertEqual(self.chat_2.messages.count(), 1)

        created_message = self.chat_1.messages.first()
        self.assertEqual(created_message.message_text, "test photo 1")
        mock_image_save.assert_called_once_with("1.jpeg", ANY, save=True)

        api_tracker = ApiTracker.objects.get()
        self.assertEqual(api_tracker.banner_counter, 1)

    @mock.patch("requests.get")
    def test_send_banner_from_api__error(self, mock_get):
        # given
        mock_get.return_value = MagicMock(status_code=200, json=MagicMock(return_value={"success": False, "photos": "error"}))

        # when / then
        with self.assertRaises(BannerAPIUnexpectedError):
            send_banner_from_api()

    @mock.patch("requests.get")
    def test_send_banner_from_api__no_photos(self, mock_get):
        # given
        mock_get.return_value = MagicMock(status_code=200, json=MagicMock(return_value=self.mock_response_no_photos))

        # when / then
        with self.assertRaises(BannerAPINoPhotosException):
            send_banner_from_api()

    @mock.patch("requests.get")
    def test_send_banner_from_api__invalid_image_data(self, mock_get):
        # given
        mock_get.return_value = MagicMock(status_code=200, json=MagicMock(return_value=self.mock_response_invalid_photo_data))

        # when / then
        with self.assertRaises(BannerAPIInvalidPhotoDataException):
            send_banner_from_api()

    @mock.patch("requests.get")
    def test_send_banner_from_api__http_error(self, mock_get):
        # given
        mock_get.side_effect = requests.exceptions.HTTPError("HTTP Error")

        # when / then
        with self.assertRaises(requests.exceptions.HTTPError):
            send_banner_from_api()

    @mock.patch("requests.get")
    def test_send_banner_from_api__http_error_on_image_download(self, mock_get):
        # given
        mock_get.side_effect = [
            MagicMock(status_code=200, json=MagicMock(return_value=self.mock_response_success)),
            requests.exceptions.HTTPError("HTTP Error")
        ]

        # when / then
        with self.assertRaises(requests.exceptions.HTTPError):
            send_banner_from_api()
        self.assertEqual(mock_get.call_count, 2)
