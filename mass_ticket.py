#!/usr/bin/env python
from jira import JIRA
import yaml
import os

# count the site
username = os.environ.get('JIRA_USER')
password = os.environ.get('JIRA_PASS')
jira_url = os.environ.get('JIRA_URL')

jira = JIRA(jira_url, basic_auth=(username, password))


with open("patching.yml", 'r') as stream:
    tasks = yaml.load(stream)

parent = jira.issue(tasks['parent'])
print(parent.key)

for task in tasks['stages']:
    subtask_dict = {
        'project' : { 'key': 'OP' },
        'summary' : task,
        'description' : '',
        'issuetype' : { 'name' : 'Sub-task' },
        'parent' : { 'id' : parent.key},
        'components' : [{ 'id' :'12510'}], # Security
        'customfield_13692' : 'none', # sitename
        'customfield_10795' : [ { 'id' :'10717'}], # ACE
    }

    child = jira.create_issue(fields=subtask_dict)
    print(task)
