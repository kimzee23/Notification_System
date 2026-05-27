from firebase_admin import credentials, initialize_app, messaging
import firebase_admin


class FirebaseClient:

    def __init__(self, service_account_path: str):

        if not firebase_admin._apps:

            cred = credentials.Certificate(
                service_account_path
            )

            initialize_app(cred)

        self.messaging = messaging

    async def send_async(self, message):

        # Firebase SDK is sync
        # wrap later with asyncio.to_thread if needed

        return self.messaging.send(message)