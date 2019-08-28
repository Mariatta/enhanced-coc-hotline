import json
import os
from unittest import mock

import pytest
from aiohttp import web

from webservice.__main__ import (
    MUSIC_WHILE_YOU_WAIT,
    get_nexmo_client,
    get_phone_number_owner,
    get_phone_numbers,
    routes,
)

MOCK_API_KEY = "apikey"

MOCK_API_SECRET = "sssh"

MOCK_PRIVATE_KEY = """
-----BEGIN PRIVATE KEY-----
MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCxephXEnphnbrX
spKQR5hXvOFik/0PKvwt2u9/RXyae81rPH+bzJ1iQoYhnNjeGyluNLMewFvKMP9m
xeWgzMQ2O7CmqG/dYYeiTg==
-----END PRIVATE KEY-----
"""


MOCK_PHONE_NUMBERS = [
    {"name": "Mariatta", "phone": "16040001234"},
    {"name": "Miss Islington", "phone": "17782223333"},
]

MOCK_HOTLINE_DESC = "PyCascades Head Office"


def test_get_nexmo_client(monkeypatch):
    monkeypatch.setitem(os.environ, "NEXMO_API_KEY", MOCK_API_KEY)
    monkeypatch.setitem(os.environ, "NEXMO_API_SECRET", MOCK_API_SECRET)
    monkeypatch.setitem(os.environ, "NEXMO_APP_ID", "app_id")
    monkeypatch.setitem(os.environ, "NEXMO_PRIVATE_KEY_VOICE_APP", MOCK_PRIVATE_KEY)
    monkeypatch.setitem(os.environ, "HOTLINE_DESC", MOCK_HOTLINE_DESC)

    client = get_nexmo_client()
    assert client.application_id == "app_id"
    assert client.private_key == MOCK_PRIVATE_KEY
    assert client.api_key == MOCK_API_KEY
    assert client.api_secret == MOCK_API_SECRET


def test_get_phone_numbers(monkeypatch):
    monkeypatch.setitem(os.environ, "PHONE_NUMBERS", json.dumps(MOCK_PHONE_NUMBERS))

    phone_numbers = get_phone_numbers()
    assert phone_numbers == MOCK_PHONE_NUMBERS


def test_get_phone_number_owner(monkeypatch):
    monkeypatch.setitem(os.environ, "PHONE_NUMBERS", json.dumps(MOCK_PHONE_NUMBERS))

    owner = get_phone_number_owner(MOCK_PHONE_NUMBERS[0]["phone"])
    assert owner == MOCK_PHONE_NUMBERS[0]["name"]


def test_get_phone_number_owner_not_found(monkeypatch):
    monkeypatch.setitem(os.environ, "PHONE_NUMBERS", json.dumps(MOCK_PHONE_NUMBERS))

    owner = get_phone_number_owner("0000000")
    assert owner is None


class FakeNexmoClient:
    def __init__(self):
        self.calls_created = []
        self.speech_sent = []
        self.messages_sent = []

    def create_call(self, params=None, **kwargs):
        self.calls_created.append(params)

    def send_speech(self, params=None, **kwargs):
        self.speech_sent.append(params)

    def send_message(self, params=None, **kwargs):
        self.messages_sent.append(params)


@pytest.fixture
def webservice_cli(loop, aiohttp_client, monkeypatch):
    monkeypatch.setitem(os.environ, "PHONE_NUMBERS", json.dumps(MOCK_PHONE_NUMBERS))
    monkeypatch.setitem(os.environ, "NEXMO_APP_ID", "app_id")
    monkeypatch.setitem(os.environ, "NEXMO_PRIVATE_KEY_VOICE_APP", MOCK_PRIVATE_KEY)
    monkeypatch.setitem(os.environ, "HOTLINE_DESC", MOCK_HOTLINE_DESC)

    app = web.Application()
    app.router.add_routes(routes)
    return loop.run_until_complete(aiohttp_client(app))


@pytest.fixture
def webservice_cli_autorecord(loop, aiohttp_client, monkeypatch):
    monkeypatch.setitem(os.environ, "PHONE_NUMBERS", json.dumps(MOCK_PHONE_NUMBERS))
    monkeypatch.setitem(os.environ, "NEXMO_APP_ID", "app_id")
    monkeypatch.setitem(os.environ, "NEXMO_PRIVATE_KEY_VOICE_APP", MOCK_PRIVATE_KEY)
    monkeypatch.setitem(
        os.environ,
        "ZAPIER_CATCH_HOOK_RECORDING_URL",
        "https://hooks.zapier.com/1111/2222",
    )
    monkeypatch.setitem(os.environ, "HOTLINE_DESC", MOCK_HOTLINE_DESC)

    monkeypatch.setitem(os.environ, "AUTO_RECORD", "True")

    app = web.Application()
    app.router.add_routes(routes)
    return loop.run_until_complete(aiohttp_client(app))


async def test_answer_call(webservice_cli):
    with mock.patch("webservice.__main__.get_nexmo_client") as mock_nexmo_client:

        mock_nexmo_client.return_value = FakeNexmoClient()
        resp = await webservice_cli.get(
            "/webhook/answer/?conversation_uuid=CON-123-456&uuid=aaaa-bbbb&to=1800123456&from=Restricted"
        )
        assert resp.status == 200
        response = await resp.json()

        assert response[0]["action"] == "talk"
        assert response[0]["text"] == f"You've reached the {MOCK_HOTLINE_DESC}."

        assert response[1]["action"] == "conversation"
        assert response[1]["name"] == "CON-123-456"
        assert response[1]["eventMethod"] == "POST"
        assert response[1]["musicOnHoldUrl"][0] in MUSIC_WHILE_YOU_WAIT
        assert response[1]["endOnExit"] is False
        assert response[1]["startOnEnter"] is False

        assert not response[1].get("record")
        assert not response[1].get("eventUrl")


async def test_answer_conference_call(webservice_cli):
    with mock.patch("webservice.__main__.get_nexmo_client") as mock_nexmo_client:

        mock_nexmo_client.return_value = FakeNexmoClient()
        resp = await webservice_cli.get(
            "/webhook/answer_conference_call/CON-123-456/aaaa-bbbb/?conversation_uuid=CON-456-789&uuid=dddd-ffff&to=16040001234&from=1800123456"
        )
        assert resp.status == 200
        response = await resp.json()

        assert response[0]["action"] == "talk"
        assert (
            response[0]["text"]
            == f"Hello Mariatta, connecting you to {MOCK_HOTLINE_DESC}."
        )

        assert response[1]["action"] == "conversation"
        assert response[1]["name"] == "CON-123-456"
        assert response[1]["startOnEnter"] is True
        assert response[1]["endOnExit"] is True


async def test_answer_call_auto_record(webservice_cli_autorecord):
    with mock.patch("webservice.__main__.get_nexmo_client") as mock_nexmo_client:
        mock_nexmo_client.return_value = FakeNexmoClient()
        resp = await webservice_cli_autorecord.get(
            "/webhook/answer/?conversation_uuid=CON-123-456&uuid=aaaa-bbbb&to=1800123456&from=Restricted"
        )
        assert resp.status == 200
        response = await resp.json()

        assert response[0]["action"] == "talk"
        assert (
            response[0]["text"]
            == f"You've reached the {MOCK_HOTLINE_DESC}. This call is recorded."
        )

        assert response[1]["action"] == "conversation"
        assert response[1]["name"] == "CON-123-456"
        assert response[1]["eventMethod"] == "POST"
        assert response[1]["musicOnHoldUrl"][0] in MUSIC_WHILE_YOU_WAIT
        assert response[1]["endOnExit"] is False
        assert response[1]["startOnEnter"] is False

        assert response[1]["record"] is True
        assert response[1]["eventUrl"] == ["https://hooks.zapier.com/1111/2222"]


async def test_inbound_sms(webservice_cli):
    with mock.patch("webservice.__main__.get_nexmo_client") as mock_nexmo_client:
        nexmo_client = FakeNexmoClient()
        mock_nexmo_client.return_value = nexmo_client

        reporter_number = "1234"
        hotline_number = "5678"
        text = "onetwothree"

        resp = await webservice_cli.get(
            f"/webhook/inbound-sms/?msisdn={reporter_number}&to={hotline_number}&text={text}"
        )

        assert resp.status == 204

        # One for each person on staff, one to respond to the reporter.
        assert len(nexmo_client.messages_sent) == 3

        # Check that the organizers got the message.
        for n, phone_number_dict in enumerate(MOCK_PHONE_NUMBERS):
            message = nexmo_client.messages_sent[n]
            assert message["from"] == hotline_number
            assert message["to"] == phone_number_dict["phone"]
            assert text in message["text"]

        # Check the response message
        response_message = nexmo_client.messages_sent[-1]
        assert response_message["to"] == reporter_number
        assert response_message["from"] == hotline_number
        assert MOCK_HOTLINE_DESC in response_message["text"]
