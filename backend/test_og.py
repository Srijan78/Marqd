import re
import requests

def test():
    url = "https://api.vxtwitter.com/ani_digital/status/2048296878845112701"
    res = requests.get(url)
    print(res.status_code)
    try:
        data = res.json()
        print("Media URLs:", data.get("mediaURLs"))
    except Exception as e:
        print("Error parsing JSON:", e)

if __name__ == "__main__":
    test()
