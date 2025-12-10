Yes—several solid open-source libraries already wrap SMTP, MIME building, attachments, logging, retries, queues, templates, etc.
You **should not** reinvent this unless you need something extremely custom.

Here are the ones worth using:

---

# 1. **Yagmail** (the simplest Gmail-focused SMTP wrapper)

```bash
pip install yagmail
```

Features:

* dead-simple API
* auto-handles MIME, HTML, attachments
* minimal boilerplate

Example:

```python
import yagmail

yag = yagmail.SMTP("you@gmail.com", "app-password")
yag.send("target@example.com", "subject", "body text")
```

Practical if your workflow is purely Gmail → yourself.

---

# 2. **envelope** (clean modern API)

```bash
pip install envelope
```

Example:

```python
from envelope import Envelope

Envelope()\
    .from_("me@example.com")\
    .to("you@example.com")\
    .subject("Report")\
    .message("Hello")\
    .smtp("smtp.gmail.com", 587, "me@example.com", "app-pass")\
    .send()
```

Very OOP-friendly.

---

# 3. **emails** library (full-featured, templating, attachments)

```bash
pip install emails
```

Example:

```python
import emails

msg = emails.html("Hello", subject="Report", mail_from="me@example.com")
msg.send(to="you@example.com",
         smtp={"host": "smtp.gmail.com", "port": 587,
               "user": "me@gmail.com", "password": "app-pass"})
```

Robust for templated reporting.

---

# 4. **AnyMessage / aiosmtplib** (async option)

If you want asynchronous sending or batching, use:

```bash
pip install aiosmtplib
```

---

# 5. **Existing syslog → email tools (outside Python)**

If your goal is literally “log collector → email me,” consider:

* `logwatch`
* `logrotate`’s `mail` feature
* `fail2ban` email actions
* journald `ForwardToSMTP=`

These already email periodic reports.

---

# Recommendation (your use-case)

You’re sending **reports + syslogs → yourself**, not building a general-purpose mail client.

Use **Yagmail** unless you need attachments/templates; if you do, use **emails** or **envelope**.

If you still want a lightweight OOP wrapper, I’ll sketch the class skeleton for you.

