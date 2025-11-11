**Project 3: Threat Intel Processor**/
This guide explains how to build a Python script that fetches malicious IPs from the AbuseIPDB threat feed and checks them against a sample log file.

We will create a basic Threat Intel script in Python and test it against AbuseIPDB and run checks against a sample log file.\
We will begin by heading to https://www.abuseipdb.com/account/api. Create an account if you don't have one, then click on API in the Menu or links in the middle panel. Click
on Create Key in the Create API Key section.\
<img width="596" height="246" alt="image" src="https://github.com/user-attachments/assets/9fc28535-ec07-4e23-aef7-96ef46b2ff1c" />\
Enter a Key Name, an API key will be generated which we will use in our Python script. And paste your API key in the script in 'Your_API_Key_Here' line.\
<img width="1096" height="284" alt="newKey" src="https://github.com/user-attachments/assets/d25b1764-b98d-4f9f-b294-1573c3ada5c7" />

**Installing dependencies**\ 
We will need to install `requests` module, because we have to make requests to AbuseIPDB website. Use `pip3 install requests` or `sudo apt install python3-requests`.\
To run `threatChecker.py` in terminal, use `python3 threatChecker.py`.\

**Analyze the Output**: The script will first print that it's fetching data and updating the database.\
Then, it will scan the access.log file it created. Since the threat feed is live, the exact malicious IPs will change, but you should see at least one "ALERT"\ 
message if any of the IPs in your access.log happen to be on the current AbuseIPDB blacklist.
