
import time
import re
from datetime import datetime
import subprocess
import apprise
from dotenv import load_dotenv
import os


load_dotenv()
bot_token = os.getenv('bot_token')
chat_id = os.getenv('chat_id')


def lire_journal_nouvelles_lignes(service='pvedaemon'):
    cmd = ['journalctl', '-fu', service]  # -f = suivre uniquement les nouvelles lignes
    with subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True) as proc:
        for ligne in proc.stdout:
            yield ligne.strip()


# Regex 1 : Échec d'authentification
regex_echec = re.compile(r'^(?P<date>\w+ \d+ \d+:\d+:\d+).*?authentication failure; rhost=(?P<ip>[\[\]\w\.:]+) user=(?P<user>[\w@.-]+)')

# Regex 2 : Succès OpenID
regex_succes = re.compile(r'^(?P<date>\w+ \d+ \d+:\d+:\d+).*?successful openid auth for user \'(?P<user>[\w@.-]+)\'')

def parser_ligne(ligne):
    match1 = regex_echec.match(ligne)
    match2 = regex_succes.match(ligne)

    if match1:
        d = match1.groupdict()
        return {
            "type": "echec",
            "date": d["date"],
            "ip": d["ip"],
            "user": d["user"]
        }

    elif match2:
        d = match2.groupdict()
        return {
            "type": "succes",
            "date": d["date"],
            "user": d["user"]
        }

    return None

def envoyer_telegram_apprise(message):
    apobj = apprise.Apprise()

    url = f"tgram://{bot_token}/{chat_id}"

    apobj.add(url)
    result = apobj.notify(
        body=message,
        title="--- Action detected ---"
    )

    if result:
        print("✅ Message Telegram envoyé avec Apprise.")
    else:
        print("❌ Échec de l'envoi.")


def message_maker(dictionnary):
    if dictionnary["type"] == "succes":
        message = (
            f"✅ Connexion réussie à Proxmox\n"
            f"👤 Utilisateur : {dictionnary['user']}\n"
            f"📅 Date      : {dictionnary['date']}"
        )
        return message

    elif dictionnary["type"] == "echec":
        message = (
            f"❌ Échec de connexion à Proxmox\n"
            f"👤 Utilisateur : {dictionnary['user']}\n"
            f"🌍 IP         : {dictionnary['ip']}\n"
            f"📅 Date      : {dictionnary['date']}"
        )
        return message
    return None


for connection in lire_journal_nouvelles_lignes():
    print("Nouvelle ligne :", connection)
    dic_parsed = parser_ligne(connection)
    print(dic_parsed)
    if dic_parsed:
        envoyer_telegram_apprise(message_maker(dic_parsed))


