import os

from dotenv import load_dotenv
from pymongo import MongoClient


# Load environment variables from .env
load_dotenv()


MONGODB_URI = os.getenv("MONGODB_URI")

if not MONGODB_URI:
    raise RuntimeError(
        "MONGODB_URI is not set in the environment."
    )


# Create the MongoDB client.
client = MongoClient(
    MONGODB_URI,
    serverSelectionTimeoutMS=10000,
)


# StudyBuddy database.
database = client["studybuddy"]


def test_mongodb_connection():
    """
    Test whether the MongoDB connection is working.
    """

    client.admin.command("ping")

    return True