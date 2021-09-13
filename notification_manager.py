import os
from twilio.rest import Client

#
#
ACCOUNT_SID = os.environ.get('ACCOUNT_SID')
AUTH_TOKEN = os.environ.get('AUTH_TOKEN')
TWILLIO_PHONE_NO = os.environ.get('TWILLIO_PHONE_NO')


class NotificationManager:

    def send_message(self, message: str, phone_no: str):
        """Accepts a message input and phone Number as arguments, and sends an sms"""
        client = Client(ACCOUNT_SID, AUTH_TOKEN)

        message = client.messages \
            .create(
                body=message,
                from_=TWILLIO_PHONE_NO,
                to=phone_no
            )
        print(message.sid)


