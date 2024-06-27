from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, jsonify, request
from subprocess import Popen, PIPE

from consistent_hash import ConsistantHash
from load_balancer.utils import (
    errHostnameListInconsistent,
    errInvalidRequest,
    get_container_rm_command,
    get_container_run_command,
    get_random_name,
    get_random_number,
    get_server_health,
    get_unhealty_servers,
    validateRequest,
)

import asyncio
import logging as log
import random
import requests

NETWORK_NAME = "load_balancer_network"

app = Flask(__name__)
consistant_hash = ConsistantHash()

def check_servers():
    global servers

    log.debug("Checking server health...")
    unhealthy_servers = asyncio.run(get_unhealty_servers(servers))
    print("Unhealthy servers: ", unhealthy_servers, flush=True)
    for server in unhealthy_servers:
        print(f"Removing {server}", flush=True)
        command = get_container_run_command(server, NETWORK_NAME)
        res = Popen(command, stdout=PIPE, stderr=PIPE)
        if res.returncode is not None:
            log.error(f"Error in adding {server}")
        else:
            log.info(f"Added {server}")


sched = BackgroundScheduler(daemon=True)
sched.add_job(check_servers, 'interval', seconds=30)
sched.start()

servers = {'Server_1', 'Server_2', 'Server_3'}

@app.route('/rep', methods=['GET'])
def rep():
    global servers

    healthy_servers = asyncio.run(get_server_health(servers))
    output = {
        'message': {
            'N': len(healthy_servers),
            'replicas': healthy_servers
        },
        'status': 'successful'
    }
    return jsonify(output), 200

@app.route('/add', methods=['POST'])
def add():
    global servers

    n, hostnames, err = validateRequest(request)
    if err is errInvalidRequest:
        return jsonify({
            'message': 'Error! Request payload invalid',
            'status': 'failure'
        }), 400
    if err is errHostnameListInconsistent:
        return jsonify({
            'message': 'Error! Length of hostname is more than available added instances',
            'status': 'failure'
        }), 400

    random_servers = 0
    for hostname in hostnames:
        if hostname in servers:
            log.info(f"Server {hostname} already exists")
            random_servers += 1
            continue

        command = get_container_run_command(hostname, NETWORK_NAME)
        res = Popen(command, stdout=PIPE, stderr=PIPE)
        if res.returncode is not None:
            log.error(f"Error in adding {hostname}")
        else:
            servers.add(hostname)
            consistant_hash.add_server_to_hash(hostname)
            log.info(f"Added {hostname}")

    random_servers += n - len(hostnames)
    random_servers_up = 0
    while random_servers_up < random_servers:
        server_name = get_random_name(7)
        command = get_container_run_command(server_name)
        res = Popen(command, stdout=PIPE, stderr=PIPE)
        if res.returncode is not None:
            log.error(f"Error in adding server with random name {server_name}")
        else:
            servers.add(server_name)
            consistant_hash.add_server_to_hash(server_name)
            log.info(f"Added {server_name}")
        
    output = {
        'message': {
            'N': len(servers),
            'replicas': list(servers)
        },
        'status': 'successful'
    }
    return jsonify(output), 200

@app.route('/rm', methods=['POST'])
def rm():
    global servers
    
    n, hostnames, err = validateRequest(request)
    if err is errInvalidRequest:
        return jsonify({
            'message': '<Error> Request payload in invalid format',
            'status': 'failure'
        }), 400
    if err is errHostnameListInconsistent:
        return jsonify({
            'message': '<Error> Length of hostname list is more than removable instances',
            'status': 'failure'
        }), 400
    
    random_servers = 0
    for hostname in hostnames:
        if hostname not in servers:
            log.info(f"Server {hostname} does not exist")
            random_servers += 1
            continue

        command = get_container_rm_command(hostname)
        res = Popen(command, stdout=PIPE, stderr=PIPE)
        if res.returncode is not None:
            log.error(f"Error in removing {hostname}")
        else:
            log.info(f"Removed {hostname}")
            consistant_hash.remove_server_from_hash(hostname)
            servers.remove(hostname)

    random_servers += n - len(hostnames)
    random_servers_up = 0
    while random_servers_up < random_servers:
        server_name = random.choice(servers)
        command = get_container_rm_command(server_name)
        res = Popen(command, stdout=PIPE, stderr=PIPE)
        if res.returncode is not None:
            log.error(f"Error in removing server: {server_name}")
        else:
            log.info(f"Server {server_name} Removed ")
            consistant_hash.remove_server_from_hash(server_name)
            servers.remove(server_name)

    output = {
        'message': {
            'N': len(servers),
            'replicas': list(servers)
        },
        'status': 'successful'
    }
    return jsonify(output), 200

@app.route('/<path>', methods=['GET'])
def index(path):
    global servers

    validPaths = ['index', 'shutdown']
    if path not in validPaths:
        return jsonify({}), 404
    
    if path == 'index':
        server_name = consistant_hash.get_server_from_request(get_random_number(6))
        response = requests.get(f"http://{server_name}:5000/index")
        return response.json(), response.status_code
    else: # path == 'shutdown'
        server_name = random.choice(list(servers))
        response = requests.post(f"http://{server_name}:5000/shutdown")
        return response.json(), response.status_code

if __name__ == '__main__':
    consistant_hash.build(servers)
    app.run(debug=True, host='0.0.0.0', port='5000')