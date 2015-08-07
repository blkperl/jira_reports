#!/usr/bin/env python
from jira import JIRA
import os
from tabulate import tabulate

# count the site
username = os.environ.get('JIRA_USER')
password = os.environ.get('JIRA_PASS')
jira_url = os.environ.get('JIRA_URL')

jira = JIRA(jira_url, basic_auth=(username, password))

query = 'project = CL AND status != Done and status != Rejected order by key'

headers=['ISSUE','TYPE','PRIORITY','# OPS TICKETS','TOTAL TIME (hours)','CUSTOMER']
table = []

num = 0
while True:
  query_result = jira.search_issues(query,maxResults=500,startAt=num)
  num += 500

  if num > query_result.total:
    break

  for issue in query_result:
      issue_timespent = 0
      issue_count = 0
      sites = []

      for link_id in issue.fields.issuelinks:
          inwardIssue = jira.issue_link(link_id).inwardIssue
          if inwardIssue.key.startswith('OP-'):
              issue_count += 1
              linked_issue = jira.issue(inwardIssue.key)

              # Get the linked issue timespent
              time = linked_issue.fields.timespent
              if time is not None:
                  issue_timespent += time

              # Get the linked issue sitename
              site = linked_issue.fields.customfield_13692
              if site is not None:
                sites.append(site)

      total_time = round(issue_timespent / 60 / 60, 2)
      if issue_timespent != 0:
          #table.append([issue.key,issue.fields.issuetype,issue.fields.priority,issue_count,total_time,sites])
          table.append([issue.key,issue.fields.issuetype,issue.fields.priority,issue_count,total_time])

print(tabulate(table,headers,tablefmt='pipe'))
