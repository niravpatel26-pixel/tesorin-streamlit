# supabase_client.py
#
# This is still a placeholder for later.
# When you're ready, you'll:
# 1. `pip install supabase-py`
# 2. Set SUPABASE_URL and SUPABASE_KEY as environment variables
# 3. Replace the fake auth functions with real Supabase calls.

import os
from typing import Optional, Dict, Tuple

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


def is_configured() -> bool:
    """Return True if Supabase env variables are set."""
    return bool(SUPABASE_URL and SUPABASE_KEY)


# ---------- PROFILE STORAGE PLACEHOLDER ----------

def save_profile(profile: Dict) -> None:
    """
    Later: send data to Supabase.
    For now this does nothing – the app just keeps data in session_state.
    """
    return


def load_profile(user_id: str) -> Optional[Dict]:
    """
    Later: read profile from Supabase by user_id (or email).
    For now we always return None.
    """
    return None


# ---------- AUTH PLACEHOLDER ----------

def sign_up(email: str, password: str, name: Optional[str] = None) -> Tuple[bool, Optional[str]]:
    """
    Placeholder sign-up.
    Returns (ok, error_message). On success error_message is None.
    Replace with real Supabase sign-up later.
    """
    # Demo: always succeed
    return True, None


def sign_in(email: str, password: str):
    """
    Placeholder sign-in.
    Returns (ok, user_or_error_message).
    """
    # Demo: always succeed and return a fake user object
    user = {"email": email, "name": email.split("@")[0]}
    return True, user


def sign_out() -> bool:
    """
    Placeholder sign-out.
    Real version would revoke tokens / clear session.
    """
    return True
