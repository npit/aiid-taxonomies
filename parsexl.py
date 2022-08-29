"""
Script to parse annotation from excel sheets into a single .json
"""
import pandas as pd
import json
import sys
import numpy as np
from collections import defaultdict

x = pd.read_excel(sys.argv[1], sheet_name=None)
annotations = defaultdict(dict)
nan = np.nan

def add_classification(incident_id, row, snippet_value, task, confidence, key):
    """Dict adder """
    if task is np.nan:
        return
    idx = snippet_value

    if isinstance(idx, str):
        idxs = np.asarray([int(x)-1 for x in idx.split(",")])
        snippet = all_snippets[idxs].tolist()
    else:
        if not np.isnan(idx):
            idxs = np.expand_dims(np.asarray(int(idx)-1), 0)
            snippet = all_snippets[idxs].tolist()
        
        else:
            snippet = [] 
    # comment = row.classif_comments if isinstance(row.classif_comments, str) else ""
    comment = row.classif_comments
    annot = {"label": task, "confidence": confidence, "snippets": snippet, "comment": comment, 'report_index': row.report_num}
    if incident_id not in annotations:
        annotations[incident_id] = defaultdict(list)
    annotations[incident_id][key].append(annot)


for k, df in x.items():
    if any(v in k for v in "TEMPLATE Definitions".split()):
        continue
    print(k)
    assert df.columns.tolist() == ['Unnamed: 0', 'Unnamed: 1', 'Unnamed: 2', 'AI Tasks', 'Unnamed: 4', 'Snippet ref', 'AI Technologies', 'Unnamed: 7', 'Snippet ref.1', 'Technical Failures', 'Unnamed: 10', 'Snippet ref.2', 'Comments on classifications', 'Comments on snippents', 'Relevant snippets from incident content', 'Unnamed: 15', 'Unnamed: 16', 'Issues'], "Unexpected df structure!"

    df.rename(columns={
        'Unnamed: 0': 'url',
        'Unnamed: 1': 'year',
        'Unnamed: 2': 'description',
        'AI Tasks': 'tasks_known',
        'Unnamed: 4': 'tasks_potential',
        'Snippet ref': 'task_snippet',
        'AI Technologies': 'technologies_known',
        'Unnamed: 7': 'technologies_potential',
        'Snippet ref.1': 'tech_snippet',
       'Technical Failures': 'failures_known',
        'Unnamed: 10': 'failures_potential',
        'Snippet ref.2': 'failures_snippet',
        'Comments on classifications': 'classif_comments',
        'Comments on snippents': 'snippet_comments',
       'Relevant snippets from incident content': 'report_num',
        'Unnamed: 15': 'snippet_num',
        'Unnamed: 16': 'snippet'}, inplace=True)

    incident_id = int(k.split(" ")[1])

    all_snippets = df["snippet"].values[1:]

    for i, row in df.iterrows():
        if i == 0:
            expected = ['url', 'Incident year', 'Incident Short Description', 'Known', 'Potential', nan, 'Known', 'Potential', nan, 'Known', 'Potential', nan, nan, nan, 'Report Id / num', 'Snippet Id', 'Snippet text', nan]
            for rv, v in zip(row.values, expected):
                if not isinstance(rv, str) and np.isnan(rv):
                    assert np.isnan(v), "Nan mismatch on second row!"
                else:
                    assert rv == v, "Value mismatch on second row!"
            continue
        add_classification(incident_id, row, row.task_snippet, row.tasks_known, "known", 'task')
        add_classification(incident_id, row, row.task_snippet, row.tasks_potential, "potential", 'task')
        add_classification(incident_id, row, row.tech_snippet, row.technologies_known, 'known', 'technology')
        add_classification(incident_id, row, row.tech_snippet, row.technologies_potential, "potential", 'technology')
        add_classification(incident_id, row, row.failures_snippet, row.failures_known, 'known', 'failure')
        add_classification(incident_id, row, row.failures_snippet, row.failures_potential, "potential", 'failure')
    issues = df["Issues"].dropna().values.tolist()
    annotations[incident_id]['issues'] = issues
    if issues:
        for issue in issues:
            print("Issue:", issue)


print(f"Writing {len(annotations)} annotations.")
with open("annotations.json", 'w') as f:
    json.dump(annotations, f, indent=4)
