import os

import supabase
from dotenv import load_dotenv

load_dotenv()


def get_supabase_client() -> supabase.Client:
    """
    Initialize and return a Supabase client.

    Returns:
        Client: A Supabase client instance.
    """
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        raise ValueError("Supabase URL and Key must be set in environment variables.")

    return supabase.create_client(url, key)


def get_user_from_session() -> dict | None:
    """
    Get the user from the session.

    Returns:
        dict: User information if available, otherwise None.
    """
    supabase_client = get_supabase_client()

    try:
        # Get the current session using the current API
        user = supabase_client.auth.get_user()

        if user and user.user:
            return user.user
    except Exception as e:
        print(f"Error getting user from session: {e}")

    return None
