"""Authentication pages for signup and login."""
import streamlit as st
from src.services import AuthService
from src.database.connection import SessionLocal
from src.utils.email_service import send_verification_email, generate_verification_token
import streamlit.components.v1 as components


def show_auth_page():
    """Show authentication page with login and signup tabs."""
    st.title("👶 Parents Healthline Assistant")

    # HIPAA Compliance Notice
    st.info("🔒 **HIPAA Compliant**: Your health information is protected. Email verification required for account security.")

    st.markdown("### Welcome! Please sign in or create an account")

    tab1, tab2, tab3, tab4 = st.tabs(["Login", "Sign Up", "Social Sign-In", "Continue as Guest"])

    with tab1:
        show_login_form()

    with tab2:
        show_signup_form()

    with tab3:
        show_social_signin()

    with tab4:
        show_guest_option()


def show_login_form():
    """Show login form."""
    st.markdown("#### Login to Your Account")

    with st.form("login_form"):
        email = st.text_input("Email", placeholder="your@email.com")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login", use_container_width=True)

        if submit:
            if not email or not password:
                st.error("Please enter both email and password")
                return

            db = SessionLocal()
            try:
                auth_service = AuthService()
                user = auth_service.authenticate_user(db, email, password)

                if user:
                    # Check if email is verified (HIPAA compliance)
                    if not user.email_verified:
                        st.warning("⚠️ **Email Not Verified**: For HIPAA compliance, please verify your email before accessing health information. Check your inbox for the verification link.")

                        # Option to resend verification
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            if st.button("Resend Verification Email", use_container_width=True):
                                verification_token = generate_verification_token()
                                user.verification_token = verification_token
                                db.commit()

                                if send_verification_email(user.email, verification_token, user.full_name):
                                    st.success("Verification email sent! Check your inbox.")
                                else:
                                    st.error("Failed to send email. Try again.")
                        return

                    # Create session for authenticated user
                    app_session, token = auth_service.create_session(
                        db, user_id=user.id, role=user.role
                    )

                    # Store in session state
                    st.session_state.user = user
                    st.session_state.app_session = app_session
                    st.session_state.access_token = token
                    st.session_state.is_authenticated = True
                    st.session_state.db_session = db

                    st.success(f"Welcome back, {user.full_name}! 👋")
                    st.rerun()
                else:
                    st.error("Invalid email or password")
            except Exception as e:
                st.error(f"Login error: {str(e)}")
            finally:
                if 'user' not in st.session_state:
                    db.close()


def show_signup_form():
    """Show signup form."""
    st.markdown("#### Create a New Account")

    with st.form("signup_form"):
        full_name = st.text_input("Full Name", placeholder="Your Name")
        email = st.text_input("Email", placeholder="your@email.com")
        password = st.text_input("Password", type="password", help="Minimum 6 characters")
        password_confirm = st.text_input("Confirm Password", type="password")

        st.markdown("**Why create an account?**")
        st.markdown("- Save conversation history")
        st.markdown("- Track your child's health over time")
        st.markdown("- Access previous recommendations")
        st.markdown("- HIPAA-compliant secure storage")

        submit = st.form_submit_button("Create Account", use_container_width=True)

        if submit:
            # Validation
            if not all([full_name, email, password, password_confirm]):
                st.error("Please fill in all fields")
                return

            if password != password_confirm:
                st.error("Passwords don't match")
                return

            if len(password) < 6:
                st.error("Password must be at least 6 characters")
                return

            db = SessionLocal()
            try:
                auth_service = AuthService()

                # Check if email exists
                existing_user = auth_service.get_user_by_email(db, email)
                if existing_user:
                    st.error("An account with this email already exists. Please login.")
                    return

                # Generate verification token
                verification_token = generate_verification_token()

                # Create user
                user = auth_service.create_user(
                    db=db,
                    email=email,
                    password=password,
                    full_name=full_name,
                    role="parent",
                    verification_token=verification_token
                )

                # Send verification email
                email_sent = send_verification_email(email, verification_token, full_name)

                if email_sent:
                    st.success(f"""
                    ✅ **Account Created Successfully!**

                    For HIPAA compliance, we've sent a verification email to **{email}**.

                    **Next Steps:**
                    1. Check your email inbox (and spam folder)
                    2. Click the verification link
                    3. Return here to login

                    *For demo purposes, the verification link is shown in the terminal/console.*
                    """)
                    st.info("💡 Switch to the **Login** tab to sign in after verifying your email.")
                else:
                    st.warning(f"Account created, but verification email failed to send. Please contact support.")

            except Exception as e:
                st.error(f"Signup error: {str(e)}")
            finally:
                db.close()


def show_social_signin():
    """Show social sign-in options (Google, Apple)."""
    st.markdown("#### Sign in with Social Account")

    st.markdown("**Quick & Secure Sign-In**")
    st.markdown("- No password needed")
    st.markdown("- Email automatically verified")
    st.markdown("- HIPAA compliant")

    st.markdown("---")

    # Google Sign-In Button
    st.markdown("### 🔴 Google Sign-In")

    if st.button("🔴 Continue with Google", use_container_width=True, disabled=True, key="google_signin"):
        st.info("Google Sign-In coming soon! Setting up integration...")

    with st.expander("📖 How to set up Google Sign-In"):
        st.markdown("""
        **Step 1: Create OAuth 2.0 Credentials**
        1. Go to [Google Cloud Console](https://console.cloud.google.com/)
        2. Create a new project or select existing one
        3. Navigate to "APIs & Services" > "Credentials"
        4. Click "Create Credentials" > "OAuth 2.0 Client ID"
        5. Configure OAuth consent screen
        6. Add authorized redirect URI: `http://localhost:8501/callback/google`
        7. Copy your **Client ID** and **Client Secret**

        **Step 2: Add to .env file**
        ```
        GOOGLE_CLIENT_ID=your_client_id_here
        GOOGLE_CLIENT_SECRET=your_client_secret_here
        ```

        **Step 3: Enable Google Sign-In**
        Update this code to enable the button and implement OAuth flow.

        **Documentation:** [Google OAuth 2.0](https://developers.google.com/identity/protocols/oauth2)
        """)

    st.markdown("---")

    # Apple Sign-In Button
    st.markdown("### Apple Sign-In")

    if st.button(" Continue with Apple", use_container_width=True, disabled=True, key="apple_signin"):
        st.info("Apple Sign-In coming soon! Setting up integration...")

    with st.expander("📖 How to set up Apple Sign-In"):
        st.markdown("""
        **Step 1: Enroll in Apple Developer Program**
        1. Sign up at [Apple Developer](https://developer.apple.com/programs/) ($99/year)
        2. Go to [Certificates, Identifiers & Profiles](https://developer.apple.com/account/resources/)
        3. Create a new App ID
        4. Enable "Sign in with Apple" capability

        **Step 2: Create Service ID**
        1. Register a Services ID
        2. Configure "Sign in with Apple"
        3. Add return URLs: `http://localhost:8501/callback/apple`
        4. Download and save your **Service ID** and **Team ID**

        **Step 3: Generate Private Key**
        1. Create a new Key with "Sign in with Apple" enabled
        2. Download the `.p8` private key file
        3. Save the Key ID

        **Step 4: Add to .env file**
        ```
        APPLE_CLIENT_ID=your_service_id
        APPLE_TEAM_ID=your_team_id
        APPLE_KEY_ID=your_key_id
        APPLE_PRIVATE_KEY_PATH=/path/to/key.p8
        ```

        **Documentation:** [Sign in with Apple](https://developer.apple.com/sign-in-with-apple/)
        """)

    st.markdown("---")

    st.success("**Benefits of Social Sign-In:**")
    st.markdown("""
    - ✅ **Security**: Email addresses automatically verified (HIPAA requirement)
    - ✅ **Trust**: Users trust Google/Apple authentication
    - ✅ **Convenience**: No password to remember
    - ✅ **Compliance**: Industry-standard OAuth 2.0 protocol

    *Social sign-in is recommended for healthcare applications to ensure verified user identities.*
    """)


def show_guest_option():
    """Show option to continue as guest."""
    st.markdown("#### Continue Without an Account")

    st.warning("""
    **⚠️ Guest Mode Limitations (HIPAA Compliance):**
    - ❌ Conversations are NOT saved
    - ❌ No access to conversation history
    - ❌ Limited to current session only
    - ❌ No HIPAA protections

    **For full HIPAA-compliant service, please create a verified account.**
    """)

    st.info("""
    **Guest Mode:**
    - Quick access to health guidance
    - No account needed
    - No personally identifiable information stored
    """)

    if st.button("Continue as Guest (Not HIPAA Protected)", use_container_width=True):
        db = SessionLocal()
        try:
            auth_service = AuthService()

            # Create anonymous session
            app_session, token = auth_service.create_session(
                db, user_id=None, role="parent"
            )

            # Store in session state
            st.session_state.user = None
            st.session_state.app_session = app_session
            st.session_state.access_token = token
            st.session_state.is_authenticated = False
            st.session_state.db_session = db

            st.success("Starting guest session...")
            st.rerun()

        except Exception as e:
            st.error(f"Error starting guest session: {str(e)}")
