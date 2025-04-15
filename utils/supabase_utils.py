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


def get_user_from_session(supabase_client: supabase.Client) -> dict | None:
    """
    Get the user from the session using the provided Supabase client instance.

    Args:
        supabase_client: The active Supabase client instance.

    Returns:
        dict: User information if available, otherwise None.
    """
    # supabase_client = get_supabase_client() # No longer create a new client here

    try:
        # Get the current session using the current API from the passed client
        user_response = supabase_client.auth.get_user()

        # Check the structure of the response, it might be user_response.user
        if user_response and hasattr(user_response, "user") and user_response.user:
            return user_response.user
        # Add a check if the response itself is the user object (API might vary)
        elif user_response and not hasattr(user_response, "user"):
            # This case might occur depending on the exact client version/state
            # You might need to inspect user_response structure if the above fails
            print("Direct user object received from get_user():", user_response)
            # Assuming user_response directly contains user data
            # Adjust this based on actual object structure if needed
            if hasattr(user_response, "id"):  # Basic check for user-like object
                return user_response

    except Exception as e:
        # More specific error catching could be useful here if needed
        print(f"Error getting user from session: {e}")

    return None
