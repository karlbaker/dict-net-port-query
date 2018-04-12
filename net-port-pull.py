#!/usr/bin/env python
"""
A script to list out the MAC address, network port, 
and assoicated VLAN using Paramiko
"""
import paramiko
import json
import time

def disable_paging(remote_conn):
    # Disable paging on a Cisco router

    remote_conn.send("terminal length 0\n")
    time.sleep(1)

    # Clear the buffer on the screen
    output = remote_conn.recv(1000)

    return output

if __name__ == '__main__':
    # VARIABLES THAT NEED CHANGED
    ip = '192.168.1.150'
    username = 'cisco'
    password = 'cisco'

    # Create instance of SSHClient object
    remote_conn_pre = paramiko.SSHClient()

    # Automatically add untrusted hosts (make sure okay for security policy in your environment)
    remote_conn_pre.set_missing_host_key_policy(
        paramiko.AutoAddPolicy())

    # initiate SSH connection
    remote_conn_pre.connect(ip, username=username, password=password, look_for_keys=False, allow_agent=False)
    print("SSH connection established to %s" %ip)

    # Use invoke_shell to establish an 'interactive session'
    remote_conn = remote_conn_pre.invoke_shell()
    print("Interactive SSH session established")

    # Strip the initial switch prompt
    output = remote_conn.recv(1000)

    # See what we have
    print(output)

    # Turn off paging
    disable_paging(remote_conn)

    # Now let's try pull the switch mac address table (it's going to be ugly)
    remote_conn.send("\n")
    remote_conn.send("show mac address-table dynamic\n")
    
    # Wait for the command to complete
    time.sleep(2)

    output = remote_conn.recv(5000)
    print(output)

    # Now let's try pull the port and assoicated vlans (it's going to be ugly too)
    remote_conn.send("\n")
    remote_conn.send("show int status\n")
    
    # Wait for the command to complete
    time.sleep(2)
    
    output = remote_conn.recv(5000)
    print(output)

    # Next clean up the output and place it into a json format...
