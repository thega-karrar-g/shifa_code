import json
import requests
import os
from google.oauth2 import service_account
import google.auth.transport.requests


class FCMService:

    def send_fcm_request(self, type_key, type_val, is_ios, rec):
        # Initialize the base data structure
        data = {"message": {}}

        # Add the notification section only if is_ios is True
        if is_ios:
            data["message"]['notification'] = {
                'title': '{0}'.format(rec.name_ar),
                'body': '{0}'.format(rec.content_ar),
                'image': rec.get_image_url('image', 'sm.app.notification', str(rec.id)),
            }

        # Add the type and to fields
        data["message"][type_key] = type_val

        # Add additional data
        data["message"]["data"] = {
            "title_ar": '{0}'.format(rec.name_ar),
            "title_en": '{0}'.format(rec.name_en),
            "body_ar": '{0}'.format(rec.content_ar),
            "body_en": '{0}'.format(rec.content_en),
            "image": rec.get_image_url('image', 'sm.app.notification', str(rec.id)),
        }

        # Set the URL and headers
        url = 'https://fcm.googleapis.com/v1/projects/globe-care-6b8d8/messages:send'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {0}'.format(self._get_access_token())
        }

        # Send the request
        response = requests.post(url=url, json=data, headers=headers, timeout=120)

        # Debugging output
        # print('=====================')
        # print(response.request.headers)
        # print(response.request.body)
        # print(response.content)
        # print('=====================')

    def _get_access_token(self):
        try:
            # Get the path to the JSON file relative to your module
            module_path = os.path.dirname(__file__)
            file_path = os.path.join(module_path, 'private', 'globe-care-firebase-fcm.json')
            #print('file_path', file_path)

            # Load the credentials from the JSON file
            with open(file_path, 'r') as f:
                credentials = service_account.Credentials.from_service_account_info(json.load(f), scopes=[
                    'https://www.googleapis.com/auth/cloud-platform'])

            # Refresh the token if it's expired
            request = google.auth.transport.requests.Request()
            credentials.refresh(request)

            #print('token', credentials.token)
            return credentials.token
        except Exception as e:
            # Handle exceptions appropriately
            #print(f"Error retrieving access token: {e}")
            return None  # Or raise an exception
