import os
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

ACCOUNT_ID = os.getenv("ZOOM_ACCOUNT_ID")
CLIENT_ID = os.getenv("ZOOM_CLIENT_ID")
CLIENT_SECRET = os.getenv("ZOOM_CLIENT_SECRET")


def get_access_token():

    credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"

    encoded_credentials = base64.b64encode(
        credentials.encode()
    ).decode()

    response = requests.post(
        "https://zoom.us/oauth/token",
        params={
            "grant_type": "account_credentials",
            "account_id": ACCOUNT_ID,
        },
        headers={
            "Authorization": f"Basic {encoded_credentials}"
        },
        timeout=30,
    )

    print("Token response status:", response.status_code)

    if response.status_code != 200:
        print(response.text)
        return None

    data = response.json()

    print("\nOAuth token information:")
    print("Token type:", data.get("token_type"))
    print("Expires in:", data.get("expires_in"))

    print("\nScopes returned by Zoom:")
    print(data.get("scope", "NO SCOPE"))

    return data.get("access_token")


def main():

    print("========================================")
    print("ZOOM SERVER-TO-SERVER OAUTH TEST")
    print("========================================\n")

    token = get_access_token()

    if not token:
        print("\nZOOM OAUTH FAILED")
        return

    print("\nZOOM OAUTH SUCCESS")
    print("Access token received.")

    # ----------------------------------------
    # Test normal user recordings endpoint
    # ----------------------------------------

    print("\n========================================")
    print("TESTING USER RECORDINGS API")
    print("========================================")

    url = "https://api.zoom.us/v2/users/me/recordings"

    response = requests.get(
        url,
        headers={
            "Authorization": f"Bearer {token}"
        },
        params={
            "page_size": 10
        },
        timeout=30,
    )

    print("\nRecording API status:", response.status_code)

    # ----------------------------------------
    # SUCCESS
    # ----------------------------------------

    if response.status_code == 200:

        data = response.json()

        meetings = data.get("meetings", [])

        print("\n========================================")
        print("ZOOM RECORDING API SUCCESS")
        print("========================================")

        print(
            "Total recordings:",
            data.get("total_records", len(meetings))
        )

        if not meetings:

            print("\nNo Zoom cloud recordings found.")

            print(
                "The Zoom API integration is working correctly."
            )

        else:

            print("\nAccessible Zoom recordings:")

            for meeting in meetings:

                print("\n--------------------------------")
                print("Topic:", meeting.get("topic"))
                print("Start time:", meeting.get("start_time"))
                print("UUID:", meeting.get("uuid"))
                print("Duration:", meeting.get("duration"))

                recording_files = meeting.get(
                    "recording_files",
                    []
                )

                print(
                    "Recording files:",
                    len(recording_files)
                )

                for recording in recording_files:

                    print(
                        "  File type:",
                        recording.get("file_type")
                    )

                    print(
                        "  Recording type:",
                        recording.get("recording_type")
                    )

                    print(
                        "  Status:",
                        recording.get("status")
                    )

        print("\n========================================")
        print("ZOOM INTEGRATION TEST PASSED")
        print("========================================")

        return

    # ----------------------------------------
    # FAILURE
    # ----------------------------------------

    print("\n========================================")
    print("ZOOM RECORDING API FAILED")
    print("========================================")

    print(response.text)

    print("\nHTTP Status:", response.status_code)


if __name__ == "__main__":
    main()