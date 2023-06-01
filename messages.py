import configparser
import firebase_admin
from firebase_admin import messaging, credentials


class FCM:
    def send_message(self, data: str, fcm_token: str, debug: bool = False, final: bool = False):
        message = messaging.Message(
            data={
                'message': data,
                'final': 'true' if final else 'false'
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

    def send_message(self, data: str, debug: bool = False, final: bool = False):
        super().send_message(
            data=data,
            fcm_token=self.fcm_token,
            debug=debug,
            final=final
        )


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('resources/config.ini')

    cred = credentials.Certificate(config['FCM']['KEY_PATH'])
    firebase_admin.initialize_app(cred)

    fcm = FCM()
    print(
        fcm.send_message("Test message", config['FCM']['TEST_TOKEN'], final=True)
    )
