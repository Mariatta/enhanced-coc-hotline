import json
import os

from webservice.__main__ import (
    get_nexmo_client,
    get_phone_number_owner,
    get_phone_numbers,
)

mock_private_key = """
-----BEGIN PRIVATE KEY-----
MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCxephXEnphnbrX
spKQR5hXvOFik/0PKvwt2u9/RXyae81rPH+bzJ1iQoYhnNjeGyluNLMewFvKMP9m
xeWgzMQ2O7CmqG/dYYeiTg==
-----END PRIVATE KEY-----
"""


mock_phone_numbers = [
    {"name": "Mariatta", "phone": "16040001234"},
    {"name": "Miss Islington", "phone": "17782223333"},
]


def test_get_nexmo_client(monkeypatch):
    monkeypatch.setitem(os.environ, "NEXMO_APP_ID", "app_id")
    monkeypatch.setitem(os.environ, "NEXMO_PRIVATE_KEY_VOICE_APP", mock_private_key)

    client = get_nexmo_client()
    assert client.application_id == "app_id"
    assert client.private_key == mock_private_key


def test_get_phone_numbers(monkeypatch):
    monkeypatch.setitem(os.environ, "PHONE_NUMBERS", json.dumps(mock_phone_numbers))

    phone_numbers = get_phone_numbers()
    assert phone_numbers == mock_phone_numbers


def test_get_phone_number_owner(monkeypatch):
    monkeypatch.setitem(os.environ, "PHONE_NUMBERS", json.dumps(mock_phone_numbers))

    owner = get_phone_number_owner(mock_phone_numbers[0]["phone"])
    assert owner == mock_phone_numbers[0]["name"]


def test_get_phone_number_owner_not_found(monkeypatch):
    monkeypatch.setitem(os.environ, "PHONE_NUMBERS", json.dumps(mock_phone_numbers))

    owner = get_phone_number_owner("0000000")
    assert owner is None
