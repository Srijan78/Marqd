import requests
print('1. Checking Health')
print(requests.get('http://127.0.0.1:5000/api/health').json())

print('\n2. Fetching Global Propagation Data')
p = requests.get('http://127.0.0.1:5000/api/propagation')
print(p.status_code)
print(p.json())

print('\n3. Triggering Scanner')
s = requests.post('http://127.0.0.1:5000/api/scans/trigger')
print(s.status_code)

print('\n4. Fetching Violations')
v = requests.get('http://127.0.0.1:5000/api/violations')
data = v.json()
print(f"Found {len(data.get('violations', []))} violations")
print('ALL SYSTEMS GO')
