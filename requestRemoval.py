# This script automatically deletes Movies and TV Shows when an OMBI user raises an issue
# matching a certain category, this gives them the ability to have items they previously
# requested removed without requiring human intervention.
# Author: Rob Crowston

import requests
import json
import shutil
import glob
import itertools
import logging

#Logging
logging.basicConfig(filename='logs/requestterminator.log',level=logging.INFO)

#Define OMBI API Endpoint
url = "http://ombiserver/api/v1/issues"
moviedir = "/path/to/Movies/"
showdir = "/path/to/TV Shows/"

#Define Headers incl auth
requestHeaders = {
"ApiKey": "thatsasecret",
"Accept": "application/json"
}

#Peform GET Request and parse the json
response = requests.get(url=url, headers=requestHeaders)
data = json.loads(response.text)

# find all unresolved and matching the issue category of 6
output_dict = [x for x in data if x['issueCategory']['id'] == 6 and x['status'] == 0]

#find the movie names and paths
movie_dict = [x for x in output_dict if x['requestType'] == 1]
rawMovieToRm = [x['title'] for x in movie_dict]
movieToRm = set(rawMovieToRm)
movieToRm_json = json.dumps(rawMovieToRm)
logging.info("Movies to delete: ")
logging.info(movieToRm_json)
cleanMovies = [s.replace(':', '') for s in movieToRm]
moviefullpaths = []
for i in cleanMovies:
 moviefullpaths.append(glob.glob(moviedir + i + ' (*)'))
movieresultlist = list(itertools.chain.from_iterable(moviefullpaths))
logging.info("Matched  Movie file paths: ")
logging.info(movieresultlist)

#find the tv show names and paths
show_dict = [x for x in output_dict if x['requestType'] == 2]
rawShowToRm = [x['title'] for x in show_dict]
showToRm = set(rawShowToRm)
showToRm_json = json.dumps(rawShowToRm)
logging.info("TV Shows to delete: ")
logging.info(showToRm_json)
cleanShows = [s.replace(':', '') for s in showToRm]
showfullpaths = []
for i in cleanShows:
 showfullpaths.append(glob.glob(showdir + i + ' (*)'))
showresultlist = list(itertools.chain.from_iterable(showfullpaths))
logging.info("Matched TV Show file paths: ")
logging.info(showresultlist)

# remove the files and directories
for showpath in showresultlist:
 logging.info("Deleting: " + showpath + "\n"),
 shutil.rmtree(showpath)
for moviepath in movieresultlist:
 logging.info("Deleting: " + moviepath + "\n"),
 shutil.rmtree(moviepath)

# mark issues as resolved
rawIssueIds = [x['id'] for x in output_dict]
issueIds = set(rawIssueIds)
for issue in issueIds:
  requests.post(url=url+'/status', headers=requestHeaders, json={"issueId": issue, "status": "Resolved"})
