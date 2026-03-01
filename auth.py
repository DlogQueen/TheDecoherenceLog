import streamlit as st
import secrets
import database
import os

# Get Admin Password from Hugging Face Secrets (or default to a strong fallback)
ADMIN_PASS = os.environ.get("ADMIN_PASSWORD", "SuperSecureAdminPass_9921!")

ADMINS = {
    "admin": ADMIN_PASS
}

def register_new_user(username, password, email):
    return database.create_user(username, password, email)

def verify_login(username, password):
    if username in ADMINS and ADMINS[username] == password:
        return {"id": 0, "username": username, "role": "admin"}
    return database.verify_user_credentials(username, password)

def login_user(user_data, remember_me=False):
    st.session_state['authenticated'] = True
    st.session_state['username'] = user_data['username']
    st.session_state['user_id'] = user_data['id']
    st.session_state['role'] = user_data.get('role', 'user')

def check_auth():
    return st.session_state.get('authenticated', False)

def logout_user():
    st.session_state["authenticated"] = False
    st.session_state["username"] = None
    st.session_state["user_id"] = None
    st.rerun()

def get_current_user():
    if check_auth():
        return {
            "id": st.session_state.get("user_id"),
            "username": st.session_state.get("username"),
            "role": st.session_state.get("role")
        }
    return None

def is_admin():
    u = get_current_user()
    return u and u['role'] == 'admin'