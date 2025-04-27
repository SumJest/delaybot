import base64

def encode_payload(action, token):
    payload = f"{action}:{token}"
    encoded = base64.b64encode(payload.encode()).decode()
    encoded = encoded.replace('+', '-').replace('/', '_').rstrip('=')
    return encoded
