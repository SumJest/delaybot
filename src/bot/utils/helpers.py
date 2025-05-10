import base64
import typing


def encode_payload(action, token) -> str:
    payload = f"{action}:{token}"
    encoded = base64.b64encode(payload.encode()).decode()
    encoded = encoded.replace('+', '-').replace('/', '_').rstrip('=')
    return encoded


def decode_payload(encoded) -> typing.Tuple[str, str]:
    encoded = encoded.replace('-', '+').replace('_', '/')
    padding = '=' * (-len(encoded) % 4)
    encoded += padding

    decoded_bytes = base64.b64decode(encoded)
    decoded_str = decoded_bytes.decode()

    action, token = decoded_str.split(':', 1)
    return action, token
