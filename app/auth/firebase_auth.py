# app/auth/firebase_auth.py
import json
import requests
import streamlit as st


# ==============================================================================
# Firebase Auth API (REST)
# ==============================================================================

def sign_in_with_email_and_password(email: str, password: str) -> dict:
    """Sign in with email and password. Returns user data including idToken."""
    request_ref = (
        "https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword"
        f"?key={st.secrets['FIREBASE_WEB_API_KEY']}"
    )
    headers = {"content-type": "application/json; charset=UTF-8"}
    data = json.dumps({
        "email": email,
        "password": password,
        "returnSecureToken": True
    })
    request_object = requests.post(request_ref, headers=headers, data=data, timeout=20)
    _raise_detailed_error(request_object)
    return request_object.json()


def get_account_info(id_token: str) -> dict:
    """Get account information using ID token."""
    request_ref = (
        "https://www.googleapis.com/identitytoolkit/v3/relyingparty/getAccountInfo"
        f"?key={st.secrets['FIREBASE_WEB_API_KEY']}"
    )
    headers = {"content-type": "application/json; charset=UTF-8"}
    data = json.dumps({"idToken": id_token})
    request_object = requests.post(request_ref, headers=headers, data=data, timeout=20)
    _raise_detailed_error(request_object)
    return request_object.json()


def send_email_verification(id_token: str) -> dict:
    """Send email verification to the user."""
    request_ref = (
        "https://www.googleapis.com/identitytoolkit/v3/relyingparty/getOobConfirmationCode"
        f"?key={st.secrets['FIREBASE_WEB_API_KEY']}"
    )
    headers = {"content-type": "application/json; charset=UTF-8"}
    data = json.dumps({
        "requestType": "VERIFY_EMAIL",
        "idToken": id_token
    })
    request_object = requests.post(request_ref, headers=headers, data=data, timeout=20)
    _raise_detailed_error(request_object)
    return request_object.json()


def send_password_reset_email(email: str) -> dict:
    """Send password reset email to the user."""
    request_ref = (
        "https://www.googleapis.com/identitytoolkit/v3/relyingparty/getOobConfirmationCode"
        f"?key={st.secrets['FIREBASE_WEB_API_KEY']}"
    )
    headers = {"content-type": "application/json; charset=UTF-8"}
    data = json.dumps({"requestType": "PASSWORD_RESET", "email": email})
    request_object = requests.post(request_ref, headers=headers, data=data, timeout=20)
    _raise_detailed_error(request_object)
    return request_object.json()


def create_user_with_email_and_password(email: str, password: str) -> dict:
    """Create a new user with email and password. Returns user data including idToken."""
    request_ref = (
        "https://www.googleapis.com/identitytoolkit/v3/relyingparty/signupNewUser"
        f"?key={st.secrets['FIREBASE_WEB_API_KEY']}"
    )
    headers = {"content-type": "application/json; charset=UTF-8"}
    data = json.dumps({
        "email": email,
        "password": password,
        "returnSecureToken": True
    })
    request_object = requests.post(request_ref, headers=headers, data=data, timeout=20)
    _raise_detailed_error(request_object)
    return request_object.json()


def delete_user_account(id_token: str) -> dict:
    """Delete the user account."""
    request_ref = (
        "https://www.googleapis.com/identitytoolkit/v3/relyingparty/deleteAccount"
        f"?key={st.secrets['FIREBASE_WEB_API_KEY']}"
    )
    headers = {"content-type": "application/json; charset=UTF-8"}
    data = json.dumps({"idToken": id_token})
    request_object = requests.post(request_ref, headers=headers, data=data, timeout=20)
    _raise_detailed_error(request_object)
    return request_object.json()


def _raise_detailed_error(request_object: requests.Response) -> None:
    """Raise HTTPError with detailed message from Firebase."""
    try:
        request_object.raise_for_status()
    except requests.exceptions.HTTPError as error:
        raise requests.exceptions.HTTPError(error, request_object.text)


# ==============================================================================
# Authentication helper functions (Streamlit-aware)
# ==============================================================================

def sign_in(email: str, password: str) -> None:
    """Sign in user and update session state."""
    try:
        id_token = sign_in_with_email_and_password(email, password)["idToken"]
        user_info = get_account_info(id_token)["users"][0]
        
        if not user_info.get("emailVerified", False):
            send_email_verification(id_token)
            st.session_state.auth_warning = "Check your email to verify your account"
        else:
            st.session_state.user_info = user_info
            st.session_state.id_token = id_token
            st.rerun()
            
    except requests.exceptions.HTTPError as error:
        error_message = json.loads(error.args[1])["error"]["message"]
        if error_message in {"INVALID_EMAIL", "EMAIL_NOT_FOUND", "INVALID_PASSWORD", "MISSING_PASSWORD"}:
            st.session_state.auth_warning = "Error: Use a valid email and password"
        else:
            st.session_state.auth_warning = "Error: Please try again later"
    except Exception:
        st.session_state.auth_warning = "Error: Please try again later"


def create_account(email: str, password: str) -> None:
    """Create a new user account."""
    try:
        id_token = create_user_with_email_and_password(email, password)["idToken"]
        send_email_verification(id_token)
        st.session_state.auth_success = "Check your inbox to verify your email"
        
    except requests.exceptions.HTTPError as error:
        error_message = json.loads(error.args[1])["error"]["message"]
        if error_message == "EMAIL_EXISTS":
            st.session_state.auth_warning = "Error: Email belongs to existing account"
        elif error_message in {"INVALID_EMAIL", "INVALID_PASSWORD", "MISSING_PASSWORD", "MISSING_EMAIL", "WEAK_PASSWORD"}:
            st.session_state.auth_warning = "Error: Use a valid email and password"
        else:
            st.session_state.auth_warning = "Error: Please try again later"
    except Exception:
        st.session_state.auth_warning = "Error: Please try again later"


def reset_password(email: str) -> None:
    """Send password reset email."""
    try:
        send_password_reset_email(email)
        st.session_state.auth_success = "Password reset link sent to your email"
        
    except requests.exceptions.HTTPError as error:
        error_message = json.loads(error.args[1])["error"]["message"]
        if error_message in {"MISSING_EMAIL", "INVALID_EMAIL", "EMAIL_NOT_FOUND"}:
            st.session_state.auth_warning = "Error: Use a valid email"
        else:
            st.session_state.auth_warning = "Error: Please try again later"
    except Exception:
        st.session_state.auth_warning = "Error: Please try again later"


def sign_out() -> None:
    """Sign out the current user."""
    keys_to_delete = ["user_info", "id_token", "auth_warning", "auth_success"]
    for key in keys_to_delete:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state.auth_success = "You have successfully signed out"


def delete_account(password: str) -> None:
    """Delete the current user's account (requires password confirmation)."""
    try:
        current_email = st.session_state.user_info["email"]
        id_token = sign_in_with_email_and_password(current_email, password)["idToken"]
        delete_user_account(id_token)
        
        # Clear all session state
        keys_to_delete = ["user_info", "id_token", "auth_warning", "auth_success"]
        for key in keys_to_delete:
            if key in st.session_state:
                del st.session_state[key]
        st.session_state.auth_success = "You have successfully deleted your account"
        
    except requests.exceptions.HTTPError as error:
        error_message = json.loads(error.args[1])["error"]["message"]
        st.session_state.auth_warning = f"Error: {error_message}"
    except Exception:
        st.session_state.auth_warning = "Error: Please try again later"


def is_authenticated() -> bool:
    """Check if user is authenticated."""
    return "user_info" in st.session_state and st.session_state.user_info is not None
