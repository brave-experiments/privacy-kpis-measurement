#!/usr/bin/env python3
import json
import sys

data = json.load(open(sys.argv[1], 'r'))
for third_party, tokens in data.items():
    for token, first_parties in tokens.items():
        first_party_names = list(first_parties.keys())
        num_first_parties = len(first_party_names)
        print(json.dumps([third_party, token, num_first_parties, first_party_names]))
