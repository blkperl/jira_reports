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

query = 'project = Ops and createdDate >=-30d and "Work Type" = Unplanned ORDER BY created DESC'

start_date = date.today() - timedelta(days=30)
print("Report for %s to %s" % (start_date, date.today()))
print("Query is", query)

issues = {}
num = 0
while True:
  query_result = jira.search_issues(query,maxResults=500,startAt=num)
  num += 500

  if num > query_result.total:
    break

  for issue in query_result:

      for link_id in issue.fields.issuelinks:
          inwardIssue = jira.issue_link(link_id).inwardIssue
          if not inwardIssue.key.startswith('OP-') and not inwardIssue.key.startswith('AM-'):
              time = jira.issue(issue.key).fields.timespent

              # skip if the OP has no time
              if time is None:
                continue

              if inwardIssue.key not in issues:
                  issues[inwardIssue.key] = { 'timespent': 0, 'summary': jira.issue(inwardIssue).fields.summary }

              issues[inwardIssue.key]['timespent'] += time / 60

print(json.dumps(issues,sort_keys=True,indent=4, separators=(',', ': ')))
