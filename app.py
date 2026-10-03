from datetime import timedelta
from flask import Flask, request, session, redirect, url_for, render_template_string
from werkzeug.security import generate_password_hash, check_password_hash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

# Demo secret only. Never use a real secret in source code.
app.config["SECRET_KEY"] = "development-only-secret-change-in-production"

# Secure session configuration
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SECURE"] = False  # True when deployed with HTTPS
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=15)

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=[]
)

# Local educational user store
users = {}


def validate_username(username):
    return (
        isinstance(username, str)
        and 3 <= len(username) <= 30
        and username.isalnum()
    )


def validate_password(password):
    return isinstance(password, str) and len(password) >= 8


# ============================================================
# COMMON DESIGN
# ============================================================

BASE_STYLE = """
<style>
* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: Arial, Helvetica, sans-serif;
    min-height: 100vh;
    background:
        radial-gradient(circle at top left, #12345b 0%, transparent 35%),
        radial-gradient(circle at bottom right, #082f49 0%, transparent 35%),
        #07111f;
    color: #e5eef8;
}

a {
    text-decoration: none;
}

.container {
    width: 100%;
    max-width: 1100px;
    margin: auto;
    padding: 30px 20px;
}

/* Navigation */

.navbar {
    border-bottom: 1px solid rgba(255,255,255,0.08);
    background: rgba(5, 15, 28, 0.82);
    backdrop-filter: blur(12px);
}

.nav-content {
    max-width: 1100px;
    margin: auto;
    padding: 18px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.logo {
    font-size: 20px;
    font-weight: bold;
    color: white;
}

.logo span {
    color: #38bdf8;
}

.nav-badge {
    font-size: 12px;
    padding: 7px 12px;
    border: 1px solid rgba(56,189,248,0.3);
    border-radius: 20px;
    color: #7dd3fc;
}

/* Hero */

.hero {
    min-height: calc(100vh - 75px);
    display: flex;
    align-items: center;
}

.hero-grid {
    width: 100%;
    display: grid;
    grid-template-columns: 1.1fr 0.9fr;
    gap: 70px;
    align-items: center;
}

.eyebrow {
    color: #38bdf8;
    font-size: 13px;
    font-weight: bold;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 18px;
}

.hero h1 {
    font-size: 55px;
    line-height: 1.05;
    margin-bottom: 20px;
}

.hero h1 span {
    color: #38bdf8;
}

.hero p {
    color: #94a9bf;
    line-height: 1.8;
    font-size: 17px;
    margin-bottom: 30px;
}

.buttons {
    display: flex;
    gap: 14px;
    flex-wrap: wrap;
}

.btn {
    display: inline-block;
    padding: 13px 22px;
    border-radius: 9px;
    font-weight: bold;
    transition: 0.2s;
}

.btn-primary {
    background: #0284c7;
    color: white;
}

.btn-primary:hover {
    background: #0ea5e9;
    transform: translateY(-2px);
}

.btn-secondary {
    border: 1px solid #334e68;
    color: #dbeafe;
    background: rgba(255,255,255,0.03);
}

.btn-secondary:hover {
    border-color: #38bdf8;
}

/* Security card */

.security-card {
    background: rgba(15, 31, 50, 0.78);
    border: 1px solid rgba(56,189,248,0.18);
    border-radius: 20px;
    padding: 30px;
    box-shadow: 0 25px 70px rgba(0,0,0,0.35);
}

.shield {
    width: 65px;
    height: 65px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 16px;
    background: rgba(14,165,233,0.12);
    border: 1px solid rgba(56,189,248,0.25);
    font-size: 30px;
    margin-bottom: 22px;
}

.security-card h2 {
    margin-bottom: 10px;
}

.security-card p {
    font-size: 14px;
    color: #8da4bb;
    line-height: 1.7;
}

.features {
    margin-top: 25px;
    display: grid;
    gap: 12px;
}

.feature {
    padding: 13px;
    border-radius: 10px;
    background: rgba(255,255,255,0.035);
    color: #c9d8e8;
    font-size: 14px;
}

.feature span {
    color: #38bdf8;
    margin-right: 8px;
}

/* Authentication */

.auth-wrapper {
    min-height: calc(100vh - 75px);
    display: flex;
    align-items: center;
    justify-content: center;
}

.auth-card {
    width: 100%;
    max-width: 450px;
    background: rgba(15, 31, 50, 0.88);
    border: 1px solid rgba(56,189,248,0.18);
    border-radius: 20px;
    padding: 38px;
    box-shadow: 0 25px 70px rgba(0,0,0,0.4);
}

.auth-icon {
    width: 58px;
    height: 58px;
    border-radius: 14px;
    background: rgba(14,165,233,0.12);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 26px;
    margin-bottom: 20px;
}

.auth-card h1 {
    margin-bottom: 8px;
}

.subtitle {
    color: #8198ae;
    font-size: 14px;
    margin-bottom: 28px;
}

.form-group {
    margin-bottom: 18px;
}

.form-group label {
    display: block;
    font-size: 13px;
    font-weight: bold;
    color: #cbd9e8;
    margin-bottom: 8px;
}

.form-group input {
    width: 100%;
    padding: 13px 14px;
    border-radius: 9px;
    border: 1px solid #29445e;
    background: #091827;
    color: white;
    outline: none;
    font-size: 14px;
}

.form-group input:focus {
    border-color: #38bdf8;
    box-shadow: 0 0 0 3px rgba(56,189,248,0.1);
}

.auth-button {
    width: 100%;
    border: none;
    cursor: pointer;
    padding: 14px;
    border-radius: 9px;
    background: #0284c7;
    color: white;
    font-weight: bold;
    font-size: 15px;
    margin-top: 5px;
}

.auth-button:hover {
    background: #0ea5e9;
}

.auth-footer {
    margin-top: 22px;
    text-align: center;
    color: #8198ae;
    font-size: 14px;
}

.auth-footer a {
    color: #38bdf8;
}

/* Dashboard */

.dashboard {
    padding-top: 50px;
}

.welcome {
    margin-bottom: 30px;
}

.welcome .eyebrow {
    margin-bottom: 10px;
}

.welcome h1 {
    font-size: 38px;
    margin-bottom: 10px;
}

.welcome p {
    color: #8da4bb;
}

.dashboard-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 18px;
    margin-bottom: 25px;
}

.dashboard-card {
    padding: 25px;
    border-radius: 16px;
    background: rgba(15,31,50,0.78);
    border: 1px solid rgba(255,255,255,0.07);
}

.dashboard-card .icon {
    font-size: 25px;
    margin-bottom: 15px;
}

.dashboard-card h3 {
    margin-bottom: 7px;
}

.dashboard-card p {
    color: #8198ae;
    font-size: 13px;
    line-height: 1.6;
}

.status-card {
    padding: 25px;
    border-radius: 16px;
    background: rgba(15,31,50,0.78);
    border: 1px solid rgba(56,189,248,0.15);
    margin-bottom: 25px;
}

.status {
    display: inline-block;
    margin-top: 10px;
    padding: 7px 12px;
    border-radius: 20px;
    background: rgba(34,197,94,0.1);
    color: #86efac;
    font-size: 12px;
}

.logout {
    display: inline-block;
    padding: 12px 20px;
    border-radius: 8px;
    border: 1px solid #334e68;
    color: #dbeafe;
}

.logout:hover {
    border-color: #38bdf8;
}

/* Responsive */

@media (max-width: 800px) {
    .hero-grid {
        grid-template-columns: 1fr;
        gap: 35px;
    }

    .hero h1 {
        font-size: 40px;
    }

    .dashboard-grid {
        grid-template-columns: 1fr;
    }
}
</style>
"""


NAVBAR = """
<div class="navbar">
    <div class="nav-content">
        <div class="logo">🛡️ Secure<span>Auth</span></div>
        <div class="nav-badge">CYBER SECURITY LAB</div>
    </div>
</div>
"""


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():
    return render_template_string(
        BASE_STYLE + NAVBAR + """
        <div class="container hero">
            <div class="hero-grid">

                <div>
                    <div class="eyebrow">Cyber Security Internship</div>

                    <h1>
                        Secure<br>
                        <span>Authentication</span>
                    </h1>

                    <p>
                        A practical authentication security lab demonstrating
                        password protection, secure sessions, validation,
                        rate limiting and defensive authentication controls.
                    </p>

                    <div class="buttons">
                        <a href="/login" class="btn btn-primary">
                            🔐 Login
                        </a>

                        <a href="/register" class="btn btn-secondary">
                            Create Account
                        </a>
                    </div>
                </div>

                <div class="security-card">
                    <div class="shield">🛡️</div>

                    <h2>Security Controls</h2>

                    <p>
                        This local lab demonstrates fundamental defensive
                        authentication techniques.
                    </p>

                    <div class="features">
                        <div class="feature">
                            <span>✓</span> Password Hashing
                        </div>

                        <div class="feature">
                            <span>✓</span> Secure Session Cookies
                        </div>

                        <div class="feature">
                            <span>✓</span> Server-Side Validation
                        </div>

                        <div class="feature">
                            <span>✓</span> Login Rate Limiting
                        </div>

                        <div class="feature">
                            <span>✓</span> Generic Authentication Errors
                        </div>

                        <div class="feature">
                            <span>✓</span> Session Expiration
                        </div>
                    </div>
                </div>

            </div>
        </div>
        """
    )


# ============================================================
# REGISTER
# ============================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "GET":
        return render_template_string(
            BASE_STYLE + NAVBAR + """
            <div class="container auth-wrapper">
                <div class="auth-card">

                    <div class="auth-icon">👤</div>

                    <h1>Create Account</h1>

                    <p class="subtitle">
                        Create a secure account for the authentication lab.
                    </p>

                    <form method="post">

                        <div class="form-group">
                            <label>Username</label>
                            <input
                                name="username"
                                placeholder="Enter username"
                                autocomplete="username"
                                required
                            >
                        </div>

                        <div class="form-group">
                            <label>Password</label>
                            <input
                                name="password"
                                type="password"
                                placeholder="Minimum 8 characters"
                                autocomplete="new-password"
                                required
                            >
                        </div>

                        <button class="auth-button" type="submit">
                            Create Account
                        </button>

                    </form>

                    <div class="auth-footer">
                        Already have an account?
                        <a href="/login">Sign in</a>
                    </div>

                </div>
            </div>
            """
        )

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    if not validate_username(username):
        return "Invalid registration data.", 400

    if not validate_password(password):
        return "Invalid registration data.", 400

    if username in users:
        return "Registration failed.", 400

    users[username] = generate_password_hash(password)

    return """
    <html>
    <body style="font-family:Arial;text-align:center;padding:100px;background:#07111f;color:white;">
        <h1>✓ Registration Successful</h1>
        <p>Your account has been created securely.</p>
        <br>
        <a href="/login" style="color:#38bdf8;">Continue to Login</a>
    </body>
    </html>
    """


# ============================================================
# LOGIN
# ============================================================

@app.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def login():

    if request.method == "GET":
        return render_template_string(
            BASE_STYLE + NAVBAR + """
            <div class="container auth-wrapper">
                <div class="auth-card">

                    <div class="auth-icon">🔐</div>

                    <h1>Welcome Back</h1>

                    <p class="subtitle">
                        Sign in to access your secure dashboard.
                    </p>

                    <form method="post">

                        <div class="form-group">
                            <label>Username</label>
                            <input
                                name="username"
                                placeholder="Enter username"
                                autocomplete="username"
                                required
                            >
                        </div>

                        <div class="form-group">
                            <label>Password</label>
                            <input
                                name="password"
                                type="password"
                                placeholder="Enter password"
                                autocomplete="current-password"
                                required
                            >
                        </div>

                        <button class="auth-button" type="submit">
                            Sign In Securely
                        </button>

                    </form>

                    <div class="auth-footer">
                        Don't have an account?
                        <a href="/register">Create one</a>
                    </div>

                </div>
            </div>
            """
        )

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    if (
        username not in users
        or not check_password_hash(users[username], password)
    ):
        # Keep this exact response for the automated security test.
        return "Invalid username or password.", 401

    session.clear()
    session["username"] = username
    session.permanent = True

    return redirect(url_for("dashboard"))


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/dashboard")
def dashboard():

    if "username" not in session:
        return redirect(url_for("login"))

    return render_template_string(
        BASE_STYLE + NAVBAR + """
        <div class="container dashboard">

            <div class="welcome">
                <div class="eyebrow">Authenticated Session</div>

                <h1>Welcome, {{ username }} 👋</h1>

                <p>
                    Your secure authentication session is active.
                </p>
            </div>

            <div class="dashboard-grid">

                <div class="dashboard-card">
                    <div class="icon">🔐</div>
                    <h3>Authentication</h3>
                    <p>
                        Your credentials are verified using secure
                        password hashing.
                    </p>
                </div>

                <div class="dashboard-card">
                    <div class="icon">🛡️</div>
                    <h3>Session Security</h3>
                    <p>
                        Your session uses HttpOnly and SameSite
                        cookie protections.
                    </p>
                </div>

                <div class="dashboard-card">
                    <div class="icon">⚡</div>
                    <h3>Rate Protection</h3>
                    <p>
                        Login requests are protected by
                        rate limiting.
                    </p>
                </div>

            </div>

            <div class="status-card">

                <h2>Security Status</h2>

                <p style="color:#8198ae;margin-top:8px;">
                    Authentication controls are active for this
                    local security laboratory.
                </p>

                <div class="status">
                    ● SESSION ACTIVE
                </div>

            </div>

            <a href="/logout" class="logout">
                Logout Securely
            </a>

        </div>
        """,
        username=session["username"]
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)