import json
from rclonerc import Client

client = Client()
print(json.dumps(client.op("options/get")))
