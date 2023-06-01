import configparser
from firebase_admin import messaging


class FCM:
    def send_message(self, data: str, fcm_token: str, debug: bool = False):
        message = messaging.Message(
            data={
                'message': data
            },
            android=messaging.AndroidConfig(
                priority='high'
            ),
            apns=messaging.APNSConfig(
                headers={
                    'apns-priority': '10'
                }
            ),
            token=fcm_token
        )

        response = messaging.send(message)

        if debug:
            print(f'Send Message to User: ')
            print(data)
            print(response)

        return response


class SpecificFCM(FCM):
    def __init__(self, fcm_token: str):
        self.fcm_token = fcm_token

    def send_message(self, data: str, debug: bool = False):
        super().send_message(
            data=data,
            fcm_token=self.fcm_token,
            debug=debug
        )


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('resources/config.ini')

    fcm = FCM()
    print(
        fcm.send_message("Test message", config['FCM']['TEST_TOKEN'])
    )