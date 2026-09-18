from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)

# --------------------------------------------------
# BASIC CONFIGURATION
# --------------------------------------------------

app.secret_key = "transitcare_secret_key_change_later"

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------

def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


# --------------------------------------------------
# DATABASE INITIALIZATION / SAFE MIGRATION
# --------------------------------------------------

def init_db():

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # ---------------- USERS ----------------

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            password TEXT,
            role TEXT
        )
    """)

    # ---------------- ISSUES ----------------

    c.execute("""
        CREATE TABLE IF NOT EXISTS issues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            transport_type TEXT,
            route_number TEXT,
            category TEXT,
            description TEXT,
            date TEXT,
            priority TEXT DEFAULT 'Moderate',
            status TEXT DEFAULT 'Pending'
        )
    """)

    # Check existing columns
    c.execute("PRAGMA table_info(issues)")
    columns = [row[1] for row in c.fetchall()]

    # Add image column if missing
    if "image" not in columns:
        c.execute("""
            ALTER TABLE issues
            ADD COLUMN image TEXT
        """)

    # Add confirmations column if missing
    if "confirmations" not in columns:
        c.execute("""
            ALTER TABLE issues
            ADD COLUMN confirmations INTEGER DEFAULT 0
        """)

    # ---------------- CONFIRMATIONS ----------------

    c.execute("""
        CREATE TABLE IF NOT EXISTS confirmations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            issue_id INTEGER NOT NULL,
            UNIQUE(user_id, issue_id)
        )
    """)

    # ---------------- CHAT ESCALATIONS ----------------

    c.execute("""
        CREATE TABLE IF NOT EXISTS chat_escalations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            issue_id INTEGER,
            reason TEXT,
            message TEXT,
            status TEXT DEFAULT 'Open',
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


# Run database initialization
init_db()


# --------------------------------------------------
# HOME
# --------------------------------------------------

@app.route("/")
def home():
    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM issues")
    total = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM issues WHERE status='Pending'")
    pending = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM issues WHERE status='Resolved'")
    resolved = c.fetchone()[0]

    conn.close()

    return render_template(
        "home.html",
        total=total,
        pending=pending,
        resolved=resolved
    )


@app.route("/live_stats")
def live_stats():
    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM issues")
    total = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM issues WHERE status='Pending'")
    pending = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM issues WHERE status='Resolved'")
    resolved = c.fetchone()[0]

    conn.close()

    return jsonify({
        "total": total,
        "pending": pending,
        "resolved": resolved
    })


# --------------------------------------------------
# SELECT ROLE
# --------------------------------------------------

@app.route("/select/<role>")
def select_role(role):

    if role not in ["user", "authority"]:
        return redirect("/")

    session["selected_role"] = role

    return redirect("/login")


# --------------------------------------------------
# REGISTER
# --------------------------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"].strip()
        email = request.form["email"].strip()
        password = request.form["password"]

        conn = get_db()
        c = conn.cursor()

        # Check if email already exists
        c.execute(
            "SELECT id FROM users WHERE email=?",
            (email,)
        )

        existing_user = c.fetchone()

        if existing_user:
            conn.close()

            return """
            <script>
                alert("Email already registered!");
                window.location.href="/register";
            </script>
            """

        c.execute("""
            INSERT INTO users
            (name, email, password, role)
            VALUES (?, ?, ?, ?)
        """, (
            name,
            email,
            password,
            "user"
        ))

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")


# --------------------------------------------------
# LOGIN
# --------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    role = session.get("selected_role")

    if request.method == "POST":

        email = request.form["email"].strip()
        password = request.form["password"]

        conn = get_db()
        c = conn.cursor()

        c.execute("""
            SELECT *
            FROM users
            WHERE email=?
            AND password=?
            AND role=?
        """, (
            email,
            password,
            role
        ))

        user = c.fetchone()

        conn.close()

        if user:

            session["user_id"] = user["id"]
            session["role"] = user["role"]
            session["user_name"] = user["name"]

            if role == "authority":
                return redirect("/authority")

            return redirect("/user_home")

        return """
        <script>
            alert("Invalid credentials!");
            window.history.back();
        </script>
        """

    return render_template(
        "login.html",
        role=role
    )


# --------------------------------------------------
# USER COMPLAINT DASHBOARD
# --------------------------------------------------

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():

    if session.get("role") != "user":
        return redirect("/")

    if request.method == "POST":

        transport_type = request.form.get("transport_type")
        route_number = request.form.get("route_number")
        category = request.form.get("category")
        description = request.form.get("description")

        # ---------------- IMAGE ----------------

        image_file = request.files.get("image")

        filename = None

        if image_file and image_file.filename:

            filename = secure_filename(
                image_file.filename
            )

            image_path = os.path.join(
                app.config["UPLOAD_FOLDER"],
                filename
            )

            image_file.save(image_path)

        # ---------------- DATABASE ----------------

        conn = get_db()
        c = conn.cursor()

        current_date = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        c.execute("""
            INSERT INTO issues
            (
                user_id,
                transport_type,
                route_number,
                category,
                description,
                date,
                priority,
                status,
                image,
                confirmations
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session["user_id"],
            transport_type,
            route_number,
            category,
            description,
            current_date,
            "Moderate",
            "Pending",
            filename,
            0
        ))

        conn.commit()
        conn.close()

        session["success_msg"] = (
            "Complaint submitted successfully!"
        )

        return redirect("/dashboard")

    # ---------------- GET COMPLAINTS ----------------

    conn = get_db()
    c = conn.cursor()

    c.execute("""
        SELECT *
        FROM issues
        WHERE user_id=?
        ORDER BY id DESC
    """, (
        session["user_id"],
    ))

    issues = c.fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        issues=issues,
        success_msg=session.pop(
            "success_msg",
            None
        )
    )


# --------------------------------------------------
# AUTHORITY DASHBOARD
# --------------------------------------------------

@app.route("/authority")
def authority():

    if session.get("role") != "authority":
        return redirect("/")

    conn = get_db()
    c = conn.cursor()

    # All complaints
    c.execute("""
        SELECT *
        FROM issues
        ORDER BY id DESC
    """)

    issues = c.fetchall()

    # ---------------- COUNTS ----------------

    c.execute(
        "SELECT COUNT(*) FROM issues"
    )

    total = c.fetchone()[0]

    c.execute("""
        SELECT COUNT(*)
        FROM issues
        WHERE status='Pending'
    """)

    pending = c.fetchone()[0]

    c.execute("""
        SELECT COUNT(*)
        FROM issues
        WHERE status='In Review'
    """)

    review = c.fetchone()[0]

    c.execute("""
        SELECT COUNT(*)
        FROM issues
        WHERE status='Resolved'
    """)

    resolved = c.fetchone()[0]

    # ---------------- CATEGORY ANALYTICS ----------------

    c.execute("""
        SELECT category, COUNT(*)
        FROM issues
        GROUP BY category
    """)

    category_data = c.fetchall()

    category_labels = [
        row[0] for row in category_data
    ]

    category_counts = [
        row[1] for row in category_data
    ]

    # ---------------- TRANSPORT ANALYTICS ----------------

    c.execute("""
        SELECT transport_type, COUNT(*)
        FROM issues
        GROUP BY transport_type
    """)

    transport_data = c.fetchall()

    transport_labels = [
        row[0] for row in transport_data
    ]

    transport_counts = [
        row[1] for row in transport_data
    ]

    # ---------------- CUSTOMER CARE ESCALATIONS ----------------

    c.execute("""
        SELECT
            ce.id,
            ce.user_id,
            u.name,
            ce.issue_id,
            i.transport_type,
            i.route_number,
            i.category,
            ce.reason,
            ce.message,
            ce.status,
            ce.created_at
        FROM chat_escalations ce
        LEFT JOIN users u
            ON ce.user_id = u.id
        LEFT JOIN issues i
            ON ce.issue_id = i.id
        ORDER BY ce.id DESC
    """)

    escalations = c.fetchall()

    c.execute("""
        SELECT COUNT(*)
        FROM chat_escalations
    """)
    total_escalations = c.fetchone()[0]

    c.execute("""
        SELECT COUNT(*)
        FROM chat_escalations
        WHERE status='Open'
    """)
    open_escalations = c.fetchone()[0]

    c.execute("""
        SELECT COUNT(*)
        FROM chat_escalations
        WHERE status='In Progress'
    """)
    in_progress_escalations = c.fetchone()[0]

    c.execute("""
        SELECT COUNT(*)
        FROM chat_escalations
        WHERE status='Resolved'
    """)
    resolved_escalations = c.fetchone()[0]

    conn.close()

    return render_template(
        "authority.html",
        issues=issues,
        total=total,
        pending=pending,
        review=review,
        resolved=resolved,
        category_labels=category_labels,
        category_data=category_counts,
        transport_labels=transport_labels,
        transport_data=transport_counts,
        escalations=escalations,
        total_escalations=total_escalations,
        open_escalations=open_escalations,
        in_progress_escalations=in_progress_escalations,
        resolved_escalations=resolved_escalations
    )


# --------------------------------------------------
# UPDATE CUSTOMER CARE ESCALATION
# --------------------------------------------------

@app.route("/update_escalation", methods=["POST"])
def update_escalation():

    if session.get("role") != "authority":
        return redirect("/")

    escalation_id = request.form.get("id")
    status = request.form.get("status")

    allowed_statuses = [
        "Open",
        "In Progress",
        "Resolved"
    ]

    if status not in allowed_statuses:
        return redirect("/authority")

    conn = get_db()
    c = conn.cursor()

    c.execute("""
        UPDATE chat_escalations
        SET status=?
        WHERE id=?
    """, (
        status,
        escalation_id
    ))

    conn.commit()
    conn.close()

    return redirect("/authority")


# --------------------------------------------------
# CREATE AUTHORITY
# --------------------------------------------------

@app.route("/create_authority")
def create_authority():

    conn = get_db()
    c = conn.cursor()

    # Prevent duplicate admin creation
    c.execute("""
        SELECT id
        FROM users
        WHERE email=?
        AND role='authority'
    """, (
        "admin@gmail.com",
    ))

    existing = c.fetchone()

    if existing:
        conn.close()

        return """
        Authority already exists.<br><br>
        Email: admin@gmail.com
        """

    c.execute("""
        INSERT INTO users
        (name, email, password, role)
        VALUES (?, ?, ?, ?)
    """, (
        "Admin",
        "admin@gmail.com",
        "admin123",
        "authority"
    ))

    conn.commit()
    conn.close()

    return """
    Authority Created<br><br>
    Email: admin@gmail.com<br>
    Password: admin123
    """


# --------------------------------------------------
# LOGOUT
# --------------------------------------------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# --------------------------------------------------
# UPDATE PRIORITY
# --------------------------------------------------

@app.route("/update_priority", methods=["POST"])
def update_priority():

    issue_id = request.form["id"]
    priority = request.form["priority"]

    conn = get_db()
    c = conn.cursor()

    c.execute("""
        UPDATE issues
        SET priority=?
        WHERE id=?
    """, (
        priority,
        issue_id
    ))

    conn.commit()
    conn.close()

    return redirect("/authority")


# --------------------------------------------------
# UPDATE STATUS
# --------------------------------------------------

@app.route("/update_status", methods=["POST"])
def update_status():

    issue_id = request.form["id"]
    status = request.form["status"]

    conn = get_db()
    c = conn.cursor()

    c.execute("""
        UPDATE issues
        SET status=?
        WHERE id=?
    """, (
        status,
        issue_id
    ))

    conn.commit()
    conn.close()

    return redirect("/authority")


# --------------------------------------------------
# CONFIRM ISSUE
# --------------------------------------------------

@app.route("/confirm_issue", methods=["POST"])
def confirm_issue():

    if session.get("role") != "user":
        return redirect("/")

    issue_id = request.form["issue_id"]
    user_id = session["user_id"]

    conn = get_db()
    c = conn.cursor()

    # Check whether this user already confirmed
    c.execute("""
        SELECT id
        FROM confirmations
        WHERE user_id=?
        AND issue_id=?
    """, (
        user_id,
        issue_id
    ))

    existing = c.fetchone()

    if existing:

        session["confirm_msg"] = (
            "You can confirm an issue only once!"
        )

    else:

        try:

            c.execute("""
                INSERT INTO confirmations
                (user_id, issue_id)
                VALUES (?, ?)
            """, (
                user_id,
                issue_id
            ))

            c.execute("""
                UPDATE issues
                SET confirmations =
                    COALESCE(confirmations, 0) + 1
                WHERE id=?
            """, (
                issue_id,
            ))

            conn.commit()

            session["confirm_msg"] = (
                "Issue confirmed successfully!"
            )

        except sqlite3.IntegrityError:

            session["confirm_msg"] = (
                "You have already confirmed this issue."
            )

    conn.close()

    return redirect("/user_home")


# --------------------------------------------------
# USER HOME
# --------------------------------------------------

@app.route("/user_home")
def user_home():

    if session.get("role") != "user":
        return redirect("/")

    conn = get_db()
    c = conn.cursor()

    # Community complaints
    c.execute("""
        SELECT *
        FROM issues
        ORDER BY id DESC
    """)

    all_issues = c.fetchall()

    # Complaints reported by the logged-in user
    user_id = session.get("user_id")
    c.execute("""
        SELECT *
        FROM issues
        WHERE user_id=?
        ORDER BY id DESC
    """, (user_id,))

    issues = c.fetchall()

    # User-specific statistics
    c.execute("SELECT COUNT(*) FROM issues WHERE user_id=?", (user_id,))
    total = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM issues WHERE user_id=? AND status='Pending'", (user_id,))
    pending = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM issues WHERE user_id=? AND status='Resolved'", (user_id,))
    resolved = c.fetchone()[0]

    conn.close()

    return render_template(
        "user_home.html",
        all_issues=all_issues,
        issues=issues,
        total=total,
        pending=pending,
        resolved=resolved,
        confirm_msg=session.pop(
            "confirm_msg",
            None
        )
    )


# ==================================================
# CHATBOT
# ==================================================

def localize_chat_reply(reply, language):
    """Translate chatbot's fixed English phrases into Roman Hindi/Marathi.
    Dynamic complaint values such as route numbers, dates and IDs remain unchanged.
    """
    if language == "en":
        return reply

    hi = [
        ("Please type a message so I can help you. 😊", "Kripya ek message type karein, main aapki madad karunga. 😊"),
        ("👋 Hello! Welcome to <b>TransitCare</b>.", "👋 Namaste! <b>TransitCare</b> mein aapka swagat hai."),
        ("I'm your TransitCare Assistant. I can help you with:", "Main aapka TransitCare Assistant hoon. Main in cheezon mein madad kar sakta hoon:"),
        ("Reporting a transport issue", "Transport ki problem report karna"), ("Checking complaint status", "Complaint ka status check karna"),
        ("Understanding the complaint process", "Complaint process samajhna"), ("Getting customer-care assistance", "Customer-care ki madad lena"),
        ("How can I help you today?", "Aaj main aapki kaise madad kar sakta hoon?"),
        ("To protect your complaint information,", "Aapki complaint information ko surakshit rakhne ke liye,"),
        ("please log in to your TransitCare account first.", "pehle apne TransitCare account mein login karein."),
        ("Once logged in, I can check your complaints directly from the TransitCare database.", "Login karne ke baad main TransitCare database se aapki complaints ka status check kar sakta hoon."),
        ("I couldn't find any complaints linked to your account yet.", "Aapke account se judi koi complaint abhi nahi mili."),
        ("If you have a transport problem, I can guide you through reporting it.", "Agar transport ki koi problem hai, main use report karne mein aapko guide kar sakta hoon."),
        ("🔎 <b>Here are your latest complaints:</b>", "🔎 <b>Aapki latest complaints yahan hain:</b>"),
        ("Complaint", "Complaint"), ("Status:", "Status:"), ("Priority:", "Priority:"), ("Reported:", "Report ki gayi:"),
        ("🔐 Please log in to your TransitCare account before requesting an escalation.", "🔐 Escalation request karne se pehle apne TransitCare account mein login karein."),
        ("I couldn't find a complaint linked to your account.", "Aapke account se judi complaint nahi mili."),
        ("Please register a complaint first.", "Pehle complaint register karein."),
        ("✅ <b>Your complaint is already resolved.</b>", "✅ <b>Aapki complaint pehle hi resolve ho chuki hai.</b>"),
        ("The authority has already marked this complaint as", "Authority ne is complaint ko pehle hi"),
        ("No new escalation has been created.", "Koi naya escalation create nahi kiya gaya hai."),
        ("🚨 <b>This complaint has already been escalated.</b>", "🚨 <b>Is complaint ka escalation pehle hi ho chuka hai.</b>"),
        ("Escalation ID:", "Escalation ID:"), ("Escalation Status:", "Escalation Status:"),
        ("A duplicate escalation will not be created.", "Duplicate escalation create nahi kiya jayega."),
        ("🚨 <b>Emergency escalation created immediately.</b>", "🚨 <b>Emergency escalation turant create ho gaya hai.</b>"),
        ("⚠️ Your issue appears to be an emergency, so it has been sent to customer care without waiting.", "⚠️ Aapki problem emergency lag rahi hai, isliye ise bina wait kiye customer care ko bhej diya gaya hai."),
        ("🚨 <b>Customer-care escalation created.</b>", "🚨 <b>Customer-care escalation create ho gaya hai.</b>"),
        ("This normal complaint has been unresolved for", "Yeh normal complaint"),
        ("days</b>, so it is now eligible for customer-care escalation.", "dinon se unresolved hai, isliye ab customer-care escalation ke liye eligible hai."),
        ("⏳ <b>Your complaint is still within the normal resolution period.</b>", "⏳ <b>Aapki complaint abhi normal resolution period mein hai.</b>"),
        ("Days since report:", "Report ke baad din:"),
        ("Customer-care escalation for normal issues becomes available after <b>10 days</b> if the complaint remains unresolved.", "Agar complaint unresolved rahti hai, to normal issues ke liye customer-care escalation <b>10 din</b> baad available hota hai."),
        ("remain before escalation becomes available.", "din baaki hain, uske baad escalation available hoga."),
        ("📝 <b>I can help you report a transport issue.</b>", "📝 <b>Main aapko transport problem report karne mein madad kar sakta hoon.</b>"),
        ("Common complaints include:", "Common complaints mein shamil hain:"), ("Bus or train delays", "Bus ya train ki deri"), ("Cleanliness problems", "Safai ki problems"), ("Overcrowding", "Zyada bheed"), ("AC not working", "AC kaam nahi kar raha"), ("Staff behaviour", "Staff ka behaviour"), ("Broken seats, handles or doors", "Tooti seats, handles ya doors"),
        ("Please open the <b>Submit Complaint</b> section on your TransitCare dashboard and provide the transport type, route number and details.", "Apne TransitCare dashboard mein <b>Submit Complaint</b> section kholen aur transport type, route number aur details dein."),
        ("🚌 <b>Transport delay detected.</b>", "🚌 <b>Transport delay ki problem hai.</b>"), ("You can report the delay through TransitCare.", "Aap TransitCare ke through delay report kar sakte hain."), ("Approximate delay", "Lagbhag kitni deri"), ("Any additional details", "Koi aur details"), ("You can also upload a supporting image if useful.", "Agar zaroori ho to supporting image bhi upload kar sakte hain."),
        ("🔧 <b>This appears to be a maintenance issue.</b>", "🔧 <b>Yeh maintenance issue lag raha hai.</b>"), ("Please report it through TransitCare with:", "Ise TransitCare par in details ke saath report karein:"), ("Description of the damage", "Damage ka description"), ("Photo, if possible", "Photo, agar possible ho"), ("A photo can help the authority understand the problem more quickly.", "Photo se authority ko problem jaldi samajhne mein madad mil sakti hai."),
        ("⚠️ <b>Staff behaviour complaint</b>", "⚠️ <b>Staff behaviour ki complaint</b>"), ("You can report the incident through TransitCare.", "Aap incident ko TransitCare ke through report kar sakte hain."), ("Please include as much factual information as possible, such as the transport type, route number and what happened.", "Transport type, route number aur kya hua jaise factual details jitni ho sake include karein."), ("If you need direct assistance or the situation cannot be resolved through the normal complaint process, I can help you request customer-care support.", "Agar direct help chahiye ya normal complaint process se problem solve nahi hoti, main customer-care support request karne mein madad kar sakta hoon."),
        ("👨‍💼 <b>Customer Care</b>", "👨‍💼 <b>Customer Care</b>"), ("Please log in first so that customer care can associate your request with your account.", "Pehle login karein taaki customer care aapki request ko account se jod sake."), ("After logging in, ask me for <b>customer care</b> again and I can create an escalation request.", "Login ke baad mujhse dobara <b>customer care</b> ke baare mein poochein, main escalation request create kar sakta hoon."), ("👨‍💼 <b>Customer Care Assistance</b>", "👨‍💼 <b>Customer Care Assistance</b>"), ("I can escalate an unresolved issue to customer care.", "Main unresolved issue ko customer care tak escalate kar sakta hoon."), ("Please tell me briefly what you need help with,", "Kripya short mein batayein ki aapko kis cheez mein help chahiye,"), ("I need to speak to an agent.", "Mujhe agent se baat karni hai."),
        ("😊 You're welcome!", "😊 Aapka swagat hai!"), ("I'm here whenever you need help with TransitCare.", "Jab bhi TransitCare mein help chahiye, main yahin hoon."),
        ("🤔 I'm not completely sure I understood that.", "🤔 Mujhe poori tarah samajh nahi aaya."), ("You can ask me things like:", "Aap mujhse aise pooch sakte hain:"), ("I want to report a bus delay", "Mujhe bus ki deri report karni hai"), ("My seat is broken", "Meri seat tooti hui hai"), ("How do I complain about a conductor?", "Conductor ki complaint kaise karun?"), ("Check my complaint status", "Meri complaint ka status check karo"), ("I need customer care", "Mujhe customer care chahiye"), ("My complaint is not resolved", "Meri complaint resolve nahi hui hai")
    ]
    mr = [
        ("Please type a message so I can help you. 😊", "Krupaya ek message type kara, mi tumhala madat karto. 😊"),
        ("👋 Hello! Welcome to <b>TransitCare</b>.", "👋 Namaskar! <b>TransitCare</b> madhye tumche swagat aahe."),
        ("I'm your TransitCare Assistant. I can help you with:", "Mi tumcha TransitCare Assistant aahe. Mi ya goshtinmadhe madat karu shakto:"),
        ("Reporting a transport issue", "Vahatukichi samasya nondavne"), ("Checking complaint status", "Takrarichi sthiti tapasa"), ("Understanding the complaint process", "Takrar prakriya samjun ghya"), ("Getting customer-care assistance", "Customer-care chi madat ghya"),
        ("How can I help you today?", "Aaj mi tumchi kashi madat karu?"), ("please log in to your TransitCare account first.", "pratham tumchya TransitCare account madhye login kara."), ("Once logged in, I can check your complaints directly from the TransitCare database.", "Login kelyanantar mi TransitCare database madhun tumchya takrari tapasu shakto."),
        ("I couldn't find any complaints linked to your account yet.", "Tumchya accountshi jodlele kontihi takrar ajun sapadli nahi."), ("If you have a transport problem, I can guide you through reporting it.", "Vahatukichi samasya asel tar mi ti nondavnyasathi margadarshan karu shakto."), ("🔎 <b>Here are your latest complaints:</b>", "🔎 <b>Tumchya latest takrari ithe aahet:</b>"),
        ("Status:", "Sthiti:"), ("Priority:", "Pradhanya:"), ("Reported:", "Nondavle:"), ("🔐 Please log in to your TransitCare account before requesting an escalation.", "🔐 Escalation magnyapurvi tumchya TransitCare account madhye login kara."), ("I couldn't find a complaint linked to your account.", "Tumchya accountshi jodlele takrar sapadli nahi."), ("Please register a complaint first.", "Pratham takrar register kara."),
        ("✅ <b>Your complaint is already resolved.</b>", "✅ <b>Tumchi takrar aadhich nikali nighali aahe.</b>"), ("No new escalation has been created.", "Navin escalation tayar keleले nahi."), ("🚨 <b>This complaint has already been escalated.</b>", "🚨 <b>Ya takrariche escalation aadhich kele aahe.</b>"), ("A duplicate escalation will not be created.", "Duplicate escalation tayar kele janar nahi."),
        ("🚨 <b>Emergency escalation created immediately.</b>", "🚨 <b>Emergency escalation lagech tayar kele aahe.</b>"), ("⚠️ Your issue appears to be an emergency, so it has been sent to customer care without waiting.", "⚠️ Tumchi samasya emergency vatat aahe, mhanun ti wait na karta customer care kade pathavli aahe."), ("🚨 <b>Customer-care escalation created.</b>", "🚨 <b>Customer-care escalation tayar kele aahe.</b>"),
        ("This normal complaint has been unresolved for", "Hi normal takrar"), ("⏳ <b>Your complaint is still within the normal resolution period.</b>", "⏳ <b>Tumchi takrar ajun normal resolution period madhye aahe.</b>"), ("Days since report:", "Takraripasun divas:"), ("Customer-care escalation for normal issues becomes available after <b>10 days</b> if the complaint remains unresolved.", "Takrar unresolved rahilyas normal issues sathi customer-care escalation <b>10 divas</b> nantar available hote."), ("remain before escalation becomes available.", "divas baki aahet; tyanantar escalation available hoil."),
        ("📝 <b>I can help you report a transport issue.</b>", "📝 <b>Mi tumhala vahatukichi samasya nondavnyas madat karu shakto.</b>"), ("Common complaints include:", "Samanya takrarinmadhe he samavisht aahe:"), ("Bus or train delays", "Bus kiwa train ushir"), ("Cleanliness problems", "Swachhatechya samasya"), ("Overcrowding", "Jast gardi"), ("AC not working", "AC chalat nahi"), ("Staff behaviour", "Staffche vartan"), ("Broken seats, handles or doors", "Tutilelya seats, handles kiwa doors"), ("You can report the delay through TransitCare.", "Tumhi TransitCare madhun ushirachi takrar nondavu shakta."), ("Approximate delay", "Andaje ushir"), ("Any additional details", "Itar mahiti"), ("You can also upload a supporting image if useful.", "Garaj asel tar supporting image upload karu shakta."),
        ("🔧 <b>This appears to be a maintenance issue.</b>", "🔧 <b>Hi maintenance problem vatat aahe.</b>"), ("Please report it through TransitCare with:", "TransitCare madhun ya mahitisah nondva:"), ("Description of the damage", "Nuksanache varnan"), ("Photo, if possible", "Photo, shakya asel tar"), ("A photo can help the authority understand the problem more quickly.", "Photomule adhikaryanna samasya lavkar samajnyas madat hoil."),
        ("⚠️ <b>Staff behaviour complaint</b>", "⚠️ <b>Staffchya vartanachi takrar</b>"), ("You can report the incident through TransitCare.", "Tumhi ha prakaar TransitCare madhun nondavu shakta."), ("Please include as much factual information as possible, such as the transport type, route number and what happened.", "Transport type, route number ani kay zale he shakya titke spasht liha."), ("👨‍💼 <b>Customer Care</b>", "👨‍💼 <b>Customer Care</b>"), ("Please log in first so that customer care can associate your request with your account.", "Pratham login kara, mhanje customer care tumchi request accountshi jodu shakel."), ("After logging in, ask me for <b>customer care</b> again and I can create an escalation request.", "Login kelyanantar mala punha <b>customer care</b> baddal vichara; mi escalation request tayar karu shakto."), ("👨‍💼 <b>Customer Care Assistance</b>", "👨‍💼 <b>Customer Care Assistance</b>"), ("I can escalate an unresolved issue to customer care.", "Mi unresolved issue customer care kade escalate karu shakto."), ("Please tell me briefly what you need help with,", "Tumhala kontya goshtit madat havi te thodkyat sanga,"),
        ("😊 You're welcome!", "😊 Tumche swagat aahe!"), ("I'm here whenever you need help with TransitCare.", "TransitCare sathi madat havi asel tevha mi ithech aahe."), ("🤔 I'm not completely sure I understood that.", "🤔 Mala te purnapane samajle nahi."), ("You can ask me things like:", "Tumhi mala ase vicharu shakta:")
    ]
    pairs = hi if language == "hi" else mr
    import re
    for src, dst in pairs:
        reply = re.sub(re.escape(src), dst, reply, flags=re.IGNORECASE)
    return reply


@app.route("/chatbot", methods=["POST"])
def chatbot():

    data = request.get_json(silent=True) or {}

    original_message = data.get(
        "message",
        ""
    ).strip()

    language = data.get("language", "en")
    if language not in ("en", "hi", "mr"):
        language = "en"

    message = original_message.lower()

    # --------------------------------------------------
    # EMPTY MESSAGE
    # --------------------------------------------------

    if not message:

        return jsonify({
            "reply": "Please type a message so I can help you. 😊"
        })


    # ==================================================
    # GREETING
    # ==================================================

    if any(word in message for word in [
        "hello",
        "hi",
        "hey",
        "good morning",
        "good afternoon",
        "good evening",
        "namaste", "namaskar", "namskar", "namaskaar", "hello ji"
    ]):

        reply = """
        👋 Hello! Welcome to <b>TransitCare</b>.<br><br>

        I'm your TransitCare Assistant. I can help you with:<br>
        📝 Reporting a transport issue<br>
        🔎 Checking complaint status<br>
        ℹ️ Understanding the complaint process<br>
        👨‍💼 Getting customer-care assistance
        """


    # ==================================================
    # STATUS CHECK
    # ==================================================

    elif any(word in message for word in [
        "status",
        "track",
        "tracking",
        "where is my complaint",
        "complaint update",
        "update on my complaint", "meri complaint ka status", "complaint ki sthiti", "complaint ki stithi", "takrarichi sthiti", "mazi takrar", "mazi takrarichi sthiti", "majhi takrar"
    ]):

        user_id = session.get("user_id")

        # User must be logged in for private complaint information
        if not user_id:

            reply = """
            🔐 To protect your complaint information,
            please log in to your TransitCare account first.<br><br>

            Once logged in, I can check your complaints
            directly from the TransitCare database.
            """

        else:

            conn = get_db()
            c = conn.cursor()

            c.execute("""
                SELECT
                    id,
                    transport_type,
                    route_number,
                    category,
                    status,
                    priority,
                    date
                FROM issues
                WHERE user_id=?
                ORDER BY id DESC
                LIMIT 5
            """, (
                user_id,
            ))

            complaints = c.fetchall()

            conn.close()

            if not complaints:

                reply = """
                🔎 I couldn't find any complaints linked
                to your account yet.<br><br>

                If you have a transport problem,
                I can guide you through reporting it.
                """

            else:

                reply = """
                🔎 <b>Here are your latest complaints:</b><br><br>
                """

                for issue in complaints:

                    reply += f"""
                    <b>Complaint #{issue['id']}</b><br>
                    🚌 {issue['transport_type']} —
                    Route {issue['route_number']}<br>
                    📌 {issue['category']}<br>
                    📊 Status:
                    <b>{issue['status']}</b><br>
                    ⚡ Priority:
                    {issue['priority']}<br>
                    📅 {issue['date']}<br><br>
                    """

    # ==================================================
    # ESCALATION
    # ==================================================

    elif any(word in message for word in [
        "not resolved",
        "unresolved",
        "still not fixed",
        "no response",
        "nobody responded",
        "escalate",
        "escalation", "shikayat badhao", "shikayat escalate", "meri complaint unresolved", "takrar escalate", "takrar vadhva", "takrar unresolved"
    ]):

        user_id = session.get("user_id")

        if not user_id:

            reply = """
            🔐 Please log in to your TransitCare account
            before requesting an escalation.
            """

        else:

            conn = get_db()
            c = conn.cursor()

            # --------------------------------------------------
            # Find the user's latest complaint
            # --------------------------------------------------

            c.execute("""
                SELECT
                    id,
                    transport_type,
                    route_number,
                    category,
                    description,
                    date,
                    priority,
                    status
                FROM issues
                WHERE user_id=?
                ORDER BY id DESC
                LIMIT 1
            """, (user_id,))

            latest_issue = c.fetchone()

            if not latest_issue:

                conn.close()

                reply = """
                🔎 I couldn't find a complaint linked to your account.
                Please register a complaint first.
                """

            else:

                issue_id = latest_issue["id"]
                issue_status = latest_issue["status"]

                # --------------------------------------------------
                # RULE 1: A resolved complaint must NEVER be
                # escalated again.
                # --------------------------------------------------

                if issue_status == "Resolved":

                    reply = f"""
                    ✅ <b>Your complaint is already resolved.</b><br><br>

                    Complaint <b>#{issue_id}</b><br>
                    🚌 {latest_issue['transport_type']} —
                    Route {latest_issue['route_number']}<br>
                    📌 {latest_issue['category']}<br>
                    📊 Status: <b>Resolved</b><br><br>

                    The authority has already marked this complaint as
                    <b>Resolved</b>. No new escalation has been created.
                    """

                    conn.close()

                else:

                    # --------------------------------------------------
                    # RULE 2: Never create duplicate escalations for
                    # the same complaint, regardless of escalation
                    # status.
                    # --------------------------------------------------

                    c.execute("""
                        SELECT id, status, created_at
                        FROM chat_escalations
                        WHERE user_id=?
                          AND issue_id=?
                        ORDER BY id DESC
                        LIMIT 1
                    """, (user_id, issue_id))

                    existing_escalation = c.fetchone()

                    if existing_escalation:

                        conn.close()

                        reply = f"""
                        🚨 <b>This complaint has already been escalated.</b><br><br>

                        Complaint: <b>#{issue_id}</b><br>
                        Escalation ID: <b>TC-{existing_escalation['id']:04d}</b><br>
                        Escalation Status: <b>{existing_escalation['status']}</b><br><br>

                        A duplicate escalation will not be created.
                        """

                    else:

                        # --------------------------------------------------
                        # RULE 3: Emergency complaints can be escalated
                        # immediately.
                        #
                        # Normal complaints must wait 10 days from the
                        # reported date before customer-care escalation.
                        # --------------------------------------------------

                        emergency_text = " ".join([
                            str(latest_issue["category"] or ""),
                            str(latest_issue["description"] or ""),
                            original_message
                        ]).lower()

                        emergency_keywords = [
                            "emergency",
                            "accident",
                            "collision",
                            "crash",
                            "injury",
                            "injured",
                            "medical",
                            "unconscious",
                            "fire",
                            "smoke",
                            "explosion",
                            "assault",
                            "violence",
                            "attack",
                            "harassment",
                            "threat",
                            "danger",
                            "unsafe",
                            "life threatening",
                            "life-threatening"
                        ]

                        is_emergency = any(
                            keyword in emergency_text
                            for keyword in emergency_keywords
                        )

                        # --------------------------------------------------
                        # Calculate how many days have passed since
                        # the complaint was reported.
                        # --------------------------------------------------

                        issue_date_text = str(latest_issue["date"] or "").strip()
                        days_since_report = 0
                        parsed_issue_date = None

                        for date_format in (
                            "%Y-%m-%d",
                            "%d-%m-%Y",
                            "%d/%m/%Y",
                            "%Y/%m/%d"
                        ):
                            try:
                                parsed_issue_date = datetime.strptime(
                                    issue_date_text,
                                    date_format
                                )
                                break
                            except ValueError:
                                pass

                        if parsed_issue_date:
                            days_since_report = (
                                datetime.now().date()
                                - parsed_issue_date.date()
                            ).days

                        # Prevent negative values if a future date
                        # somehow exists in the database.
                        days_since_report = max(0, days_since_report)

                        # --------------------------------------------------
                        # EMERGENCY → immediate escalation
                        # NORMAL → only after 10 days
                        # --------------------------------------------------

                        if is_emergency:

                            c.execute("""
                                INSERT INTO chat_escalations
                                (
                                    user_id,
                                    issue_id,
                                    reason,
                                    message,
                                    status,
                                    created_at
                                )
                                VALUES (?, ?, ?, ?, ?, ?)
                            """, (
                                user_id,
                                issue_id,
                                "Emergency issue - immediate escalation",
                                original_message,
                                "Open",
                                datetime.now().strftime(
                                    "%Y-%m-%d %H:%M:%S"
                                )
                            ))

                            escalation_id = c.lastrowid

                            conn.commit()
                            conn.close()

                            reply = f"""
                            🚨 <b>Emergency escalation created immediately.</b><br><br>

                            Complaint: <b>#{issue_id}</b><br>
                            Escalation ID: <b>TC-{escalation_id:04d}</b><br>
                            Status: <b>Open</b><br><br>

                            ⚠️ Your issue appears to be an emergency, so
                            it has been sent to customer care without waiting.
                            """

                        elif days_since_report >= 10:

                            c.execute("""
                                INSERT INTO chat_escalations
                                (
                                    user_id,
                                    issue_id,
                                    reason,
                                    message,
                                    status,
                                    created_at
                                )
                                VALUES (?, ?, ?, ?, ?, ?)
                            """, (
                                user_id,
                                issue_id,
                                "Normal issue unresolved for 10 or more days",
                                original_message,
                                "Open",
                                datetime.now().strftime(
                                    "%Y-%m-%d %H:%M:%S"
                                )
                            ))

                            escalation_id = c.lastrowid

                            conn.commit()
                            conn.close()

                            reply = f"""
                            🚨 <b>Customer-care escalation created.</b><br><br>

                            Complaint: <b>#{issue_id}</b><br>
                            Escalation ID: <b>TC-{escalation_id:04d}</b><br>
                            Status: <b>Open</b><br><br>

                            This normal complaint has been unresolved for
                            <b>{days_since_report} days</b>, so it is now eligible
                            for customer-care escalation.
                            """

                        else:

                            days_remaining = 10 - days_since_report

                            conn.close()

                            reply = f"""
                            ⏳ <b>Your complaint is still within the normal resolution period.</b><br><br>

                            Complaint: <b>#{issue_id}</b><br>
                            📊 Status: <b>{issue_status}</b><br>
                            📅 Reported: <b>{issue_date_text or 'Unknown date'}</b><br>
                            ⏱️ Days since report: <b>{days_since_report}</b><br><br>

                            Customer-care escalation for normal issues becomes
                            available after <b>10 days</b> if the complaint remains unresolved.<br><br>

                            Approximately <b>{days_remaining} day(s)</b> remain before
                            escalation becomes available.
                            """

    # ==================================================
    # REPORT COMPLAINT
    # ==================================================

    elif any(word in message for word in [
    "complaint",
    "report",
    "problem",
    "issue",
    "complain", "shikayat", "shikayaat", "takrar", "takraar", "nond", "nondva", "nondavaychi", "problem aahe", "samasya"
]) and not any(word in message for word in [
    "status",
    "track",
    "not resolved",
    "unresolved",
    "still not fixed",
    "no response",
    "nobody responded",
    "escalate",
    "escalation"
]):

        reply = """
        📝 <b>I can help you report a transport issue.</b><br><br>

        Common complaints include:<br>
        • Bus or train delays<br>
        • Cleanliness problems<br>
        • Overcrowding<br>
        • AC not working<br>
        • Staff behaviour<br>
        • Broken seats, handles or doors<br><br>

        Please open the <b>Submit Complaint</b> section
        on your TransitCare dashboard and provide the
        transport type, route number and details.
        """


    # ==================================================
    # DELAY
    # ==================================================

    elif any(word in message for word in [
        "delay",
        "late",
        "delayed", "deri", "der hua", "bus late hai", "train late hai", "ushir", "usheer", "bus ushir", "train ushir"
    ]):

        reply = """
        🚌 <b>Transport delay detected.</b><br><br>

        You can report the delay through TransitCare.<br><br>

        Please provide:<br>
        • Transport type<br>
        • Route number<br>
        • Approximate delay<br>
        • Any additional details<br><br>

        You can also upload a supporting image if useful.
        """


    # ==================================================
    # BROKEN EQUIPMENT
    # ==================================================

    elif any(word in message for word in [
        "broken",
        "seat",
        "handle",
        "door",
        "chair",
        "equipment",
        "damaged", "tooti seat", "seat tuti", "handle tutla", "darwaza tutla", "tutlela", "tootlela"
    ]):

        reply = """
        🔧 <b>This appears to be a maintenance issue.</b><br><br>

        Please report it through TransitCare with:<br>
        • Transport type<br>
        • Route number<br>
        • Description of the damage<br>
        • Photo, if possible<br><br>

        A photo can help the authority understand
        the problem more quickly.
        """


    # ==================================================
    # STAFF BEHAVIOUR
    # ==================================================

    elif any(word in message for word in [
        "conductor",
        "driver",
        "staff",
        "misbehave",
        "behaviour",
        "behavior",
        "rude",
        "abuse", "badtameezi", "staff ne badtameezi", "karmachari", "staffche vartan", "staffcha gairvartan"
    ]):

        reply = """
        ⚠️ <b>Staff behaviour complaint</b><br><br>

        You can report the incident through TransitCare.
        Please include as much factual information as possible,
        such as the transport type, route number and what happened.<br><br>

        If you need direct assistance or the situation
        cannot be resolved through the normal complaint process,
        I can help you request customer-care support.
        """


    # ==================================================
    # CUSTOMER CARE / HUMAN AGENT
    # ==================================================

    elif any(word in message for word in [
        "agent",
        "customer care",
        "customer service",
        "human",
        "representative",
        "support",
        "talk to someone", "mujhe customer care chahiye", "customer care chahiye", "agent se baat", "mala customer care pahije", "customer care pahije", "agent shi bolayche"
    ]):

        user_id = session.get("user_id")

        if not user_id:

            reply = """
            👨‍💼 <b>Customer Care</b><br><br>

            Please log in first so that customer care
            can associate your request with your account.<br><br>

            After logging in, ask me for <b>customer care</b>
            again and I can create an escalation request.
            """

        else:

            reply = """
            👨‍💼 <b>Customer Care Assistance</b><br><br>

            I can escalate an unresolved issue to
            customer care.<br><br>

            Please tell me briefly what you need help with,
            for example:<br>
            <i>"My complaint has not been resolved."</i><br>
            <i>"I need to speak to an agent."</i>
            """


   

    # ==================================================
    # THANK YOU
    # ==================================================

    elif any(word in message for word in [
        "thank",
        "thanks",
        "thankyou", "dhanyavaad", "dhanyavad", "shukriya", "thanks ji", "dhanyawad"
    ]):

        reply = """
        😊 You're welcome!

        I'm here whenever you need help with TransitCare.
        """


    # ==================================================
    # DEFAULT
    # ==================================================

    else:

        reply = """
        🤔 I'm not completely sure I understood that.<br><br>

        You can ask me things like:<br>
        • "I want to report a bus delay"<br>
        • "My seat is broken"<br>
        • "How do I complain about a conductor?"<br>
        • "Check my complaint status"<br>
        • "I need customer care"<br>
        • "My complaint is not resolved"
        """


    return jsonify({
        "reply": localize_chat_reply(reply, language),
        "language": language
    })


# --------------------------------------------------
# RUN APPLICATION
# --------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)