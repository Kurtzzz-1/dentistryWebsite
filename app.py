from functools import wraps

from dotenv import load_dotenv
from flask import Flask, flash, g, redirect, render_template, request, url_for

from utils.local_db_utils import (
    get_num_questions_topic,
    get_questions_for_topic,
    get_table_names,
    get_topics,
)
from utils.question_class import QuestionType
from utils.supabase_utils import (
    get_supabase_client,
    get_user_from_session,
    is_valid_credentails_for_signup,
)

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = "your-secret-key"  # Replace with a secure secret key


# Initialize Supabase client
supabase = get_supabase_client()


@app.before_request
def load_user():
    """
    Load the user from the session and store in flask.g for each request.
    """
    g.user = get_user_from_session(supabase)


# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            # flash("Please sign in to access this page.", "warning")
            return redirect(url_for("signin"))
        return f(*args, **kwargs)

    return decorated_function


@app.route("/")
@login_required
def index():
    """
    Home route that returns a welcome message and lists all topics.
    """
    topics = get_topics()
    if not topics:
        flash("No topics available.", "warning")
    return render_template("index.html", user=g.user, topics=topics)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """
    Route for user signup.
    """
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")  # Get confirm password

        error = is_valid_credentails_for_signup(email, password, confirm_password)

        if error:
            flash(error, "danger")
            return redirect(url_for("signup"))

        # Call Supabase signup function
        try:
            response = supabase.auth.sign_up({"email": email, "password": password})

            print("Signup response user:", response.user)
            print("Signup response session:", response.session)

            if response.user:
                flash("Signup successful!", "success")
        except Exception as e:
            print("Error during signup:", e)
            flash("Signup failed. Please try again.", "danger")
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


@app.route("/test_config/<topic>", methods=["GET", "POST"])
@login_required
def test_config(topic):
    """
    Page to configure test settings for a selected topic.
    Allows user to choose number of questions and test duration.
    """
    topics = get_topics()
    if topic not in topics:
        flash("Invalid topic selected.", "danger")
        return redirect(url_for("index"))

    # Get the maximum number of questions available for this topic
    max_questions = get_num_questions_topic(topic)
    # Ensure we have at least 1 question available
    max_questions = max(1, max_questions)

    if request.method == "POST":
        num_questions = int(request.form.get("num_questions", 5))
        # Limit num_questions to available questions
        num_questions = min(num_questions, max_questions)
        duration = int(request.form.get("duration", 10))  # in minutes
        # Fetch questions for the topic
        questions = get_questions_for_topic(topic, num_questions)
        # Store config in session or pass to test page (not implemented here)
        return render_template(
            "test_page.html",
            topic=topic,
            questions=questions,
            duration=duration,
            user=g.user,
            QuestionType=QuestionType,
        )

    # Default values for form - ensure default is not greater than max
    default_num_questions = min(5, max_questions)
    return render_template(
        "test_config.html",
        topic=topic,
        user=g.user,
        default_num_questions=default_num_questions,
        default_duration=10,
        max_questions=max_questions,
    )


if __name__ == "__main__":
    print("Registered routes:")
    print(app.url_map)
    print("-" * 30)  # Separator for clarity
    print(get_table_names())
    app.run(debug=True, host="0.0.0.0", port=5000)
