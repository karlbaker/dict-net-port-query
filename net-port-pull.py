#!/usr/bin/env python
"""
A script to find the switch (Cisco IOS) port location using an end device MAC address.
"""
import paramiko, json, time, logging, string, re
from netaddr import EUI, mac_bare, mac_cisco, mac_eui48, mac_pgsql, mac_unix
from io import StringIO
from collections import defaultdict

# Global varaibles that'll be feed in by a different application/script.
network_device = ('192.168.1.150',)
network_username = "cisco" # Move to file before putting into Production.
network_password = "cisco" # Move to file before putting into Production.


def mac_formatting(mac_address):
    mac = EUI(mac_address)
    mac.dialect = mac_cisco

    mac = str(mac)

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

def find_mac(mac_address):
    
    mac = mac_formatting(mac_address)

    d = {}                  # Empty dicionary to store network switch information.
    switchIPCount = 0       # Counter to loop through the switch IP address list.
    outputEntryCount = 0
    vlan_count = 0
    mac_count = 1
    port_count = 3
    
    while(switchIPCount < network_device.__len__()):                                            # Loop through each switch
        CMD = (connection(network_device[switchIPCount], 'show mac address-table dynamic\n'))   # Retreive a list of the port information
        d = {}                                                                                  # Create the initial dictionary to store the parsed data.
        while(outputEntryCount < CMD.__len__()):                                                # Loop through the port information list
            
            if CMD[mac_count] == mac:
                d['switch'] = [network_device[switchIPCount]]
                d['port'] = CMD[port_count]             
                d['mac'] = CMD[mac_count]  
                d['vlan'] = CMD[vlan_count]
            vlan_count = vlan_count + 4
            mac_count = mac_count + 4
            port_count = port_count + 4
            outputEntryCount = outputEntryCount + 4
        switchIPCount = switchIPCount + 1
    return d

def main():
    mac = "00:26:73:e8:e2:3c" # Change to MAC feed from server's PXE image/REST API.
    print(find_mac(mac))

if __name__ == '__main__':
    main()   