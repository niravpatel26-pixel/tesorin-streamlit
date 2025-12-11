# supabase_client.py
#
# This is still a placeholder for later.
# When you're ready, you'll:
# 1. `pip install supabase-py`
# 2. Set SUPABASE_URL and SUPABASE_KEY as environment variables
# 3. Replace the fake auth functions with real Supabase calls.

import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


def is_configured() -> bool:
    return bool(SUPABASE_URL and SUPABASE_KEY)


# ---------- PROFILE STORAGE PLACEHOLDER ----------

def save_profile(profile: dict) -> None:
    """
    Later: send data to Supabase.
    For now this does nothing – the app just keeps data in session_state.
    """
    return


def load_profile(user_id: str) -> dict | None:
    """
    Later: read profile from Supabase by user_id (or email).
    """
    return None


# ---------- AUTH PLACEHOLDER ----------

def sign_up(email: str, password: str, name: str | None = None):
    """
    Placeholder sign-up.
    Returns (ok, message or user).
    Replace with real Supabase sign-up later.
    """
    # In this demo we always succeed.
    user = {"email": email, "name": name}
    return True, None


def sign_in(email: str, password: str):
    """
    Placeholder sign-in.
    Returns (ok, user or message).
    """
    # In this demo we always succeed and return a fake user.
    user = {"email": email, "name": email.split("@")[0]}
    return True, user


def sign_out():
    """
    Placeholder sign-out.
    Real version would revoke tokens / clear session.
    """
    return True
