git config --global credential.helper store
sudo useradd -m -G sudo sos
sudo git clone https://simplycleverlol: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@github.com/simplycleverlol/sosbot.git /home/sos/sosbot
sudo chown -R sos:sos /home/sos/sosbot
sudo locale-gen ru_RU.utf8
sudo update-locale LANG=ru_RU.UTF8
sudo apt-get update
sudo apt-get -y install python3 python3-pip python3.8-venv
sudo python3 -m venv /home/sos/sosbot/venv
sudo cp /home/sosbot.service /lib/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start sosbot.service
sudo systemctl enable sosbot.service
