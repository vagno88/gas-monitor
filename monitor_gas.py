import os
import json
import smtplib
import pandas as pd

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

CSV_URL = "https://docs.google.com/spreadsheets/d/18bzSR5JAIGhiISITbEMehDAWRVXMJqUNbqXeTmYLttM/export?format=csv&gid=325699321"

STATE_FILE = "best_offer.json"

EMAIL_USER = os.environ["EMAIL_USER"]
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]

EMAIL_TO = [
    x.strip()
    for x in os.environ["EMAIL_TO"].split(",")
]


def send_email(subject, html_body):

    msg = MIMEMultipart("alternative")

    msg["Subject"] = subject
    msg["From"] = EMAIL_USER
    msg["To"] = ", ".join(EMAIL_TO)

    msg.attach(
        MIMEText(
            html_body,
            "html",
            "utf-8"
        )
    )

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

    medals = ["🥇", "🥈", "🥉"]

    cards = ""

    for idx, (_, row) in enumerate(top3.iterrows()):

        cards += f"""
        <div style="
            background:#ffffff;
            border-radius:16px;
            padding:18px;
            margin-bottom:18px;
            border:1px solid #d9d9d9;
            box-shadow:0 2px 8px rgba(0,0,0,0.08);
        ">

            <h2 style="
                margin:0;
                color:#003366;
            ">
                {medals[idx]} {row['GESTORE']}
            </h2>

            <p style="
                margin-top:6px;
                margin-bottom:16px;
                font-size:15px;
            ">
                <strong>{row['DENOMINAZIONE OFFERTA']}</strong>
            </p>

            <div style="
                background:#dff6dd;
                color:#0a6417;
                padding:15px;
                border-radius:12px;
                text-align:center;
                margin-bottom:16px;
            ">
                <div style="
                    font-size:12px;
                    font-weight:bold;
                    letter-spacing:1px;
                ">
                    PREZZO SMC
                </div>

                <div style="
                    font-size:34px;
                    font-weight:bold;
                    margin-top:4px;
                ">
                    {row['PREZZO Smc']}
                </div>
            </div>

            <table style="
                width:100%;
                border-collapse:collapse;
                font-size:14px;
            ">

                <tr>
                    <td style="padding:6px;"><b>💰 Totale</b></td>
                    <td style="padding:6px;">{row['TOTALE']}</td>
                </tr>

                <tr>
                    <td style="padding:6px;"><b>📋 QVD-CCV</b></td>
                    <td style="padding:6px;">{row['QVD - CCV']}</td>
                </tr>

                <tr>
                    <td style="padding:6px;"><b>📅 Aggiornato</b></td>
                    <td style="padding:6px;">{row['AGGIORNATO']}</td>
                </tr>

                <tr>
                    <td style="padding:6px;"><b>⏳ Validità</b></td>
                    <td style="padding:6px;">{row["VALIDITA'"]}</td>
                </tr>

                <tr>
                    <td style="padding:6px;"><b>📝 Durata</b></td>
                    <td style="padding:6px;">{row['DURATA CONTRATTO']}</td>
                </tr>

            </table>

            <div style="
                background:#f5f5f5;
                border-radius:8px;
                padding:10px;
                margin-top:12px;
                font-size:12px;
                color:#555;
            ">
                {row['NOTE']}
            </div>

        </div>
        """

    html_body = f"""
    <html>
    <body style="
        background:#f0f2f5;
        font-family:Arial,sans-serif;
        padding:20px;
        margin:0;
    ">

        <div style="
            max-width:700px;
            margin:auto;
        ">

            <h1 style="
                color:#003366;
                text-align:center;
            ">
                🏆 Nuova Migliore Offerta Gas
            </h1>

            <p style="
                text-align:center;
                color:#555;
            ">
                È stata rilevata una variazione nella classifica delle offerte gas a prezzo fisso.
            </p>

            {cards}

            <div style="
                background:#fff3cd;
                border-radius:12px;
                padding:16px;
                margin-top:20px;
                border:1px solid #ffe69c;
            ">

                <h3 style="margin-top:0;">
                    📌 Precedente Migliore Offerta
                </h3>

                <b>Gestore:</b>
                {previous.get('gestore', 'N/D')}
                <br><br>

                <b>Offerta:</b>
                {previous.get('offerta', 'N/D')}
                <br><br>

                <b>Totale:</b>
                {previous.get('totale', 'N/D')}

            </div>

        </div>

    </body>
    </html>
    """

    send_email(
        "🏆 Nuova migliore offerta GAS rilevata",
        html_body
    )

    save_current(current)

    print("EMAIL INVIATA")

else:

    print("NESSUNA VARIAZIONE")
