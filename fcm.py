import configparser
import firebase_admin
from firebase_admin import credentials, messaging


class Fcm:
    def __init__(self, config_path='resources/config.ini'):
        config = configparser.ConfigParser()
        config.read(config_path)

        cred = credentials.Certificate(config['FCM']['KEY_PATH'])
        firebase_admin.initialize_app(cred)

    def send_message(self, data: str, fcm_token):
        message = messaging.Message(
            data={
                'message': data
            },
            token=fcm_token
        )

        response = messaging.send(message)

        print(data)
        print(response)
        return response


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('resources/config.ini')

    fcm = Fcm()
    print(
        fcm.send_message("Test message", config['FCM']['TEST_TOKEN'])
    )