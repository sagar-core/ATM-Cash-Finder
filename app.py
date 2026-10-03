from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

import sqlite3
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)

# Used for Flask sessions.
# Change this before putting the project on GitHub/deploying it.
app.secret_key = "change-this-secret-key"


DATABASE = "atm.db"


# ============================================================
# DATABASE
# ============================================================

def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():

    connection = get_db()
    cursor = connection.cursor()

    # ATM inventory
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            denomination INTEGER PRIMARY KEY,
            quantity INTEGER NOT NULL DEFAULT 0
        )
    """)

    # Transaction history
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount INTEGER NOT NULL,
            notes TEXT NOT NULL,
            total_notes INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Admin users
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)

    # Default ATM denominations
    default_inventory = {
        500: 3,
        200: 4,
        100: 5,
        50: 10
    }

    for denomination, quantity in default_inventory.items():

        cursor.execute("""
            INSERT OR IGNORE INTO inventory
            (denomination, quantity)
            VALUES (?, ?)
        """, (denomination, quantity))

    # Create default admin if one doesn't exist.
    admin_username = "admin"
    admin_password = "admin123"

    existing_admin = cursor.execute(
        "SELECT id FROM admins WHERE username = ?",
        (admin_username,)
    ).fetchone()

    if existing_admin is None:

        password_hash = generate_password_hash(
            admin_password
        )

        cursor.execute("""
            INSERT INTO admins
            (username, password_hash)
            VALUES (?, ?)
        """, (
            admin_username,
            password_hash
        ))

    connection.commit()
    connection.close()


# ============================================================
# ADMIN LOGIN PROTECTION
# ============================================================

def admin_required(function):

    @wraps(function)
    def decorated_function(*args, **kwargs):

        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))

        return function(*args, **kwargs)

    return decorated_function


# ============================================================
# LINEAR DIOPHANTINE EQUATION ENGINE
# ============================================================

def find_combinations(amount, denominations):

    if amount <= 0:
        return []

    available = {
        note: quantity
        for note, quantity in denominations.items()
        if quantity > 0
    }

    notes = sorted(
        available.keys(),
        reverse=True
    )

    combinations = []

    def search(
        index,
        remaining_amount,
        current_combination
    ):

        if remaining_amount == 0:

            combinations.append(
                current_combination.copy()
            )

            return

        if index >= len(notes):
            return

        note = notes[index]

        maximum_notes = min(
            available[note],
            remaining_amount // note
        )

        for count in range(
            maximum_notes,
            -1,
            -1
        ):

            if count > 0:
                current_combination[note] = count

            search(
                index + 1,
                remaining_amount - (note * count),
                current_combination
            )

            if count > 0:
                del current_combination[note]

    search(
        0,
        amount,
        {}
    )

    return combinations


def minimum_note_combination(combinations):

    if not combinations:
        return None

    return min(
        combinations,
        key=lambda combination:
        sum(combination.values())
    )


def calculate_total(combination):

    return sum(
        denomination * quantity
        for denomination, quantity
        in combination.items()
    )


def count_notes(combination):

    return sum(
        combination.values()
    )


# ============================================================
# GET CURRENT INVENTORY FROM SQLITE
# ============================================================

def get_inventory():

    connection = get_db()

    rows = connection.execute("""
        SELECT denomination, quantity
        FROM inventory
        ORDER BY denomination DESC
    """).fetchall()

    connection.close()

    return {
        row["denomination"]: row["quantity"]
        for row in rows
    }


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    inventory = get_inventory()

    return render_template(
        "index.html",
        inventory=inventory
    )


# ============================================================
# WITHDRAW
# ============================================================

@app.route(
    "/withdraw",
    methods=["GET", "POST"]
)
def withdraw():

    if request.method == "POST":

        try:
            amount = int(
                request.form["amount"]
            )

        except (
            ValueError,
            TypeError
        ):

            return "Invalid withdrawal amount.", 400

        if amount <= 0:
            return "Withdrawal amount must be greater than zero.", 400

        inventory = get_inventory()

        combinations = find_combinations(
            amount,
            inventory
        )

        best_combination = minimum_note_combination(
            combinations
        )

        return render_template(
            "result.html",
            amount=amount,
            combinations=combinations,
            best_combination=best_combination
        )

    inventory = get_inventory()

    return render_template(
        "withdraw.html",
        inventory=inventory
    )


# ============================================================
# CONFIRM WITHDRAWAL
# ============================================================

@app.route(
    "/confirm-withdrawal",
    methods=["POST"]
)
def confirm_withdrawal():

    try:
        amount = int(
            request.form["amount"]
        )

    except (
        ValueError,
        TypeError
    ):

        return "Invalid withdrawal amount.", 400

    inventory = get_inventory()

    combinations = find_combinations(
        amount,
        inventory
    )

    best_combination = minimum_note_combination(
        combinations
    )

    if not best_combination:

        return render_template(
            "result.html",
            amount=amount,
            combinations=combinations,
            best_combination=None
        )

    # Make sure the inventory hasn't changed.
    for denomination, quantity in best_combination.items():

        if quantity > inventory.get(
            denomination,
            0
        ):

            return "ATM inventory changed. Please try again.", 409

    connection = get_db()

    try:

        # Deduct notes.
        for denomination, quantity in best_combination.items():

            connection.execute("""
                UPDATE inventory
                SET quantity = quantity - ?
                WHERE denomination = ?
            """, (
                quantity,
                denomination
            ))

        # Store transaction.
        notes_text = ", ".join(
            f"{denomination}x{quantity}"
            for denomination, quantity
            in best_combination.items()
            if quantity > 0
        )

        total_notes = count_notes(
            best_combination
        )

        connection.execute("""
            INSERT INTO transactions
            (
                amount,
                notes,
                total_notes
            )
            VALUES (?, ?, ?)
        """, (
            amount,
            notes_text,
            total_notes
        ))

        connection.commit()

    except Exception:

        connection.rollback()
        connection.close()

        return "Transaction failed.", 500

    connection.close()

    return render_template(
        "success.html",
        amount=amount,
        combination=best_combination
    )


# ============================================================
# ADMIN LOGIN
# ============================================================

@app.route(
    "/admin/login",
    methods=["GET", "POST"]
)
def admin_login():

    if session.get("admin_logged_in"):
        return redirect(
            url_for("admin_dashboard")
        )

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        connection = get_db()

        admin = connection.execute("""
            SELECT *
            FROM admins
            WHERE username = ?
        """, (username,)).fetchone()

        connection.close()

        if (
            admin
            and check_password_hash(
                admin["password_hash"],
                password
            )
        ):

            session["admin_logged_in"] = True
            session["admin_username"] = username

            return redirect(
                url_for("admin_dashboard")
            )

        flash(
            "Invalid username or password."
        )

    return render_template(
        "admin_login.html"
    )


# ============================================================
# MANAGE INVENTORY
# ============================================================

@app.route(
    "/admin/inventory",
    methods=["GET", "POST"]
)
@admin_required
def manage_inventory():

    connection = get_db()

    if request.method == "POST":

        denominations = [500, 200, 100, 50]

        for denomination in denominations:

            field_name = f"quantity_{denomination}"

            try:
                quantity = int(
                    request.form.get(
                        field_name,
                        0
                    )
                )
            except (ValueError, TypeError):

                flash(
                    f"Invalid quantity for ₹{denomination}."
                )

                connection.close()

                return redirect(
                    url_for("manage_inventory")
                )

            if quantity < 0:

                flash(
                    f"Quantity for ₹{denomination} cannot be negative."
                )

                connection.close()

                return redirect(
                    url_for("manage_inventory")
                )

            connection.execute("""
                UPDATE inventory
                SET quantity = ?
                WHERE denomination = ?
            """, (
                quantity,
                denomination
            ))

        connection.commit()
        connection.close()

        flash(
            "ATM inventory updated successfully."
        )

        return redirect(
            url_for("manage_inventory")
        )

    rows = connection.execute("""
        SELECT denomination, quantity
        FROM inventory
        ORDER BY denomination DESC
    """).fetchall()

    connection.close()

    inventory = {
        row["denomination"]: row["quantity"]
        for row in rows
    }

    return render_template(
        "manage_inventory.html",
        inventory=inventory
    )

# ============================================================
# ADMIN DASHBOARD
# ============================================================

@app.route("/admin")
@admin_required
def admin_dashboard():

    inventory = get_inventory()

    return render_template(
        "admin.html",
        inventory=inventory,
        username=session.get(
            "admin_username"
        )
    )


# ============================================================
# ADMIN LOGOUT
# ============================================================

@app.route("/admin/logout")
def admin_logout():

    session.clear()

    return redirect(
        url_for("admin_login")
    )

# ============================================================
# TRANSACTION HISTORY
# ============================================================

@app.route("/history")
@admin_required
def history():

    connection = get_db()

    transactions = connection.execute("""
        SELECT
            id,
            amount,
            notes,
            total_notes,
            created_at
        FROM transactions
        ORDER BY id DESC
    """).fetchall()

    connection.close()

    return render_template(
        "history.html",
        transactions=transactions
    )


# ============================================================
# DELETE ONE TRANSACTION
# ============================================================

@app.route(
    "/admin/history/delete/<int:transaction_id>",
    methods=["POST"]
)
@admin_required
def delete_transaction(transaction_id):

    connection = get_db()

    connection.execute("""
        DELETE FROM transactions
        WHERE id = ?
    """, (transaction_id,))

    connection.commit()
    connection.close()

    flash("Transaction deleted successfully.")

    return redirect(
        url_for("history")
    )

    
# ============================================================
# START APPLICATION
# ============================================================

initialize_database()


if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0",port=5000)