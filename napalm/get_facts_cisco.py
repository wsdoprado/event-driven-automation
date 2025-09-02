from napalm import get_network_driver

driver = get_network_driver("ios")
device = driver("192.168.100.31", "admin", "admin")
device.open()

print(device.get_facts())      # infos básicas
print(device.get_interfaces()) # infos de interfaces

device.close()