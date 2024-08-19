import os
from urllib.parse import urlparse

import requests
from django.conf import settings
from django.core.files.base import ContentFile

from chats.exceptions import BannerAPIUnexpectedError, BannerAPINoPhotosException, BannerAPIInvalidPhotoDataException
from chats.models import ChatMessage, Chat, ApiTracker


def send_banner_from_api() -> None:
    """
    Get next banner message from external API and send it to all active chats.

    Connects with external API, tries to retrieve next unsent banner message, then on success
    creates new ChatMessage instance and adds to all Chat instances.

    Raises:
        BannerAPIUnexpectedError if no success response from API.
        BannerAPINoPhotosException if API returns no more available banners.
        BannerAPIInvalidPhotoDataException if retrieved image data is malformed (cannot retrieve its URL and title).
        requests.exceptions.HTTPError if any API call returns unsuccessful status code.
    """
    # Get current offset from api_tracker
    api_tracker = ApiTracker.objects.get_or_create()[0]
    offset = api_tracker.banner_counter

    # Connect with external API and retrieve one image data (offset keeps the order of image retrieving)
    response = requests.get(settings.BANNERS_API_URL, params={"offset": offset, "limit": 1})
    response.raise_for_status()

    # Validate data response
    response_json = response.json()
    if not response_json.get("success", False):
        raise BannerAPIUnexpectedError("Unexpected banner API Error. Please try again later.")

    image_data = response_json.get("photos")
    if not image_data:
        raise BannerAPINoPhotosException("Error - no new photos to download.")

    try:
        image_url = response_json["photos"][0]["url"]
        image_text = response_json["photos"][0]["title"]
    except (KeyError, AttributeError):
        raise BannerAPIInvalidPhotoDataException("Error - invalid image data.")

    # Download image from retrieved image URL
    download_image_response = requests.get(image_url)
    download_image_response.raise_for_status()
    image_filename = os.path.basename(urlparse(image_url).path)


    # Create new chat message instance and save downloaded image onto.
    new_message = ChatMessage.objects.create(
        message_text=image_text
    )
    new_message.image.save(image_filename, ContentFile(download_image_response.content), save=True)

    # When new chat message containing downloaded banner was successfully created, increase banner count to download
    # next banner on next call.
    api_tracker.count_new_banner()

    # Send new ChatMessage to all chats
    new_message.chats.add(*Chat.objects.all())
