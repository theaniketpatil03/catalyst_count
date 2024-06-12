import json

file = open("flowpath.json")
profile = json.load(file)
print(type(profile))