# ☁️ Deployment Guide: Google Cloud Platform (GCP)

## Recommended VM Specifications (Google Compute Engine)

For running the full stack (FastAPI, Postgres, Redis, Next.js, Celery) reliably, here are the recommended specs:

### 1. Minimum Specs (Testing/MVP)
*   **Instance Type**: `e2-medium`
*   **CPU**: 2 vCPUs
*   **RAM**: 4 GB
*   **Storage**: 30 GB SSD (Balanced Persistent Disk)
*   **OS**: Ubuntu 22.04 LTS
*   **Cost**: ~$25-30/month (approx.)
*   *Note: You might need to enable "Swap Memory" to prevent crashes during heavy builds.*

### 2. Recommended Specs (Production)
*   **Instance Type**: `e2-standard-2`
*   **CPU**: 2 vCPUs
*   **RAM**: 8 GB
*   **Storage**: 50 GB SSD
*   **OS**: Ubuntu 22.04 LTS
*   **Cost**: ~$50-60/month (approx.)
*   *Why? Database and AI processing can consume significant RAM. 8GB ensures stability.*

---

## Deployment Steps on VM

1.  **SSH into your VM**:
    ```bash
    gcloud compute ssh --zone "your-zone" "your-instance-name"
    ```

2.  **Install Docker & Docker Compose**:
    ```bash
    # Add Docker's official GPG key:
    sudo apt-get update
    sudo apt-get install ca-certificates curl
    sudo install -m 0755 -d /etc/apt/keyrings
    sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    sudo chmod a+r /etc/apt/keyrings/docker.asc

    # Add the repository to Apt sources:
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
      $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
      sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update

    # Install Docker
    sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    ```

3.  **Clone Your Code**:
    *   Upload your code to GitHub/GitLab first, then clone it on the server.
    *   `git clone https://github.com/your-repo/lionbot.git`
    *   `cd lionbot`

4.  **Setup Environment**:
    *   Create the `.env` file in `backend/` (copy the one from your local machine).
    *   `nano backend/.env` -> Paste your keys.

5.  **Run**:
    ```bash
    sudo docker compose up -d --build
    ```

6.  **Setup Domain & SSL (Optional but Recommended)**:
    *   Point your domain (e.g., `api.lionbot.com`) to the VM's External IP.
    *   Use Nginx + Certbot for HTTPS.
