import upwork
from pprint import pprint
from upwork.routers import auth
import json
import configparser

"""Emulation of desktop app.
Your keys should be created with project type "Desktop".
Returns: ``upwork.Client`` instance ready to work.
"""


def get_desktop_client():
    print("Emulating desktop app")

    # Initialize the parser
    config = configparser.ConfigParser()

    # Read the configuration file
    config.read('config.ini')

    # Extract the consumer key and secret
    consumer_key = config['upwork']['consumer_key']
    consumer_secret = config['upwork']['consumer_secret']
    config = upwork.Config(
        {
            "client_id": consumer_key,
            "client_secret": consumer_secret,
            "redirect_uri": "http://192.168.0.14",
        }
    )

    client = upwork.Client(config)

    try:
        config.token
    except AttributeError:
        # remove client.get_authorization_url and authz_code input in case Client Credentials Grant is used
        authorization_url, state = client.get_authorization_url()
        # cover "state" flow if needed
        authz_code = input(
            "Please enter the full callback URL you get "
            "following this link:\n{0}\n\n> ".format(authorization_url)
        )

        print("Retrieving access and refresh tokens.... ")
        token = client.get_access_token(authz_code)
        # Save the access token for future use
        with open('access_token.json', 'w') as f:
            json.dump(token, f)
        pprint(token)
        print("OK")

    return client


if __name__ == "__main__":
    client = get_desktop_client()

    try:
        print("My info")
        pprint(auth.Api(client).get_user_info())
    except Exception as e:
        raise e
