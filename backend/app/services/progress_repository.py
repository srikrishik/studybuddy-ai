from app.services.mongodb import database


quiz_attempts_collection = database["quiz_attempts"]


def get_learning_progress() -> dict:
    """
    Build learning progress from saved quiz attempts.
    """

    attempts = list(
        quiz_attempts_collection.find(
            {},
            {"_id": 0},
        ).sort("created_at", -1)
    )

    if not attempts:
        return {
            "total_attempts": 0,
            "average_score": 0,
            "topics": [],
        }

    total_attempts = len(attempts)

    average_score = (
        sum(
            attempt.get("score_percentage", 0)
            for attempt in attempts
        )
        / total_attempts
    )

    topic_progress = {}

    for attempt in attempts:
        topic = attempt.get("topic", "Unknown")

        if topic not in topic_progress:
            topic_progress[topic] = {
                "topic": topic,
                "attempts": 0,
                "average_score": 0,
            }

        topic_progress[topic]["attempts"] += 1
        topic_progress[topic]["average_score"] += (
            attempt.get("score_percentage", 0)
        )

    for topic in topic_progress.values():
        topic["average_score"] = (
            topic["average_score"]
            / topic["attempts"]
        )

    return {
        "total_attempts": total_attempts,
        "average_score": average_score,
        "topics": list(topic_progress.values()),
    }