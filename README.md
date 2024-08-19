# Django Chat Demo

### About
This project is a simulation of administration panel for chat and messages management.
It allows to connect with external API to download new banner photos and send it to all chats.

### Installation
1. Download the project repository.
2. Run `docker compose up -d`
3. After the container is up, run `docker compose run web python manage.py createsuperuser` to create your local admin account.
4. The application will be available under http://0.0.0.0:8000/admin

### Usage
For running banner send action - while logged in to admin, go to Chats list view, from actions dropdown select
`Send API banner to all chats` and click Go. You will be messaged about process result.
After successful run the new ChatMessage will be present in Chat messages admin view. 

### Testing
If the container is already built, run `docker compose run web python manage.py test` to run all unit tests.

