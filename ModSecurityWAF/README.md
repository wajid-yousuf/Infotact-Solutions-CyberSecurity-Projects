**Project 2: WAF Rule Development Lab**\
This guide walks you through setting up ModSecurity, a Web Application Firewall (WAF), to block a basic SQL Injection attack.\
What is ModSecurity:\
ModSecurity is an open source, cross-platform web application firewall (WAF) module. Known as the “Swiss Army Knife” of WAFs, it enables web application defenders to gain visibility into HTTP(S) traffic and provides a power rules language and API to implement advanced protections.\
Setup & Installation:\
Install Apache & ModSecurity: On Ubuntu VM we will install the Apache web server and ModSecurity module.\
<img width="670" height="147" alt="one" src="https://github.com/user-attachments/assets/882baebd-bb15-4032-85fe-57c3a6fe65ed" />\
Enable ModSecurity: Enable the module and restart Apache using following commands:\
'sudo a2enmod security2', 'sudo systemctl restart apache2'.\
Cofigure ModSecurity: Turn the engine on by editing the configuratiion file.\
'sudo nano /etc/modsecurity/modsecurity.conf-recommend'. Find the SecRule Engine DitectionOnl and change it to SecRuleEngine On.\
<img width="819" height="560" alt="two" src="https://github.com/user-attachments/assets/c17d526d-652e-4e23-afdd-0c82221f639c" />\
Deploy a Vulnearble App:\
For simplicity we'll create a single vulnerable PHP page instead of installing a complex application like DVWA.

**Install PHP:**'sudo apt install -y php libapache2-mod-php'\
<img width="818" height="212" alt="three" src="https://github.com/user-attachments/assets/352caad0-1cbb-4b40-8738-1d328cf5b624" />\
Create a vulnerable login page: Create a file at /var/www/html/login.php using the command 'sudo nano /var/www/html/login.php'.\
Paste the following PHP code into the file. This code is intentionally vulnerable.\
```
PHP
<html>
    <body>
        <h2>Login Page</h2>
        <form action="login.php" method="POST">
        Username: <input type="text" name="username"><br>
        Password: <input type="password" name="password"><br>
        <input type="Submit" value="Login">
        </form>
        <?php
            if($_SERVER["REQUEST_METHOD"]=="POST"){
            $username = $_POST['username'];
            echo "<p>Attempting login for user:" .htmlspecialchars($username)."</p>";
            }  
       ?>       
    </body>
</html>
PHP
```
<img width="748" height="286" alt="four" src="https://github.com/user-attachments/assets/d37a4081-5e92-4766-8283-3d28819eb122" />\
Create and test a WAF Rule:\
1): Create a Custom Rules File:'sudo nano /etc/apache2/conf-available/modsecurity-custom.conf'\
2): Add an SQLi Rule: Add the following rule to the file. This rule blocks any request where a POST request contains the word
UNION, a common SQLi injection keyword.
```
<IfModule security2_module>
SecRule ARGS_POST"@rx(?!)union\s+select" "id:10001,phase:2,block,msg:'SQL Injection Attempt Detected (UNION SELECT)"
</IfModule>
```
<img width="1005" height="86" alt="five" src="https://github.com/user-attachments/assets/aea803d7-b5d9-4fc0-86de-ff46ff19b7bd" />
This rule was not working so ChatGPT gave me another one.

```
<IfModule security2_module>
    SecRule ARGS_POST "@rx (?i)union\s+select" \
"id:10001,phase:2,deny,log,status:403,msg:'SQL Injection Attempt Detected (UNION SELECT)'"
</IfModule>
```
Explanation of the rule:\
Wrapper: ```<IfModule security2_module></IfModule>```: We want to keep the rule variable and operator within this wrapper.\
**The rule:**\
SecRule: The directive that defines a ModSecurity rule. It has two main parts: the variable to inspect and an operator/pattern.\
ARGS_POST: The variable collection to inspect. we intent to inspect only data sent via POST. If we want to inspect all requests we will use, ARGS_GET+POST.\
"@rx (?i)union\s+select": @rx = the regular expression operator(match using PCRE-style regex).\
(?i) = regex flag for case-insensitive matching (so UNION, union, UnIoN, etc).\
union\s+select = the regex itself:\
    -> union literal\
    -> \s+ = one or more whitespace characters (space,tab,newline)\
    -> select = literal\
So the operator matches union select with any whitespace between them, case-intensively.\
\ is the trailing backslash or we could write the whole rule on the same line.\
"id:10001 = A unique identifier for this rule. id is mandator for persistent rules. Convention: use your own range for local rules, if there are other rules using number higher that 10001.\
phase:\
phase:2 = Which processing phase the rule runs in. Modsecurity phases (common ones):\
phase:1 = request headers and URI\
phase:2 = request body (after request body has been read and parsed) - good for POST form values.\
phase:3 = response headers\
phase:4 = response body/logging\
phase:2 = is chosen because ARGS_POST (POST parameters) are available after the body is parsed.\
deny = The action, block the request. Other possible actions: pass(do nothing), allow,redirect,drop. deny will stop normal processing and return the configured status.
log = Log the transaction (to the audit log/error log depending on settings). Without log, you may block but not record details in the audit logs.\
status:403 = Return an HTTP 403 Forbidden status to the client when the rule triggers. If omitted, default behaviour for deny will apply.\
msg: 'SQL Injection Attempt Detected (UNION SELECT)'" = message that will appear in logs/audit entries describing why the request was blocked.\
What the rule does:
When ModSecurity is active, for any POST from parameter (ARGS_POST) it will:\
-> Check if the value matches the case-insensitive regex union\s+select.\
-> If matched (e.g.,test' UNION SELECT 1,2),deny the request, log details, respond with HTTP 403, and record the message SQL Injection Attempt Detected (UNION SELECT).
Enable the Custom Config:'sudo a2enconf modsecurity-custom.conf'\
Then restart the apache server for changes to take place using the command: 'sudo systemctl restart apache2'\
Test the WAF:\
-> Benign Request:\
Open a web browser and go to http://VM_IP/login.php. Enter a normal username like admin and click login. should work.\
<img width="642" height="207" alt="seven" src="https://github.com/user-attachments/assets/b43c2a16-1f91-438f-bf9f-62c879866c0d" />\
-> Attack Request: Now, enter a basic SQLi probe into the username field test'UNION SELECT 1,2,3--\
<img width="639" height="248" alt="eight" src="https://github.com/user-attachments/assets/1740461f-6fe5-4288-9574-d6d910c66a52" />\
When we enter the SQL payload we will get a 403 forbidden message:\
<img width="722" height="294" alt="twelve" src="https://github.com/user-attachments/assets/d7e36275-f160-46ed-8748-7ac36747015c" />
-> Verify the Block: When you click Login, you'll receive a 403 forbidden error from the server. The WAF has blocked your request. You can see your request. You can see the block message in Apache's error log('sudo tail /var/log/apache2/error.log').\
<img width="1282" height="639" alt="thirteen" src="https://github.com/user-attachments/assets/ff8eb571-c70f-4305-9389-dbc84a27fe26" />\
Looking at the logs we can see that it says Warning: 'Pattern Match'. And we can also see the attacker VM IP address.
We can also use 'curl'.\
<img width="735" height="182" alt="beforeFifteen" src="https://github.com/user-attachments/assets/e5332069-4ac7-4c6e-81d0-f99e93994b15" />\
And if we check the logs we can see the 'User-Agent', SQL Injection query, etc.\
<img width="1280" height="631" alt="fifteen" src="https://github.com/user-attachments/assets/805a07dc-9831-48ba-8958-cccc8d3afd05" />


