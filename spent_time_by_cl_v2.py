#!/usr/bin/env python
from __future__ import print_function

from getpass import getpass
import os
import sys

from jira import JIRA
from jira.utils import JIRAError

import click
from tabulate import tabulate

@click.command()
@click.argument("project")
def go(project):
    username = os.environ.get('JIRA_USER')
    jira_url = os.environ.get('JIRA_URL')

    # Grab the password.
    if "JIRA_PASS" in os.environ:
        password = os.environ.get("JIRA_PASS")
    else:
        password = getpass("Password for %s on JIRA instance %s: " % (username, jira_url))

    try:
        jira = JIRA(jira_url, basic_auth=(username, password))
    except JIRAError:
        print("Couldn't log in; wrong credentials?")
        sys.exit(1)

    query = """project = %s AND
               status NOT IN (Done, Rejected) AND
               createdDate >=-30d
               ORDER BY key""" % (project,)

    headers=['ISSUE','TYPE','PRIORITY','# OPS TICKETS','TOTAL TIME (hours)','CUSTOMER']

    # Secret jira jutsu: Falsy maxResults causes jira to internally auto-paginate
    # the query. Otherwise, we'd hit the limit of 500 tickets per query pretty
    # rapidly.
    query_result = jira.search_issues(query, maxResults=False)

    table = []
    with click.progressbar(query_result) as issues:
        for issue in issues:
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


if __name__ == "__main__":
    go()
