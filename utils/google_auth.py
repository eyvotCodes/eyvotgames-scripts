#!/usr/bin/python3
import requests

def refresh_access_token(client_id, client_secret, refresh_token):
    token_url = "https://oauth2.googleapis.com/token"
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    }

    response = requests.post(token_url, data=payload)
    if response.status_code == 200:
        data = response.json()
        print(data)
        new_access_token = data["access_token"]
        new_expires_in = data["expires_in"]
        print("new_access_token:", new_access_token)
        return new_access_token, new_expires_in
    else:
        print("Error al renovar el access token:", response.text)
        return None, None


refresh_access_token(
    "[client_id]",
    "[client_secret]",
    "[refresh_token]"
)
