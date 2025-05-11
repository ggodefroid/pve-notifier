pve-notifier is a python script designed for system administrators who want to receive real-time notifications on Telegram whenever an login (successful or failed) occurs on their Proxmox Webui.

The project is built around a Python script that monitors authentication logs (/var/log/auth.log) and triggers formatted messages sent through a Telegram bot. It is integrated into a systemd service to ensure reliable and automatic execution upon system startup.


# How to install
```shell
git clone https://github.com/ggodefroid/pve-notifier.git
```
Sensitive information like the bot token and chat ID are securely stored in an .env file
So you need to create the .env and add your bot key and the channel id that the bot will use. 
you can See the [Telegram documentation](https://core.telegram.org/bots/tutorial#obtain-your-bot-token) to create you own telegram bot

```shell
cd pve-notifier
cp .env.example .env
```
Install the required python packages

```shell
pip install -r requirements.txt
```
## create a systemd
create a telegram_log_auth.service in /etc/systemd/system.
```shell
vim /etc/systemd/system/telegram_log_auth.service
```

```txt
[Unit]
Description=Monitoring Webui proxmix connections and sending to Telegram
After=network.target

[Service]
ExecStart=python3 /root/pve-notifier/alerter.py
Restart=on-failure
User=root

[Install]
WantedBy=multi-user.target
```

enable the service
```shell
systemctl daemon-reload
systemctl enable telegram_log_auth
systemctl start telegram_log_auth
```


