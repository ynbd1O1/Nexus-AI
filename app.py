import streamlit as st
import streamlit_authenticator as stauth
from ddgs import DDGS

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="Nexus AI", page_icon="⚡")

# --- 2. INITIALIZE SESSION STATE ---
# We store credentials in session state so new registrations persist during the current session
if 'credentials' not in st.session_state:
    st.session_state['credentials'] = {
        "usernames": {
            "youness_admin": {
                "name": "Youness",
                "password": "nexus2026",
                "email": "youness@example.com"
            }
        }
    }

# --- 3. SECURITY LAYER ---
# Modern way to hash the dictionary
stauth.Hasher.hash_passwords(st.session_state['credentials'])

def main():
    # --- 4. INITIALIZE AUTHENTICATOR ---
    authenticator = stauth.Authenticate(
        st.session_state['credentials'],
        "nexus_secure_cookie_v4", # Changed version name to force a fresh cookie
        "nexus_signature_key",
        cookie_expiry_days=30
    )

    # --- 5. AUTHENTICATION UI ---
    if not st.session_state.get("authentication_status"):
        tab1, tab2 = st.tabs(["Login", "Register"])

        with tab2:
            try:
                # pre_authorized=None allows ANYONE to register without a whitelist
                result = authenticator.register_user(location='main', pre_authorized=None, key='reg_form')
                if result:
                    # 'result' is only truthy if the form was actually submitted successfully
                    st.success('Registration successful! Please switch to the Login tab.')
            except Exception as e:
                st.error(f"Registration Error: {e}")

        with tab1:
            try:
                authenticator.login(location='main')
            except Exception as e:
                # This catches that 'User not authorized' bug specifically
                st.info("Nexus is ready for login.")

    # --- 6. AUTHORIZED APP AREA ---
    if st.session_state.get("authentication_status"):
        st.sidebar.title(f"Welcome, {st.session_state['name']}")
        authenticator.logout('Logout', 'sidebar')

        st.title("⚡ NEXUS AI")
        st.markdown("---")

        query = st.text_input("Enter your command:", key="nexus_search")
        if query:
            with st.spinner("Nexus is scanning..."):
                with DDGS() as ddgs:
                    results = [r for r in ddgs.text(query, max_results=3)]
                    for res in results:
                        st.subheader(res['title'])
                        st.write(res['body'])
                        st.caption(f"Source: {res['href']}")
                        st.divider()

    elif st.session_state.get("authentication_status") is False:
        st.error('Username/password is incorrect')

if __name__ == "__main__":
    main()