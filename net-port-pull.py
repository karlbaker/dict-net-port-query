#!/usr/bin/env python
"""
A script to find the switch (Cisco IOS) port location using an end device MAC address.
"""
import paramiko, json, time, logging, string, re
from netaddr import EUI, mac_bare, mac_cisco, mac_eui48, mac_pgsql, mac_unix
from io import StringIO
from collections import defaultdict

# Varaibles that'll be feed in by a different application/script.
network_device = ('192.168.1.150',)
network_username = "cisco" # Move to file before putting into Production.
network_password = "cisco" # Move to file before putting into Production.


def mac_formatting(mac_address):
    mac = EUI(mac_address)
    mac.dialect = mac_cisco

    return mac

def disable_paging(remote_conn):
    # Disable paging on a Cisco router
    remote_conn.send("terminal length 0\n")
    time.sleep(1)

    # Clear the buffer on the screen
    output = remote_conn.recv(1000)

    return output

def connection(ip, CMD):
    
    # Create instance of SSHClient object
    remote_conn_pre = paramiko.SSHClient()

    # Automatically add untrusted hosts (make sure okay for security policy in your environment)
    remote_conn_pre.set_missing_host_key_policy(
        paramiko.AutoAddPolicy())

    # initiate SSH connection
    remote_conn_pre.connect(ip, username=network_username, password=network_username, look_for_keys=False, allow_agent=False)
    #print("%s::SSH connection established" %ip)

    # Use invoke_shell to establish an 'interactive session'
    remote_conn = remote_conn_pre.invoke_shell()
    #print("Interactive SSH session established")

    # Strip the initial switch prompt
    conn_log = remote_conn.recv(1000)

    # See what we have
    #print(conn_log)

    # Turn off paging
    disable_paging(remote_conn)

    # Now let's try pull the switch mac address table (it's going to be ugly)
    remote_conn.send(CMD)
    
    # Wait for the command to complete
    time.sleep(2)

    output = remote_conn.recv(5000)
    words = output.split()

    count = 0
    while (count < 17):
        words.pop(0)
        count = count + 1

    count = 0
    while (count < 8):
        words.pop()
        count = count + 1

    return words

def main():
    mac = "00:26:73:e8:e2:3c" # Change to MAC feed from server's PXE image/REST API.
    mac = mac_formatting(mac)
    #print(connection(network_device[0], 'show mac address-table dynamic\n'))
    '''
    d = {}
    d['192.168.1.150'] = {}
    d['192.168.1.150']['FastEthenet0/0'] = {}
    d['192.168.1.150']['FastEthenet0/0']['mac'] = '00:00:00:00:00:00'
    d['192.168.1.150']['FastEthenet0/0']['vlan'] = '0'

    d['192.168.1.150']['FastEthenet0/1'] = {}
    d['192.168.1.150']['FastEthenet0/1']['mac'] = '11:11:11:11:11:11'
    d['192.168.1.150']['FastEthenet0/1']['vlan'] = '1'
    
    d['192.168.1.150']['FastEthenet0/2'] = {}
    d['192.168.1.150']['FastEthenet0/2']['mac'] = '22:22:22:22:22:22'
    d['192.168.1.150']['FastEthenet0/2']['vlan'] = '2'

    print(d)
    #print(type(connection(network_device[0], 'show mac address-table dynamic\n')))
    '''
    
    d = {}                  # Empty dicionary to store network switch information.
    switchIPCount = 0       # Counter to loop through the switch IP address list.
    outputEntryCount = 0
    vlan = 0
    mac = 1
    port = 3

    while(switchIPCount < network_device.__len__()):
        CMD = (connection(network_device[switchIPCount], 'show mac address-table dynamic\n'))
        d[network_device[switchIPCount]] = {}
        print (CMD.__len__())
        while(outputEntryCount < CMD.__len__()):
            d[network_device[switchIPCount]][CMD[port]] = {}                
            d[network_device[switchIPCount]][CMD[port]]['mac'] = CMD[mac]  
            d[network_device[switchIPCount]][CMD[port]]['vlan'] = CMD[vlan]
            outputEntryCount = outputEntryCount + 1
            #vlan = vlan + 4
            #mac = mac + 4
            #port = port + 4
        switchIPCount = switchIPCount + 1 

    print(d)
    n = json.loads(json.dumps(d))
    print (type(n))
 
if __name__ == '__main__':
    main()   