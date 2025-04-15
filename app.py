from functools import wraps

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for

from utils.local_db_utils import get_table_names, get_topics
from utils.supabase_utils import get_supabase_client, get_user_from_session

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = "your-secret-key"  # Replace with a secure secret key


# Initialize Supabase client
supabase = get_supabase_client()


# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Pass the main supabase client instance
        user = get_user_from_session(supabase)
        if user is None:
            flash("Please sign in to access this page.", "warning")
            return redirect(url_for("signin"))
        # Pass the user object to the decorated function if needed
        # Or store it in flask.g for access within the request context
        # For now, just proceed if user exists
        return f(*args, **kwargs)

    return decorated_function


@app.route("/")
@login_required
def index():
    """
    Home route that returns a welcome message and lists all topics.
    """
    # Pass the main supabase client instance
    user = get_user_from_session(supabase)
    # It's generally better practice to get the user once,
    # potentially in the decorator and store in flask.g,
    # but passing the client here works for now.
    topics = get_topics()
    if not topics:
        flash("No topics available.", "warning")

    return render_template("index.html", user=user, topics=topics)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """
    Route for user signup.
    """
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            return redirect(url_for("signup"))

        # Call Supabase signup function
        try:
            response = supabase.auth.sign_up(email=email, password=password)

            print("Signup response user:", response.user)
            print("Signup response session:", response.session)

            if response.user:
                flash("Signup successful!", "success")
        except Exception as e:
            print("Error during signup:", e)
            return redirect(url_for("signup"))

        return redirect(url_for("index"))

    return render_template("signup.html")


@app.route("/signin", methods=["GET", "POST"])
def signin():
    """
    Route for user sign-in.
    """
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            return redirect(url_for("signin"))
        try:
            response = supabase.auth.sign_in_with_password(
                {"email": email, "password": password}
            )

            print("Signin response user:", response.user)
            print("Signin response session:", response.session)

            if response.user:
                flash("Signin successful!", "success")
        except Exception as e:
            print("Error during signin:", e)
            return redirect(url_for("signin"))

        return redirect(url_for("index"))

    return render_template("signin.html")


@app.route("/logout")
def logout():
    """
    Route for user logout.
    """
    try:
        supabase.auth.sign_out()
        flash("You have been logged out successfully.", "success")
    except Exception as e:
        print("Error during logout:", e)

    return redirect(url_for("signin"))


@app.route("/signin/google")
def signin_google():
    """
    Route to initiate Google OAuth sign-in.
    """
    try:
        # Construct an absolute URL for the callback
        redirect_url = url_for("auth_callback_google", _external=True)
        sign_in_url = supabase.auth.sign_in_with_oauth(
            {"provider": "google", "options": {"redirect_to": redirect_url}}
        )

        # Redirect the user to the Google sign-in page
        return redirect(sign_in_url.url)
    except Exception as e:
        print("Error during Google sign-in:", e)
        flash("Failed to initiate Google sign-in.", "danger")
        return redirect(url_for("signin"))


@app.route("/auth/callback/google")
def auth_callback_google():
    """
    Callback route for Google OAuth sign-in.
    """
    try:
        code = request.args.get("code")
        if not code:
            flash(
                "Authentication failed: No code received. Please try again.", "danger"
            )
            return redirect(url_for("signin"))

        # Exchange the authorization code for a session
        session_response = supabase.auth.exchange_code_for_session({"auth_code": code})

        # Check if the session exchange was successful
        if session_response and session_response.user:
            flash("Sign-in successful!", "success")
            # Session is set by Supabase client, redirect to the main page
            return redirect(url_for("index"))
        else:
            print(
                "Error during Google auth callback - code exchange failed:",
                session_response,
            )
            flash(
                "Authentication failed during code exchange. Please try again.",
                "danger",
            )
            return redirect(url_for("signin"))

    except Exception as e:
        # Catch potential exceptions during the code exchange
        print("Error during Google auth callback:", e)
        flash(f"Authentication failed: {e}. Please try again.", "danger")
        return redirect(url_for("signin"))


if __name__ == "__main__":
    print("Registered routes:")
    print(app.url_map)
    print("-" * 30)  # Separator for clarity
    print(get_table_names())
    app.run(debug=True, host="0.0.0.0", port=5000)
