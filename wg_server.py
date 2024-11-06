from flask import Flask, request, jsonify
import subprocess
import ipaddress
import re
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:8001"}})

SERVER_PUB_KEY = 'sL2AIYdeWr1FlRfW0bbU2D16d4q93/9FGPqDY4PcIV0='

## if client doesnt not have wg0.conf
#get list of wireguard clients

#create new client (wg set)

import ipaddress
import subprocess

def get_next_ip():
    # Get the current peers' allowed IPs using the `wg` command
    result = subprocess.run(['sudo', 'wg', 'show', 'wg0', 'allowed-ips'], stdout=subprocess.PIPE)
    if result.returncode != 0:
        raise Exception(f"Error getting WireGuard peers: {result.stderr}")

    # Debug: Print the raw output from wg command
    print("wg show output:", result.stdout)

    # Extract the IP addresses from the output
    allowed_ips = []
    if result.stdout:
        for line in result.stdout.splitlines():
            # Step 1: Decode the byte object to a string
                decoded_data = line.decode('utf-8')

                # Step 2: Split the string by tab ('\t') to separate the key and the IP address
                _, ip_with_subnet = decoded_data.split('\t')

                # Step 3: Further split by '/' to extract only the IP address (without the subnet)
                ip_address = ip_with_subnet.split('/')[0]
                allowed_ips.append(ip_address)

    # Debug: Print the list of allowed IPs
    print("Allowed IPs:", allowed_ips)

    # Check if allowed_ips is empty and return a default IP if necessary
    if not allowed_ips:
        return "10.10.0.2"  # Return a default IP if none are found

    # Find the highest IP and calculate the next one
    max_ip = max(ipaddress.IPv4Address(ip) for ip in allowed_ips)
    next_ip = max_ip + 1
    return str(next_ip)

print(get_next_ip())

# Generate new client keys using wg command
def generate_client_keys():
    # Generate the private key
    private_key = subprocess.check_output("wg genkey", shell=True).decode('utf-8').strip()

    # Generate the public key based on the private key
    public_key = subprocess.check_output(f"echo {private_key} | wg pubkey", shell=True).decode('utf-8').strip()

    return private_key, public_key

def read_wireguard_config():
    # Use 'sudo' to run the 'cat' command on the config file
    command = ['sudo', 'cat', '/etc/wireguard/wg0.conf']
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE)
        return result.stdout.decode('utf-8')
    except subprocess.CalledProcessError as e:
        print(f"Error reading config file: {e.stderr.decode('utf-8')}")
        return None

@app.route('/create_wireguard_client', methods=['GET'])
def create_wireguard_client():
    # get all clients

    try:
        content = read_wireguard_config()
        # with open(conf_file, 'r') as file:
        #     content = file.read()

        # Regular expression to capture PublicKey and AllowedIPs
        peer_regex = r'\[Peer\]\s*PublicKey\s*=\s*(\S+)\s*AllowedIPs\s*=\s*(\S+)'

        peers = re.findall(peer_regex, content)

        clients = {}
        client_exists = 0
        if peers:
            for i, peer in enumerate(peers, 1):
                public_key, allowed_ips = peer
                clients[i] = {'PublicKey': public_key, 'AllowedIPs': allowed_ips}
                # print(f"Client #{i}:")
                # print(f"  PublicKey: {public_key}")
                # print(f"  AllowedIPs: {allowed_ips}")
        else:
            print("No clients found.")
        # save last ip
        # print(clients)
        # last_ip = clients[len(clients)]['AllowedIPs'] #this works as long as there are some clients in the conf... there should always be the first two tested ips
        # subnet = '10.0.0.0/24'
        next_ip = get_next_ip()

        # create client
        new_client_priv_key, new_client_public_key = generate_client_keys()
        command = [
            'sudo', 'wg', 'set', 'wg0', 'peer', new_client_public_key, 'allowed-ips', next_ip+'/32'
        ]
        subprocess.run(command, stdout=subprocess.PIPE)

        # return client info - adjust locally if needed
        # Return the client configuration as a JSON response
        return jsonify({
            'status': 'success',
            "client_ip": next_ip,
            "private_key": new_client_priv_key,
            "server_pub_key": SERVER_PUB_KEY, #return server pub key
        })
    except Exception as e:
        return jsonify({
            'status': 'fail',
            'message': 'Error: '+str(e)
        })

#return client private key and server public key
@app.route('/wireguard_connect', methods=['POST'])
def wireguard_connect():
    data = request.get_json()
    client_ip = data.get('client_ip')
    client_priv_key = data.get('client_priv_key')
    client_pub_key = data.get('client_pub_key')

    # get all clients
    conf_file = "/etc/wireguard/wg0.conf"
    try:
        with open(conf_file, 'r') as file:
            content = file.read()

        # Regular expression to capture PublicKey and AllowedIPs
        peer_regex = r'\[Peer\]\s*PublicKey\s*=\s*(\S+)\s*AllowedIPs\s*=\s*(\S+)'

        peers = re.findall(peer_regex, content)

        clients = {}
        client_exists = 0
        if peers:
            for i, peer in enumerate(peers, 1):
                public_key, allowed_ips = peer
                clients[i] = {'PublicKey': public_key, 'AllowedIPs': allowed_ips}
                print(f"Client #{i}:")
                print(f"  PublicKey: {public_key}")
                print(f"  AllowedIPs: {allowed_ips}")
                # check if client exists (by ip?)
                if allowed_ips == client_ip and public_key == client_pub_key:
                    client_exists = 1
        else:
            print("No clients found.")
        # save last ip
        last_ip = clients[-1]['AllowedIPs']
        subnet = '10.0.0.0/24'
        next_ip = get_next_ip(l)

        # create client if not
        if client_exists == 0:
            # create client
            new_client_priv_key, new_client_public_key = generate_client_keys()
            command = [
                'sudo', 'wg', 'set', 'wg0', 'peer', new_client_public_key, 'allowed-ips', next_ip+'/32'
            ]
            subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # adjust client if needed on server
            # return client info - adjust locally if needed
            # return client info - adjust locally if needed
            # Return the client configuration as a JSON response
            return jsonify({
                'status': 'created',
                "client_ip": next_ip,
                "private_key": new_client_priv_key,
                "public_key": new_client_public_key,
            })
        else:
            return jsonify({
                'status': 'client exists',
                "client_ip": client_ip,
                "private_key": client_priv_key,
                "public_key": client_pub_key,
            })
    except Exception as e:
        return jsonify({
            'status': 'Error: '+e
        })

if __name__ == '__main__':
    # subprocess.run(['sudo', 'wg-quick', 'up', 'wg0'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    app.run(host='0.0.0.0', port=5000)
