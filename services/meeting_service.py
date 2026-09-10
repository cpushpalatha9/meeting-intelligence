def clean_participants(participants):

    unique_participants = {}

    for participant in participants:

        name = participant.name.strip()

        if not name:
            continue

        if name.lower() == "unknown":
            name = "Unknown"

        if name not in unique_participants:

            unique_participants[name] = {
                "name": name,
                "responsibilities": []
            }

        for responsibility in (
            participant.responsibilities
        ):

            responsibility = (
                responsibility.strip()
            )

            if (
                responsibility
                and responsibility
                not in unique_participants[name][
                    "responsibilities"
                ]
            ):

                unique_participants[name][
                    "responsibilities"
                ].append(
                    responsibility
                )

    return list(
        unique_participants.values()
    )


def clean_action_items(action_items):

    cleaned_items = []

    seen = set()

    for item in action_items:

        task = item.task.strip()

        if not task:
            continue

        assignee = item.assignee

        if assignee:
            assignee = assignee.strip()

        deadline = item.deadline

        if deadline:
            deadline = deadline.strip()

        priority = item.priority

        if priority:
            priority = priority.strip()

        status = item.status.strip()

        key = (
            task.lower(),
            (assignee or "").lower()
        )

        if key in seen:
            continue

        seen.add(key)

        cleaned_items.append(
            {
                "task": task,
                "assignee": assignee,
                "deadline": deadline,
                "priority": priority,
                "status": status
            }
        )

    return cleaned_items