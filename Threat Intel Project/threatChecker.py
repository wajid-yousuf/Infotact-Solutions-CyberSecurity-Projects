import requests
import json
import sqlite3

API_KEY = "APIkey"
DB_FILE = 'threat_intel.db'

def setup_database():
    """Create the SQLite database and table if they don't exist"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS iocs (ip_address TEXT PRIMARY KEY, abuse_confidence INTEGER, country_code TEXT)")
    conn.commit()
    conn.close()
def fetch_threat_feed():
    """Fetch a list of malicious IPs from AbuseIPDB and store them."""
    print("Fetching latest threat intelligence...")
    headers = {'Accept': 'application/json', 'Key':API_KEY}
    params = {'limit':1000} # Fetch 1000 most recently reported IPs.

    try:
        response = requests.get('https://api.abuseipdb.com/api/v2/blacklist',headers=headers,params=params)
        response.raise_for_status()# Raise an exception for bad status codes
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data:{e}")
        return
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    count = 0

    for record in data['data']:
        # USE INSERT OR IGNORE to avoid errors on duplicate IPs
        cursor.execure("INSERT OR IGNORE INTO iocs (ip_address, abuse_confidence, country_code)" \
        "VALUES(?,?,?)," \
        "(record['ipAddress'],record)['countryCode']")
    if cursor.rowcount > 0:
        count += 1
    conn.commit()
    conn.close()
    print(f"Database updated. Addec {count} new IPs.")
def check_logs(log_file):
    """Check IPs from a log file against the threat database"""
    print(f"\nScanning log file:{log_file}...")
    conn = sqlite3.connect(DB_FILE)

    try:
        with open(log_file, 'r') as f:
            for line in f:
                # Sample example. real log parsing would be more complex
                ip = line.strip()
                cursor = conn.cursor()
                cursor.execute("SELECT ip_address, abuse_confidence FROM iocs WHERE ip_address = ?", (ip,))
                result = cursor.fetchone()

                if result:
                    print(f"[!] Alert Malicious IP found in logs: {result[0]} (Confidence: {result[1]}%)")
    except FileNotFoundError:
        print(f"Error: Log File '{log_file}' not found")
    finally:
        conn.close()
if __name__ == "__main__":
    # Setup the local database
    setup_database()
    # Fetch the latest threats and populate the database
    fetch_threat_feed()
    # Create a fake log file for demo
    with open('access.log', 'w') as f:
        f.write("192.168.1.1\n")
        f.write("185.191.171.21\n")
        f.write("8.8.8.8\n")
        f.write("206.189.123.45\n")
    check_logs('access.log')
