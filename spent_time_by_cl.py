#!/usr/bin/env python
from jira import JIRA
import os

# count the site
username = os.environ.get('JIRA_USER')
password = os.environ.get('JIRA_PASS')
jira_url = os.environ.get('JIRA_URL')

jira = JIRA(jira_url, basic_auth=(username, password))

query = 'project = CL AND status != Done and status != Rejected'

num = 0
while True:
  query_result = jira.search_issues(query,maxResults=500,startAt=num)
  num += 500

  if num > query_result.total:
    break

  for issue in query_result:
      issue_timespent = 0
      issue_count = 0

      for link_id in issue.fields.issuelinks:
          inwardIssue = jira.issue_link(link_id).inwardIssue
          if inwardIssue.key.startswith('OP-'):
              issue_count += 1
              time = jira.issue(inwardIssue.key).fields.timespent
              if time is not None:
                  issue_timespent += time

      total_time = issue_timespent / 60
      # $65 per hour for Ops
      total_money = round(total_time / 60 * 65, 2)
      if issue_timespent != 0:
          print("%s: %s minutes, %s linked tickets, %s dollars, %s" % (
              issue.key, total_time, issue_count, total_money, issue.fields.summary))
