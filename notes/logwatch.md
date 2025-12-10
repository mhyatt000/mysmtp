Here is the **minimal, correct, practical way** to enable **daily emailed system summaries with logwatch** on Ubuntu.

This gives you:

* auth failures
* sudo usage
* ssh activity
* kernel warnings
* service errors
* cron failures
* disk space
* package updates
* and all major logs summarized

Exactly what you want.

---

# 1. **Install logwatch**

```bash
sudo apt update
sudo apt install logwatch
```

---

# 2. **Tell Ubuntu what email address to send to**

Edit the main config:

```bash
sudo nano /usr/share/logwatch/default.conf/logwatch.conf
```

Find:

```
MailTo = root
```

Change to your actual email:

```
MailTo = your_email@gmail.com
```

Optional: change subject prefix:

```
MailSubject = "Logwatch Report"
```

---

# 3. **Set `MailFrom` (optional but recommended)**

In the same config:

```
MailFrom = logwatch@$(hostname)
```

If using Gmail SMTP (via postfix or msmtp), set:

```
MailFrom = you@gmail.com
```

---

# 4. **Tell logwatch which logs and services to include**

Default config is fine, but if you want **everything**:

Find:

```
Service = All
```

If it's commented out, uncomment it.

This makes logwatch parse all known logs.

---

# 5. **Enable the daily cron job**

logwatch installs a cron entry in:

```
/etc/cron.daily/00logwatch
```

It will run automatically every day.

If you want to run it manually for testing:

```bash
sudo logwatch --detail High --range Today --mailto your_email@gmail.com --service All
```

You should receive a big email summary within ~20 seconds.

---

# 6. **Configure the system to actually send email**

logwatch *doesn't* send email itself—it calls your local MTA (mail sender).

You need one of:

### Option A: postfix (easiest all-purpose)

```bash
sudo apt install postfix
```

Choose:

```
Internet Site
```

Set:

```
System mail name: yourhostname
```

Then configure it to relay through Gmail:

Edit:

```bash
sudo nano /etc/postfix/main.cf
```

Add:

```
relayhost = [smtp.gmail.com]:587
smtp_sasl_auth_enable = yes
smtp_sasl_password_maps = hash:/etc/postfix/sasl_passwd
smtp_sasl_security_options = noanonymous
smtp_use_tls = yes
```

Then create the password file:

```
sudo nano /etc/postfix/sasl_passwd
```

Contents:

```
[smtp.gmail.com]:587 your_email@gmail.com:your_app_password
```

Secure and activate:

```bash
sudo chmod 600 /etc/postfix/sasl_passwd
sudo postmap /etc/postfix/sasl_passwd
sudo systemctl restart postfix
```

Email sending now fully works.

### Option B: msmtp (lightweight)

If you don’t want postfix, configure:

`/etc/ssmtp/ssmtp.conf` or `/etc/msmtprc`

but postfix is easier and more reliable long-term.

---

# 7. **Test that logwatch sends the full summary**

Run:

```bash
sudo /usr/sbin/logwatch --detail High --service All --range Today --mailto your_email@gmail.com
```

If you receive the email, you’re done.

Every day at ~6am, logwatch will email you fresh reports.

---

# TL;DR Table

| Step | Action                             |
| ---- | ---------------------------------- |
| 1    | install logwatch                   |
| 2    | set MailTo=your_email              |
| 3    | enable Service=All                 |
| 4    | configure an MTA (postfix easiest) |
| 5    | test with `logwatch --detail High` |

---

If you want, I can give you a **prebuilt working msmtp+logwatch config** instead of postfix, which is cleaner and works perfectly with Gmail App Passwords.

