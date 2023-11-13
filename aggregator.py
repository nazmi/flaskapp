import json
import os
from collections import defaultdict
from datetime import datetime
from operator import itemgetter
logs = []
log_dir = os.path.join(os.getcwd(), 'logs')
log_file = os.path.join(log_dir, 'new branch.log')
with open(log_file, 'r') as file:
    logs.extend([json.loads(line) for line in file])

# Filter out logs with exceptions and sort by timestamp
logs_no_exceptions = sorted(
    (log for log in logs if log.get('exception') is None and log.get('exit_code') == ExitCode.SUCCESS),
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
    exit_code = group[0]['exit_code']
    run_sequence = " -> ".join(log['tool'] for log in group)
    history_diagram_rows += f"<tr><td>{timestamp}</td><td>{hostname}</td><td>{commit}</td><td>{project}</td><td>{run_sequence}</td></tr>"


# Read the template content
with open('template.html', 'r') as file:
    html_template = file.read()

# Replace placeholders in the template with actual content
current_time = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
final_html_content = html_template.replace('<!-- Latest Runs Rows -->', latest_runs_rows)
final_html_content = final_html_content.replace('<!-- History Diagram Rows -->', history_diagram_rows)
final_html_content = final_html_content.replace('<!-- Log File Path -->', log_file)
final_html_content = final_html_content.replace('<!-- Date Created -->', current_time)

# Write the final HTML content to a new file
output_file_path = os.path.join(log_dir, log_file+'.html')
with open(output_file_path, 'w') as html_file:
    html_file.write(final_html_content)

print(f"HTML log report has been generated: {output_file_path}")