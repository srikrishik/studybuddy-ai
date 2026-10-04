from app.services.ai_engine import get_ai_response


def generate_study_notes(topic):
    """Generate simple, structured study notes."""

    prompt = f"""
    Create clear study notes for the topic: {topic}

    Include:
    1. Simple explanation
    2. Important concepts
    3. Examples
    4. Key points to remember
    5. Three revision questions

    Use beginner-friendly language and clear headings.
    """

    return get_ai_response(prompt)


def generate_quiz(topic):
    """Generate a short quiz on a topic."""

    prompt = f"""
    Create a quiz about: {topic}

    Include five multiple-choice questions.
    Give four options per question.
    Provide the correct answers and brief explanations
    at the end.
    """

    return get_ai_response(prompt)


def generate_flashcards(topic):
    """Generate revision flashcards."""

    prompt = f"""
    Create five study flashcards about: {topic}.

    Format each card as:
    Question: ...
    Answer: ...

    Keep the answers concise and easy to remember.
    """

    return get_ai_response(prompt)