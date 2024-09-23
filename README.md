# Bitcoin Private Key Searcher

This is a CPU-based Python script designed to search for Bitcoin private keys that match specific addresses in the **[1000 BTC Puzzle Challenge](https://privatekeys.puzzle.com/)**. The script uses elliptic curve cryptography (ECC) to generate public keys from private keys and checks if they correspond to target Bitcoin addresses. It is optimized for parallel processing using multiple CPU cores to maximize the key search rate.

## Setup Instructions

1. **Clone the repository**:
    ```bash
    git clone https://github.com/bruidbarrett/bitcoin-searcher.git
    cd bitcoin-key-searcher
    ```

2. **Set up a virtual environment (optional but recommended)**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # use 'venv\Scripts\activate' on Windows
    ```

3. **Install dependencies**:
    Install the required Python packages using `pip`:
    ```bash
    pip install -r requirements.txt
    ```

4. **Create a `.env` file**:
    Create a `.env` file in the root directory of the project to store your Discord webhook URLs. The script will use these webhooks to send status updates and alerts.
    
    Example `.env` file:
    ```env
    DISCORD_STATUS_WEBHOOK_URL=https://discord.com/api/webhooks/your_status_webhook
    DISCORD_ALERTS_WEBHOOK_URL=https://discord.com/api/webhooks/your_alerts_webhook
    ```

5. **Start the search**:
    Run the script with:
    ```bash
    python searcher.py
    ```

6. **Select challenge, cores, and optional offset**:
    When prompted, select a Bitcoin challenge from the list. You will also be asked to specify how many CPU cores to use and where in the key range to start searching.

## Features

- **Optimized Public Key Generation**: Uses efficient algorithms to convert private keys into Bitcoin addresses.
- **CPU Parallel Processing**: Leverages multiple CPU cores to divide the search range and speed up the process.
- **Discord Notifications**: Sends hourly status reports and success alerts to a Discord channel.
- **Configurable Challenges**: Allows selection of specific Bitcoin challenges from a predefined list.