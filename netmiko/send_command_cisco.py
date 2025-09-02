from netmiko import ConnectHandler

device = {
    "device_type": "cisco_ios",
    "ip": "192.168.100.31",
    "username": "admin",
    "password": "admin",
}

conn = ConnectHandler(**device)
output = conn.send_command("show version")
print(output)
conn.disconnect()