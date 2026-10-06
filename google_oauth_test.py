from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os
import pickle

SCOPES = [
    "https://www.googleapis.com/auth/meetings.space.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]

CLIENT_SECRET_FILE = "client_secret.json"
TOKEN_FILE = "token.json"


def main():
    print("Starting Google OAuth...")

    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        SCOPES
    )

    credentials = flow.run_local_server(
        port=0,
        access_type="offline",
        prompt="consent"
    )

    # Save token locally
    with open(TOKEN_FILE, "wb") as token:
        pickle.dump(credentials, token)

    print("\n================================")
    print("GOOGLE OAUTH SUCCESS")
    print("================================")
    print("Token saved as token.json")

    # Test Google Drive API
    print("\nTesting Google Drive API...")

    drive = build(
        "drive",
        "v3",
        credentials=credentials
    )

    results = drive.files().list(
        pageSize=5,
        fields="files(id,name,mimeType)"
    ).execute()

    files = results.get("files", [])

    print(f"Drive API accessible.")
    print(f"Files returned: {len(files)}")

    for file in files:
        print(
            f"- {file['name']} "
            f"({file['mimeType']})"
        )

    print("\nGOOGLE INTEGRATION TEST PASSED")


if __name__ == "__main__":
    main()