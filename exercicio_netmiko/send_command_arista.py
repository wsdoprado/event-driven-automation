from netmiko import ConnectHandler

device = {
    "device_type": "arista_eos",
    "ip": "192.168.100.101",
    "username": "admin",
    "password": "admin",
}

conn = ConnectHandler(**device)
output = conn.send_command("show version")
print(output)
conn.disconnect()