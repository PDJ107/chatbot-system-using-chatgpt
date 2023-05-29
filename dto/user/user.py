from dataclasses import dataclass


@dataclass
class User:
    fcm_token: str
    user_id: str
    context_source: list
    context: bool = False
