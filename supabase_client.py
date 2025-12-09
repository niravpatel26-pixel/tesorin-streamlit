# supabase_client.py
#
# This is a placeholder for later.
# When you're ready, you'll:
# 1. `pip install supabase-py`
# 2. Set SUPABASE_URL and SUPABASE_KEY as environment variables
# 3. Use this client inside the app to store/load user data.

import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


def is_configured() -> bool:
    return bool(SUPABASE_URL and SUPABASE_KEY)


# Example placeholder functions
def save_profile(profile: dict) -> None:
    """
    Later: send data to Supabase.
    For now: just a placeholder so you can call it from the app without crashing.
    """
    # TODO: implement real Supabase integration
    return


def load_profile(user_id: str) -> dict | None:
    """
    Later: read profile from Supabase by user_id.
    """
    # TODO: implement real Supabase integration
    return None
