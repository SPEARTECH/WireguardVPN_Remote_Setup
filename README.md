# Wireguard VPN Remote Setup
WireguardVPN Remote Setup scripts, directions, and api on server + client.

###### enable in and out networking for 51820 wireguard port for all ips and protocols
###### Set up cloud vm wireguard server conf
- $sudo apt upgrade
- $sudo apt install wireguard
###### Start interface on boot
- $ sudo systemctl enable wg-quick@wg0
###### Start wg0 now
- $sudo systemctl start wg-quick@wg0
###### Check wg0
- $sudo systemctl status wg-quick@wg0
###### Start wireguard api on server
- python -m pip install requirements.txt
- python ./wg_server.py
###### Enable wireguard api on server

