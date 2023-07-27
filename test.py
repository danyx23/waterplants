import requests
import sys
import ssl

print("Python version: ", sys.version)
print("OpenSSL version: ", ssl.OPENSSL_VERSION)
print(requests.get("https://wttr.in/Berlin?format=j1").json()["current_condition"][0]["temp_C"])