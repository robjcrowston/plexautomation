import requests
import json
import shutil
import glob
import itertools
import logging

#Logging
logging.basicConfig(filename='requestterminator.log',level=logging.INFO)

#Define OMBI API Endpoint
url = "http://ombiserver/api/v1/issues"
moviedir = "/path/to/movies/"

#Define Headers incl auth
requestHeaders = {
"ApiKey": "yourapikeyhere",
"Accept": "application/json"
}

#Peform GET Request and parse the json
response = requests.get(url=url, headers=requestHeaders)
data = json.loads(response.text)

# find all unresolved and matching the issue category of 6
output_dict = [x for x in data if x['issueCategory']['id'] == 6 and x['status'] == 0]

#find the movie names amd issue IDs
rawMovieToRm = [x['title'] for x in output_dict]
movieToRm = set(rawMovieToRm)
rawIssueIds = [x['id'] for x in output_dict]
issueIds = set(rawIssueIds)
movieToRm_json = json.dumps(rawMovieToRm)
logging.info("Movies to delete: ")
logging.info(movieToRm_json)

# create list of movie paths
cleanMovies = [s.replace(':', '') for s in movieToRm]
fullpaths = []
for i in cleanMovies:
 fullpaths.append(glob.glob(moviedir + i + ' (*)'))
resultlist = list(itertools.chain.from_iterable(fullpaths))
logging.info("Matched file paths: ")
logging.info(resultlist)

# remove the files and directories
for path in resultlist:
 logging.info("Deleting: " + path + "\n"),
 shutil.rmtree(path)

# mark issues as resolved
for issue in issueIds:
  requests.post(url=url+'/status', headers=requestHeaders, json={"issueId": issue, "status": "Resolved"})
