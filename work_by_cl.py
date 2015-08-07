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

query = 'project = Ops and createdDate >=-30d ORDER BY created DESC'

start_date = date.today() - timedelta(days=30)
print("Report for %s to %s" % (start_date, date.today()))
print("Query is", query)

issues = {}
num = 0
while True:
  query_result = jira.search_issues(query,maxResults=500,startAt=num)
  num += 500

  for issue in query_result:

      for link_id in issue.fields.issuelinks:
          outwardIssue = jira.issue_link(link_id).outwardIssue
          if outwardIssue.key.startswith('CL-'):
              time = jira.issue(issue.key).fields.timespent

              if outwardIssue.key not in issues:
                  issue2 = jira.issue(outwardIssue)
                  summary = issue2.fields.summary
                  priority = issue2.fields.priority
                  issuetype = issue2.fields.issuetype
                  status = issue2.fields.status
                  issues[outwardIssue.key] = {
                      'issuecount': 0,
                      'timespent': 0,
                      'summary': str(summary),
                      'issuetype': str(issuetype),
                      'priority': str(priority),
                      'status': str(status),
                  }

              issues[outwardIssue.key]['timespent'] += time / 60 / 60
              issues[outwardIssue.key]['issuecount'] += 1

  if num > query_result.total:
    break



print(json.dumps(issues,sort_keys=True,indent=2, separators=(',', ': ')))
