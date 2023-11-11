import json
from collections import defaultdict
from datetime import datetime
from operator import itemgetter
import sys
import os
import argparse
import requests

# read every log file in the directory
# parse the log file
# filter out logs with exceptions
# sort by timestamp
# aggregate logs by project, then by tool, picking only the latest run
# group logs by run_id
# sort groups by the first timestamp in each group
# read the template content
# placeholder for latest runs rows
# placeholder for history diagram rows
# replace placeholders in the template with actual content
# write the final HTML content to a new file


cwd = os.getcwd()
log_file_path = os.path.join(cwd, "logs")

log_files = [os.path.join(log_file_path,file) for file in os.listdir(log_file_path) if file.endswith(".log")]
logs = []

for log_file in log_files:
    # Read the log file and parse the JSON
    with open(log_file, 'r') as file:
        logs.extend([json.loads(line) for line in file])

# Filter out logs with exceptions and sort by timestamp
logs_no_exceptions = sorted(
    (log for log in logs if not log.get('exception')),
    key=itemgetter('timestamp'), reverse=True
)

# Aggregate logs by project, then by tool, picking only the latest run
latest_runs_per_project = defaultdict(dict)
for log in logs_no_exceptions:
    project = log['project']
    tool = log['tool']
    # Update the record if this tool has no entry or if the log is more recent
    if tool not in latest_runs_per_project[project]:
        latest_runs_per_project[project][tool] = log


# Placeholder for latest runs rows
latest_runs_rows = ''
for project, tools in latest_runs_per_project.items():
    for tool_log in sorted(tools.values(), key=itemgetter('timestamp'), reverse=True):
        latest_runs_rows += f"<tr><td>{tool_log['timestamp']}</td><td>{tool_log['host']}</td><td>{tool_log['commit'][0:6]}</td><td>{project}</td><td>{tool_log['tool']}</td></tr>"

# Group logs by run_id
history_by_run_id = defaultdict(list)
for log in logs:
    history_by_run_id[log['run_id']].append(log)

# Sort groups by the first timestamp in each group
sorted_history = sorted(history_by_run_id.values(), key=lambda x: x[0]['timestamp'])
sorted_history.reverse()

# Placeholder for history diagram rows
history_diagram_rows = ''
for group in sorted_history:
    timestamp = group[0]['timestamp']
    hostname = group[0]['host']
    commit = group[0]['commit'][0:6]
    project = group[0]['project']
    run_sequence = " -> ".join(log['tool'] for log in group)
    history_diagram_rows += f"<tr><td>{timestamp}</td><td>{hostname}</td><td>{commit}</td><td>{project}</td><td>{run_sequence}</td></tr>"


# Read the template content
with open('template.html', 'r') as file:
    html_template = file.read()

# Replace placeholders in the template with actual content
current_time = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
final_html_content = html_template.replace('<!-- Latest Runs Rows -->', latest_runs_rows)
final_html_content = final_html_content.replace('<!-- History Diagram Rows -->', history_diagram_rows)
final_html_content = final_html_content.replace('<!-- Log File Path -->', log_file_path)
final_html_content = final_html_content.replace('<!-- Date Created -->', current_time)

# Write the final HTML content to a new file
output_filename = 'log_report.html'
output_file_path = os.path.join(log_file_path, output_filename)
with open(output_file_path, 'w') as html_file:
    html_file.write(final_html_content)

print(f"HTML log report has been generated: {output_file_path}")
