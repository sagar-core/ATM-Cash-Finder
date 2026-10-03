# 🏧 ATM Cash Combination Finder (Linear Diophantine Engine)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Framework-Flask%203.1-black.svg?logo=flask)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/Database-SQLite3-003B57.svg?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Discrete Math](https://img.shields.io/badge/Math-Linear%20Diophantine%20Equations-orange.svg)]()
[![Status](https://img.shields.io/badge/Status-Complete-success.svg)]()

> A full-stack financial application combining **discrete mathematics, number theory, and modern web architecture** to model, compute, and optimize physical banknote distributions for automated teller machines.

---

## 📌 Overview

Standard ATM systems cannot rely on naive greedy dispensing when denomination quantities are limited or irregular. This project models the cash dispensing problem mathematically using **Linear Diophantine Equations** subject to hardware inventory constraints.

It computes **all feasible non-negative integer note distributions** for any requested withdrawal amount and automatically identifies the **optimal combination that minimizes the total note count** dispensed to the user.

---

## 🧮 Mathematical Modeling

### 1. Linear Diophantine Formulation
Given a withdrawal amount \(N\) and a set of \(k\) available banknote denominations \(a_1, a_2, \dots, a_k\), the dispensing logic is represented as a multivariable Linear Diophantine Equation:

$$a_1 x_1 + a_2 x_2 + \dots + a_k x_k = N$$

Where:
* \(a_i \in \mathbb{Z}^+\) represents the denomination value (e.g. ₹500, ₹200, ₹100, ₹50).
* \(x_i \in \mathbb{Z}_{\ge 0}\) represents the number of notes of denomination \(a_i\) dispensed.
* \(Q_i \in \mathbb{Z}_{\ge 0}\) represents the current inventory count of denomination \(a_i\) in the ATM.

### 2. Constraints & Bounded Search
Unlike pure Diophantine equations which allow negative integers, real-world cash dispensing requires:

$$0 \le x_i \le \min\left(Q_i, \left\lfloor \frac{N}{a_i} \right\rfloor\right), \quad \forall i \in \{1, \dots, k\}$$

### 3. Optimization Objective
Out of all valid solution sets \(S = \{(x_1, \dots, x_k) \mid \sum a_i x_i = N\}\), the engine selects the **optimal minimum-note distribution**:

$$\text{Optimal Solution} = \arg\min_{(x_1, \dots, x_k) \in S} \sum_{i=1}^k x_i$$

This reduces physical dispensing wear, prevents cassette exhaustion, and delivers a better customer experience.

---

## ✨ Features

### 👤 Customer Experience
* **Dynamic Amount Input:** Validates withdrawal requests against available cash in real-time.
* **Combinatorial Analysis:** Discovers all mathematically viable combinations of available notes.
* **Optimal Dispense Recommendation:** Automatically highlights the payout that uses the fewest total banknotes.
* **Real-time Inventory Deduction:** Atomically updates cash cassettes upon withdrawal confirmation.
* **Instant Digital Receipt:** Clear breakdown of dispensed denominations, date, time, and transaction ID.

### 🔐 Administrative Control
* **Protected Portal:** Session-based authentication with Werkzeug password hashing (`check_password_hash`).
* **Inventory Management:** View, restock, or adjust note quantities across all denominations.
* **Audit & Transaction History:** Persistent log of all completed transactions with timestamped note breakdowns.
* **Auto Initialization:** Automatically bootstraps database tables and initial stock on first launch.

---

## 🏗️ Architecture & Project Structure

```text
ATM-Cash-Finder/
├── app.py                # Core Flask backend & Diophantine search algorithm
├── requirements.txt      # Python package dependencies
├── .gitignore            # Git exclusion rules (venv, db, pycache)
├── README.md             # Project documentation & mathematical theory
├── templates/            # Jinja2 HTML templates
│   ├── index.html        # Customer home & balance preview
│   ├── withdraw.html     # Withdrawal input & live inventory
│   ├── result.html       # Solution choices & optimal recommendation
│   ├── success.html      # Transaction receipt
│   ├── admin_login.html  # Secure administrative login
│   ├── admin.html        # Admin dashboard
│   ├── manage_inventory.html # Restock denominations
│   ├── history.html      # Transaction audit log
│   └── _background.html  # Shared styling wrapper
└── static/               # CSS styles & static assets
```

---

## 🚀 Getting Started

### Prerequisites
* Python 3.10 or higher
* `pip` (Python package manager)
* `git`

### Installation & Local Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/sagar-core/ATM-Cash-Finder.git
   cd ATM-Cash-Finder
   ```

2. **Create and activate a virtual environment:**
   * **Windows (PowerShell):**
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   * **Linux / macOS:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch the application:**
   ```bash
   python app.py
   ```

5. **Open in your browser:**
   ```
   http://127.0.0.1:5000
   ```

---

## 🔑 Default Credentials (Development)

| Role | Username | Password |
| :--- | :--- | :--- |
| **Admin** | `admin` | `admin123` |

> *Note: For production deployments, change `app.secret_key` and update the admin credentials via the database.*

---

## 🛠️ Tech Stack

* **Language:** Python 3
* **Web Framework:** Flask 3.1
* **Templating Engine:** Jinja2
* **Database:** SQLite3
* **Security:** Werkzeug Cryptography (`generate_password_hash`, `check_password_hash`)
* **Frontend:** HTML5, CSS3, Flexbox/Grid

---

## 👨‍💻 Project Leadership & Author

* **Sagar P** — Project Lead & Developer
  * GitHub: [@sagar-core](https://github.com/sagar-core)
  * LinkedIn: [Sagar P](https://linkedin.com/in/sagar-p-9a7058388)
  * Institution: Atria Institute of Technology (ISE)

---

## 📄 License
This project was developed for academic, algorithmic, and practical demonstration purposes.
