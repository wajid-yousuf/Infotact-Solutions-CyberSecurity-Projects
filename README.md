NIDS Rule Creation & Testing Lab
This is a detailed report on how to setup Snort, a Network Intrusion
Detection System (NIDS), VM setup and network configuration and
how to detect SSH brute-force attack with custom snort rules.
Setup & Installation:
We will install Virtualbox and setup two Virtual machines (Ubuntu
Server & Kali Linux).
Network Configuration:
Make sure that both the machines have Bridged or NAT Network
enabled. In our case we chose NAT Network and named our
network ‘Test’ for both VMs.
<img width="884" height="379" alt="image" src="https://github.com/user-attachments/assets/c82144bf-a834-44a8-a0ae-749d1a011c58" />

Installation of Snort and other tools:
On our Ubuntu machine we will install Snort and OpenSSH server by
using the following commands:
<img width="340" height="44" alt="image" src="https://github.com/user-attachments/assets/1263348b-0802-4e63-a302-848dda683b05" />
After typing this command in the terminal we will be prompted to select
a network range. Run the 'ifconfig' command.
<img width="912" height="379" alt="image" src="https://github.com/user-attachments/assets/f5e9876c-881b-42c3-a2ac-fe3fe55ba501" />

Since my IP is ‘192.168.1.9’, I will set the network range to and my network interface is 'enp0s3'
‘192.168.1.0/24’ which I intend to monitor. Also make sure to enter
name of your primary interface (e.g: enp0s3 or eth0)
We also need to install openssh-server, we will use the following
command:
<img width="410" height="40" alt="image" src="https://github.com/user-attachments/assets/7c6e106b-3c3e-4fdb-8993-0002397339f4" />

Create a Custom NIDS Rule:
To create our own custom rules we have to edit the local.rules file
located in ‘/etc/snort/rules/local.rules’, I will use nano to edit this file.
Make sure to prepend ‘sudo’ to these commands.
`alert tcp any any -> $HOME_NET 22 (msg:"SSH Brute-Force Attempt
Detected";
flow:to_server,established; detection_filter:track by_src, count 5,
seconds 60; sid:1000002;
rev:1;)` , add this command to local.rules files without quotes.
What this rule basically does is that it detects/alerts us if there have
been 5 or more connection attempts to port 22 from the same source IP2
within 60 seconds timeframe.
Explanation:
alert -> Action we want the snort to take (Generate alert in this case).
tcp -> Protocol (Applies this rule to Tcp traffic)
any any -> Source IP and Port (any means all)
$HOME_NET 22 -> Destination IP and Port (Traffic going to our
IP(HOME_NET) on port 22(SSH).
Options inside:
msg:”SSH Brute-Force Attempt Detected” -> Message that will be
displayed once the rule is triggered.
flow:to_server,established -> Match only traffic to the server side of a
connection that is already established (after TCP handshake).
detection_filter:track by_src, count 5, seconds 60 -> Trigger if the same
source IP (by_src) makes 5 or more connection attempts in 60 seconds.
sid: 10000001 -> Snort ID (unique identifier for your custom snort rule).
Always use number greater than 10000001.
rev:1 -> Revision number of the rule.
Test the Rule:
We will run snort in console mode because we want to see the alerts in
real-time:
sudo snort -A console -q -c /etc/snort/snort.conf -i enp0s3
To perform the attack from other VM or our host machine make sure
to have hydra installed: Hydra is a password cracker tool used to
simulate brute-force attacks.
On our Attacker VM, we will first create a dummy password file:
echo “pass123/npass/npassword/nqwerty/nroot” > pass.txt
Now we will run hydra using the command:
<img width="1016" height="152" alt="image" src="https://github.com/user-attachments/assets/baffa8ec-3a40-4175-9401-c7ed291e8a88" />
hydra -l non_existent_user -P pass.txt ssh://192.168.1.94
We will check our Ubuntu machine if snort was able to generate alerts:
<img width="1000" height="123" alt="image" src="https://github.com/user-attachments/assets/feb6d31c-41c2-46f9-97b2-dd6526e65708" />
As we can see we are able to successfully detect the SSH Brute-Force Attempt with Source IP as well as source Port logged in the alert message.
