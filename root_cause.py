#!/usr/bin/env python
from jira import JIRA
import os
import json
from datetime import date, timedelta

# count the site
username = os.environ.get('JIRA_USER')
password = os.environ.get('JIRA_PASS')
jira_url = os.environ.get('JIRA_URL')

jira = JIRA(jira_url, basic_auth=(username, password))

query = 'project = Ops and createdDate >=-30d and "Root cause" is not EMPTY ORDER BY created DESC'

start_date = date.today() - timedelta(days=30)
print("Report for %s to %s" % (start_date, date.today()))
print("Query is", query)

causes = {}
num = 0
while True:
  query_result = jira.search_issues(query,maxResults=500,startAt=num)

  if num > query_result.total:
    break

  num += 500

  for issue in query_result:

      cause = issue.fields.customfield_14690.value
      time = issue.fields.timespent

      if time is None:
        time = 0

      if cause not in causes:
          causes[cause] = { 'count': 0, 'timespent': 0 }

      causes[cause]['count'] += 1
      causes[cause]['timespent'] += (time / 60 / 60)


print(json.dumps(causes,sort_keys=True,indent=4, separators=(',', ': ')))
