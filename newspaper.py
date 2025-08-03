import feedparser
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Template
from dotenv import load_dotenv
import os
import urllib.request
from datetime import datetime

# Load .env variables
load_dotenv()

EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO = os.getenv("EMAIL_TO")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))

# RSS Feeds
FEEDS = {
    "BBC": "http://feeds.bbci.co.uk/news/rss.xml",
    "CHEK News": "https://www.cheknews.ca/feed/",
    "AP News": "https://news.yahoo.com/rss/ap",
    "Ars Technica": "http://feeds.arstechnica.com/arstechnica/index",
    "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
}

def fetch_headlines():
    headlines = {}
    opener = urllib.request.build_opener()
    opener.addheaders = [("User-Agent", "Mozilla/5.0")]
    urllib.request.install_opener(opener)

    for source, url in FEEDS.items():
        try:
            feed = feedparser.parse(url)
            if feed.entries:
                headlines[source] = [
                    {"title": entry.title, "link": entry.link}
                    for entry in feed.entries[:5]
                ]
            else:
                print(f"⚠️ No entries found for {source}")
        except Exception as e:
            print(f"❌ Failed to fetch {source}: {e}")
    return headlines

today = datetime.now().strftime("%A, %B %d, %Y")

HTML_TEMPLATE = f"""
<html>
  <body style="font-family: Arial, sans-serif;">
    <h2>Today's News</h2>
    <p style="color: gray;">{today}</p>
    {% for source, entries in headlines.items() %}
      <h3>{{ source }}</h3>
      <ul>
        {% for item in entries %}
          <li><a href="{{ item.link }}">{{ item.title }}</a></li>
        {% endfor %}
      </ul>
    {% endfor %}
    <p style="font-size: small; color: gray;">Sent by {{ email_from }}</p>
  </body>
</html>
"""

def send_email(html):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Your Daily News Digest"
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO

    part = MIMEText(html, 'html')
    msg.attach(part)

    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
        server.login(EMAIL_FROM, EMAIL_PASS)
        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())

def main():
    headlines = fetch_headlines()
    html = Template(HTML_TEMPLATE).render(headlines=headlines, email_from=EMAIL_FROM, today=today)
    send_email(html)

if __name__ == "__main__":
    main()
