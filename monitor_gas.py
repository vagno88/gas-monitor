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

    msg = MIMEText(body, "plain", "utf-8")

    msg["Subject"] = subject
    msg["From"] = EMAIL_USER
    msg["To"] = ", ".join(EMAIL_TO)

    with smtplib.SMTP_SSL(
        "smtp.gmail.com",
        465
    ) as server:

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


print("Download offerte...")

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

top3 = (
    df.sort_values("TOTALE_NUM")
      .head(3)
)

best = top3.iloc[0]

current = {
    "gestore": str(best["GESTORE"]),
    "offerta": str(best["DENOMINAZIONE OFFERTA"]),
    "totale": float(best["TOTALE_NUM"]),
    "smc": str(best["PREZZO Smc"])
}

previous = load_previous()

changed = (
    previous.get("gestore") != current["gestore"]
    or previous.get("offerta") != current["offerta"]
    or previous.get("totale") != current["totale"]
)

if changed:

    body = """
🏆 TOP 3 OFFERTE GAS PREZZO FISSO
=================================
"""

    for pos, (_, row) in enumerate(top3.iterrows(), start=1):

        body += f"""

==========================================
POSIZIONE #{pos}
==========================================

GESTORE
--------
{row['GESTORE']}

OFFERTA
--------
{row['DENOMINAZIONE OFFERTA']}

QVD - CCV
---------
{row['QVD - CCV']}

PREZZO SMC
----------
{row['PREZZO Smc']}

TOTALE
-------
{row['TOTALE']}

AGGIORNATO
----------
{row['AGGIORNATO']}

VALIDITA'
---------
{row["VALIDITA'"]}

NOTE
----
{row['NOTE']}

DURATA CONTRATTO
----------------
{row['DURATA CONTRATTO']}
"""

    body += f"""

==========================================
PRECEDENTE MIGLIORE OFFERTA
==========================================

GESTORE
--------
{previous.get('gestore', 'N/D')}

OFFERTA
--------
{previous.get('offerta', 'N/D')}

TOTALE
------
{previous.get('totale', 'N/D')}
"""

    send_email(
        "🏆 Nuova migliore offerta GAS rilevata",
        body
    )

    save_current(current)

    print("EMAIL INVIATA")

else:

    print("NESSUNA VARIAZIONE")
