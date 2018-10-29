import os
import sys

import click
import nexmo

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


def get_nexmo_client():
    """Return an instance of Nexmo client library"""
    app_id = os.environ.get("NEXMO_APP_ID")
    private_key = os.environ.get("NEXMO_PRIVATE_KEY_VOICE_APP")

    if not app_id:
        click.echo("Missing NEXMO_APP_ID environment variable.")
        sys.exit(-1)
    if not private_key:
        click.echo("Missing NEXMO_PRIVATE_KEY_VOICE_APP environment variable.")
        sys.exit(-1)

    client = nexmo.Client(application_id=app_id, private_key=private_key)
    return client


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument("urls", nargs=-1)
def download_recording(urls):
    """Download the recordings off Nexmo

    From the enhanced-coc-hotline, type in command line:

       $ python3 -m download_recording url1 url2 url3 ...

    """

    client = get_nexmo_client()
    for url in urls:
        recording = client.get_recording(url)
        uuid = url.split("/")[-1]

        recordingfile = f"./recordings/{uuid}.mp3"
        os.makedirs(os.path.dirname(recordingfile), exist_ok=True)
        with open(recordingfile, "wb") as f:
            f.write(recording)


if __name__ == "__main__":
    download_recording()
