import requests
import json

url = "https://api.sigfox.com/v2/devices/4D310E/messages"
payload = ''
headers = {
	"Accept": "application/json",
	"Content-Type": "application/x-www-form-urlencoded",
	"Authorization": "Basic NWRjNDY1ZjRlODMzZDk0MWY2Y2M0Y2QzOjBmMjQ1NDI0MTg2YTMxNDhjYzJkNWJiYjI0MDUwOWY5",
	"cache-control": "no-cache"
}
params = {"limit": 5}
response = requests.request("GET", url, data=payload, headers=headers, params=params)
parsed = response.json()
strings = response.text
# print(type(parsed))
print(json.dumps(parsed, indent=4))

byte_array = []
values = parsed["data"]
for val in values:
	byte_array.append(bytearray.fromhex(val["data"]))

print(byte_array)
