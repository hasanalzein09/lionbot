# 🦁 Lion Delivery BOT - Setup & Run Guide

Congratulations! The system code is ready. To make it come alive, follow these steps.

## 1. Prerequisites (What you need)

### A. API Keys
You need to obtain the following keys and add them to your `backend/.env` file (rename `.env.example` to `.env`):

1.  **OpenAI API Key**:
    *   Sign up at [platform.openai.com](https://platform.openai.com/).
    *   Create a new API Key.
    *   Set `OPENAI_API_KEY=sk-...` in `.env`.

2.  **WhatsApp Cloud API**:
    *   Go to [developers.facebook.com](https://developers.facebook.com/).
    *   Create a Business App.
    *   Add "WhatsApp" product.
    *   Get the **Temporary Access Token**, **Phone Number ID**, and **WhatsApp Business Account ID**.
    *   Set them in `.env`.
    *   **Verify Token**: Choose a random string (e.g., `lionbot_secret`) and set `WHATSAPP_VERIFY_TOKEN` in `.env`.

### B. Tools
*   **Docker Desktop**: Make sure it's installed and running.
*   **Ngrok**: Download from [ngrok.com](https://ngrok.com/). This is needed to let WhatsApp talk to your local computer.

---

## 2. Running the System

Open your terminal in the project folder (`/Users/hasanelzein/Desktop/lionbot`) and run:

```bash
docker-compose up --build
```

This will start:
*   **Backend API**: http://localhost:8000
*   **Database**: PostgreSQL
*   **Redis**: Caching & Queues

---

## 3. Connecting WhatsApp (The Magic Step)

Since the code is on your laptop, WhatsApp needs a way to reach it. We use **Ngrok**.

1.  Open a new terminal window.
2.  Run ngrok to expose port 8000:
    ```bash
    ngrok http 8000
    ```
3.  Copy the HTTPS URL generated (e.g., `https://a1b2-c3d4.ngrok-free.app`).
4.  Go to your **Meta Developers Dashboard** -> **WhatsApp** -> **Configuration**.
5.  Click **Edit** on the Webhook section.
6.  **Callback URL**: Paste your ngrok URL + `/api/v1/webhook`
    *   Example: `https://a1b2-c3d4.ngrok-free.app/api/v1/webhook`
7.  **Verify Token**: Enter the same token you put in `.env` (e.g., `lionbot_secret`).
8.  Click **Verify and Save**.
9.  Click **Manage** (Webhook fields) and subscribe to `messages`.

---

## 4. Testing

1.  Send a message to the Test Phone Number provided in the Meta Dashboard.
2.  Check the terminal where `docker-compose` is running. You should see the log!
3.  Open the **Web Dashboard** (you need to run the frontend separately for now):
    ```bash
    cd frontend
    npm run dev
    ```
    Go to `http://localhost:3000`.

4.  **Login**:
    *   Email: `admin@lionbot.com`
    *   Password: `admin123`

---

## 5. Mobile Apps

To run the mobile apps, you need an emulator (Android/iOS) or a real device connected.

```bash
cd mobile
flutter run
```

*Note: If running on a real device, you might need to update the API URL in `api_service.dart` to your computer's local IP address instead of `localhost`.*
