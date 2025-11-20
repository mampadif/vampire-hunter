# 🧛 Vampire Subscription Hunter

**Stop losing money to hidden subscriptions.**

Vampire Hunter is a financial utility tool built with Python and Streamlit. It securely connects to your Gmail account to audit your last 90 days of emails, identifying recurring "vampire" charges (Netflix, Adobe, Gyms, etc.) that are draining your bank account.

🔗 **Live Demo:** [https://vampire-hunter.streamlit.app](https://vampire-hunter.streamlit.app)

---

## 🚀 Features

* **Automated Audit:** Scans email subject lines and metadata for keywords like "Receipt," "Invoice," "Renew," and "Subscription."
* **Cost Calculation:** Uses Regex to extract currency amounts ($10.99, £15.00) and calculates total monthly wasted spend.
* **Visual Analytics:** Interactive charts (Plotly) showing spend by category (Streaming, Software, Food, etc.).
* **Direct Action:** Provides direct "One-Click" links to cancel or negotiate bills via services like Rocket Money and PocketGuard.

---

## 🛠️ Tech Stack

* **Python 3.9+**
* **Streamlit** (Frontend UI)
* **Google Gmail API** (OAuth 2.0 Read-Only Access)
* **Plotly** (Data Visualization)
* **Pandas** (Data Processing)

---

## 💻 Installation (Run Locally)

To run this tool on your own machine or VPS:

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/mampadif/vampire-hunter.git](https://github.com/mampadif/vampire-hunter.git)
    cd vampire-hunter
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up Google Credentials:**
    * Go to [Google Cloud Console](https://console.cloud.google.com/).
    * Create a project and enable the **Gmail API**.
    * Create an **OAuth Client ID (Desktop App)**.
    * Download the JSON file, rename it to `credentials.json`, and place it in the root folder.
    * Add your email to the "Test Users" list in the OAuth Consent Screen settings.

4.  **Run the App:**
    ```bash
    streamlit run app.py
    ```

---

## ☁️ Cloud Deployment (Streamlit Cloud)

To deploy this app publicly without exposing your API keys, we use **Headless Authentication**.

1.  **Push to GitHub:** Upload `app.py` and `requirements.txt`.
    * *⚠️ IMPORTANT: Do NOT upload `credentials.json` or `token.pickle` to GitHub.*
2.  **Connect Streamlit Cloud:** Link your GitHub repo.
3.  **Configure Secrets:**
    * Go to App Settings -> Secrets on Streamlit Cloud.
    * Add your `[google_credentials]` block (contents of your JSON file).
    * Add the `token_pickle` secret for headless login.

### How to generate the `token_pickle` Secret:
Since Cloud apps cannot open a browser window to log in, you must generate the token locally first and "transplant" it to the cloud.

1.  Run the app locally (`streamlit run app.py`) and log in via the browser once. This creates a `token.pickle` file.
2.  Run this extraction script in your terminal:
    ```python
    import pickle, base64
    # Reads your local login file and converts it to a text string
    print(base64.b64encode(open("token.pickle", "rb").read()).decode())
    ```
3.  Copy the long output string.
4.  Paste it into Streamlit Secrets like this:
    ```toml
    token_pickle = """YOUR_LONG_STRING_HERE"""
    ```

---

## 🔒 Privacy & Security

* **Local Processing:** Email data is processed in memory during the session.
* **No Database:** We do not store your emails, passwords, or financial data on any external server.
* **Read-Only:** The app uses `gmail.readonly` scope—it cannot send emails or modify your account.
* **Ephemeral:** Once you close the tab, your session data is cleared.

---

## 💰 Monetization

This tool monetizes via affiliate partnerships with financial management services. It identifies problems (wasted spend) and offers solutions:
* **Rocket Money** (Subscription Cancellation)
* **Trim** (Bill Negotiation)
* **PocketGuard** (Budgeting)

---

*Built by [Fred Mampadi]*
