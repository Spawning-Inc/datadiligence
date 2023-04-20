import datadiligence as dd
import requests


response = requests.get("https://www.google.com/image")
is_allowed = dd.is_allowed(headers=response.headers)
