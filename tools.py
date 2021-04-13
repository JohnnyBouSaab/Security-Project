import subprocess

# returns interfaces (names) available. None if none available
def get_interfaces():
    output = subprocess.run(['airmon-ng'])
    print(output)