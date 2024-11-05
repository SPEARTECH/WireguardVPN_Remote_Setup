# WireguardVPN_Remote_Setup
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
###### Enable wg0 on server
