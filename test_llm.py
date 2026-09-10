import os

from dotenv import load_dotenv

from services.llm_service import LLMService


load_dotenv()


api_key = os.getenv(
    "GEMINI_API_KEY"
)

model = os.getenv(
    "GEMINI_MODEL"
)


print(
    "API key configured:",
    bool(api_key)
)

print(
    "Model:",
    model
)


transcript = """
Manager: Today we discussed the mobile
application launch.

Ravi: I will complete the API integration
by Friday.

Priya: I will prepare the UI testing report.

Manager: We have decided to continue with
the planned mobile application launch.

Ravi: I will make sure the API integration
is ready for testing.
"""


try:

    llm_service = LLMService(
        api_key=api_key,
        model=model
    )

    result = llm_service.process(
        transcript
    )

    print("\n========== SUMMARY ==========")

    print(
        result.summary
    )

    print("\n========== KEY POINTS ==========")

    for point in result.key_points:

        print(
            "-",
            point
        )

    print("\n========== DECISIONS ==========")

    for decision in result.decisions:

        print(
            "-",
            decision
        )

    print("\n========== ACTION ITEMS ==========")

    for item in result.action_items:

        print(
            "Task:",
            item.task
        )

        print(
            "Assignee:",
            item.assignee
        )

        print(
            "Deadline:",
            item.deadline
        )

        print(
            "Priority:",
            item.priority
        )

        print(
            "Status:",
            item.status
        )

        print()

    print("\n========== PARTICIPANTS ==========")

    for participant in result.participants:

        print(
            "Name:",
            participant.name
        )

        print(
            "Responsibilities:",
            participant.responsibilities
        )

        print()

    print(
        "\n✅ LLM PROCESSING SUCCESSFUL"
    )


except Exception as error:

    print(
        "\n❌ LLM PROCESSING FAILED"
    )

    print(
        error
    )