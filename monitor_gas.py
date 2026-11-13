import os
import json
import smtplib
import pandas as pd

from email.mime.text import MIMEText

CSV_URL = "https://docs.google.com/spreadsheets/d/18bzSR5JAIGhiISITbEMehDAWRVXMJqUNbqXeTmYLttM/export?format=csv&gid=325699321"

STATE_FILE = "best_offer.json"

EMAIL_USER = os.environ["EMAIL_USER"]
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]

EMAIL_TO = [
    x.strip()
    for x in os.environ["EMAIL_TO"].split(",")
]


def send_email(subject, body):

    msg = MIMEText(body)

    msg["Subject"] = subject
    msg["From"] = EMAIL_USER
    msg["To"] = ", ".join(EMAIL_TO)

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(
            EMAIL_USER,
            EMAIL_PASSWORD
        )

        server.sendmail(
            EMAIL_USER,
            EMAIL_TO,
            msg.as_string()
        )


def load_previous():

    if not os.path.exists(STATE_FILE):
        return {}

    with open(
        STATE_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def save_current(data):

    with open(
        STATE_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )


df = pd.read_csv(CSV_URL)

df["TOTALE_NUM"] = (
    df["TOTALE"]
    .astype(str)
    .str.replace("€", "", regex=False)
    .str.replace(".", "", regex=False)
    .str.replace(",", ".", regex=False)
    .str.strip()
)

df["TOTALE_NUM"] = pd.to_numeric(
    df["TOTALE_NUM"],
    errors="coerce"
)

df = df.dropna(subset=["TOTALE_NUM"])

best = df.loc[
    df["TOTALE_NUM"].idxmin()
]

current = {
    "gestore": str(best["GESTORE"]),
    "offerta": str(best["DENOMINAZIONE OFFERTA"]),
    "totale": float(best["TOTALE_NUM"]),
    "smc": str(best["PREZZO Smc"])
}

previous = load_previous()

changed = (
    previous.get("gestore")
    != current["gestore"]
    or previous.get("offerta")
    != current["offerta"]
    or previous.get("totale")
    != current["totale"]
)

if changed:

    body = f"""
NUOVA MIGLIORE OFFERTA GAS

GESTORE:
{current['gestore']}

OFFERTA:
{current['offerta']}

TOTALE:
€ {current['totale']:.2f}

PREZZO SMC:
{current['smc']}

----------------------

PRECEDENTE

{previous}
"""

    send_email(
        "Nuova migliore offerta GAS",
        body
    )

    save_current(current)

    print("EMAIL INVIATA")

else:

    print("NESSUNA VARIAZIONE")
