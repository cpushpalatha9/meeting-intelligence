import os
import pickle
from googleapiclient.discovery import build

TOKEN_FILE = "token.json"

def main():
    print("Starting Google Meet API test...")

    if not os.path.exists(TOKEN_FILE):
        print("ERROR: token.json not found.")
        print("Run google_oauth_test.py first.")
        return

    with open(TOKEN_FILE, "rb") as token:
        credentials = pickle.load(token)

    meet = build(
        "meet",
        "v2",
        credentials=credentials
    )

    print("\nTesting Google Meet conference records...")

    response = meet.conferenceRecords().list(
        pageSize=10
    ).execute()

    conferences = response.get("conferenceRecords", [])

    print(f"\nConference records found: {len(conferences)}")

    if not conferences:
        print("\nNo accessible Google Meet conferences were found.")
        print("This does NOT mean the API failed.")
        print("It means this account currently has no accessible past conferences.")
    else:
        print("\nAccessible Google Meet conferences:")

        for conference in conferences:
            print("--------------------------------")
            print("Name:", conference.get("name"))
            print("Start:", conference.get("startTime"))
            print("End:", conference.get("endTime"))
            print("Space:", conference.get("space"))

    print("\n================================")
    print("GOOGLE MEET API TEST PASSED")
    print("================================")


if __name__ == "__main__":
    main()