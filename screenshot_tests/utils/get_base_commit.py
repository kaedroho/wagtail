import os

import requests

repo = os.environ['CI_REPO']
pr = os.environ['CI_PULL_REQUEST']
api_url = 'https://api.github.com/repos/{}/pulls/{}'.format(repo, pr)

data = requests.get(api_url).json()
print(data['base', 'sha'])
