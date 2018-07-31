from os import environ
import requests

REPRESENTATIVE_URL = "https://www.googleapis.com/civicinfo/v2/representatives?key="
CIVIC_KEY = environ['GOOGLE_CIVIC_KEY']
ADDRESS = "&address=" + "94588"


HOUSE_URL = "https://api.propublica.org/congress/v1/115/house/members.json"
SENATE_URL = "https://api.propublica.org/congress/v1/115/senate/members.json"
PROPUBLICA_KEY = environ['PROPUBLICA_CONGRESS_KEY']


request = requests.get(REPRESENTATIVE_URL + CIVIC_KEY + ADDRESS)
politician_json = request.json()
office_info = politician_json['offices']
politician_info = politician_json['officials']

dummy = []

office_dict = {}
for office in office_info:
    title = office['name']
    official_index = office['officialIndices']
    for index in official_index:
        office_dict[index] = title;


# [print(dum) for dum in dummy]

dummy2 = []
# for politician in politician_info:
#     name = politician['name']
#     political_party = politician['party']
#     dummy2.append()

print("YOUR OFFICIALS")
print("######################################")
for i in range(len(politician_info)):
    title = office_dict[i]
    name = politician_info[i]['name']
    dummy2.append((title, name))

[print(dum) for dum in dummy2]

print()
print()
print()
print("SENATORS")
print("######################################")
fill_senate_request = requests.get(SENATE_URL, headers={'X-API-Key': PROPUBLICA_KEY})
senate_json = fill_senate_request.json()
senate_members = senate_json["results"][0]['members']

[print((senator['title'] + " " + senator['first_name'] + " " + senator['last_name'] + " " + senator['party']))
 for senator in senate_members]

print()
print()
print()
print("REPRESENTATIVES")
print("######################################")
fill_house_request = requests.get(HOUSE_URL, headers={'X-API-Key': PROPUBLICA_KEY})
house_json = fill_house_request.json()
house_members = house_json["results"][0]['members']

[print((member['title'] + " " + member['first_name'] + " " + member['last_name'] + " " + member['party']))
 for member in house_members]








