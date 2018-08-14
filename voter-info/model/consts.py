from os import environ

HOUSE_URL = "https://api.propublica.org/congress/v1/115/house/members.json"
SENATE_URL = "https://api.propublica.org/congress/v1/115/senate/members.json"
BILL_BY_CATEGORY_URL = "https://api.propublica.org/congress/v1/bills/subjects/{subject}.json"
REPRESENTATIVE_URL = "https://www.googleapis.com/civicinfo/v2/representatives?key="
ROLL_CALL_URL = "https://api.propublica.org/congress/v1/115/bills/{bill-id}.json"
VOTE_URL = "https://api.propublica.org/congress/v1/115/{chamber}/sessions/{session-number}/votes/{roll-call-number}.json"

PROPUBLICA_KEY = environ['PROPUBLICA_CONGRESS_KEY']
CIVIC_KEY = environ['GOOGLE_CIVIC_KEY']
