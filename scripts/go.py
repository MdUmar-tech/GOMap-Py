#!/usr/bin/env python3
"""
Corrected & Fixed Gene Ontology (GO) Processing and Visualization Script (go.py - v1.1).
Parses InterProScan tabular GO assignments, maps terms via go-basic.obo,
calculates domain statistics, and generates plots.
"""

import os
import re
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg') # Headless backend to prevent GUI blocking
import matplotlib.pyplot as plt
import seaborn as sns

def parse_obo(file_path):
    terms = {}
    current_term = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line == "[Term]":
                if current_term and "id" in current_term:
                    terms[current_term["id"]] = current_term
                current_term = {}
            elif line.startswith("id:"):
                current_term["id"] = line.split("id: ")[1].split()[0]
            elif line.startswith("name:"):
                current_term["name"] = line.split("name: ")[1]
            elif line.startswith("namespace:"):
                current_term["namespace"] = line.split("namespace: ")[1]
            elif line.startswith("is_a:"):
                parent = line.split("is_a: ")[1].split()[0]
                current_term.setdefault("parents", []).append(parent)
            elif line.startswith("relationship:"):
                parts = line.split(" ")
                if len(parts) >= 3 and parts[1] in ["part_of", "regulates", "negatively_regulates", "positively_regulates"]:
                    parent = parts[2]
                    current_term.setdefault("parents", []).append(parent)
        if current_term and "id" in current_term:
            terms[current_term["id"]] = current_term
    return terms

def find_related_terms(go_id, terms, visited=None):
    if visited is None:
        visited = set()
    related_ids = set()

    def get_ancestors(id_val):
        if id_val in terms and id_val not in visited:
            visited.add(id_val)
            related_ids.add(id_val)
            if "parents" in terms[id_val]:
                for parent in terms[id_val]["parents"]:
                    get_ancestors(parent)

    get_ancestors(go_id)
    return list(related_ids)

def get_level(go_id, terms):
    level = 0
    visited = set()
    curr = go_id
    while curr in terms and "parents" in terms[curr] and curr not in visited:
        visited.add(curr)
        parent_id = terms[curr]["parents"][0]
        if parent_id in terms:
            curr = parent_id
            level += 1
        else:
            break
    return level

def process_data(input_file):
    new_rows = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                parts = line.split('\t')
                id_value = parts[0]
                if id_value.lower() in ['id', 'gene_id', 'gene id']:
                    continue
                # Split GO IDs based on pipe or comma
                raw_go = parts[1] if len(parts) > 1 else ""
                go_ids = [g.strip() for g in re.split(r'[,|]', raw_go) if g.strip().startswith('GO:')]
                
                for go_id in go_ids:
                    new_rows.append({'id': id_value, 'GO_ID': go_id})
    return new_rows

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    data_dir = os.path.join(repo_root, "data")
    out_dir = os.path.join(repo_root, "results")
    os.makedirs(out_dir, exist_ok=True)

    file_path = os.path.join(data_dir, 'go-basic.obo')
    input_file_path = os.path.join(data_dir, 'GO_Assignment.txt')

    terms = parse_obo(file_path)
    processed_data = process_data(input_file_path)
    df = pd.DataFrame(processed_data)
    
    data = []
    for _, row in df.iterrows():
        gene_id = row['id']
        go_id = row['GO_ID']

        related_ids = find_related_terms(go_id, terms)
        hierarchy_data = []

        for related_id in related_ids:
            if related_id in terms:
                hierarchy_data.append((terms[related_id]["name"], related_id, terms[related_id].get("namespace", "")))

        for hierarchy, level_go_id, namespace in hierarchy_data:
            level = get_level(level_go_id, terms)
            data.append({
                "Gene ID": gene_id,
                "GO ID": go_id,
                "Hierarchy": hierarchy,
                "Level GO ID": level_go_id,
                "Level": level,
                "Class": namespace
            })

    result_df = pd.DataFrame(data)
    result_df.to_csv(os.path.join(out_dir, 'result_df.csv'), index=False)
    
    unique_go_count = result_df['Level GO ID'].nunique()
    unique_gene_id_count = result_df['Gene ID'].nunique()

    filtered_df = result_df[result_df['Level'] == 1].copy()
    unique_filtered_df = filtered_df[['Gene ID', 'Hierarchy', 'Level GO ID', 'Class']].drop_duplicates()

    grouped_df = unique_filtered_df.groupby(['Hierarchy', 'Level GO ID', 'Class']).size().reset_index(name='Counts')
    grouped_df['TotalGOid'] = unique_go_count
    grouped_df['TotalGeneAnnotated'] = unique_gene_id_count
    
    grouped_csv = os.path.join(out_dir, 'grouped_df.csv')
    grouped_df.to_csv(grouped_csv, index=False)
    
    # Class level summary text
    class_counts = grouped_df.groupby('Class')['Counts'].sum().reset_index()
    
    bp_count = class_counts.loc[class_counts['Class'] == "biological_process", 'Counts'].values[0] if "biological_process" in class_counts['Class'].values else 0
    cc_count = class_counts.loc[class_counts['Class'] == "cellular_component", 'Counts'].values[0] if "cellular_component" in class_counts['Class'].values else 0
    mf_count = class_counts.loc[class_counts['Class'] == "molecular_function", 'Counts'].values[0] if "molecular_function" in class_counts['Class'].values else 0
    total = bp_count + cc_count + mf_count

    print(f"\nTotal annotations (v1.1): {total} (Biological Process: {bp_count}, Cellular Component: {cc_count}, Molecular Function: {mf_count})")

    # Generate Horizontal Barplot
    data_plot = grouped_df.rename(columns={'Hierarchy': 'Description', 'Level GO ID': 'GOid'})
    selected_data = data_plot[['Description', 'GOid', 'Class', 'Counts']].copy()
    selected_data['Label'] = selected_data['Description'] + ' (' + selected_data['GOid'] + ')'
    sorted_data = selected_data.sort_values(by='Counts')

    sns.set_theme(style="whitegrid")
    color_palette = sns.color_palette("husl", n_colors=len(sorted_data['Class'].unique()))

    fig, ax = plt.subplots(figsize=(14, 12))
    for idx, (label_cls, label_data) in enumerate(sorted_data.groupby('Class')):
        bars = ax.barh(label_data['Label'], label_data['Counts'], color=color_palette[idx], height=0.6, label=label_cls)
        for bar in bars:
            ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height() / 2, f'{int(bar.get_width()):,}', 
                    va='center', ha='left', fontsize=10, color='black')

    ax.set_xlabel('Counts', fontsize=12, fontweight='bold')
    ax.set_ylabel('GO Terms', fontsize=12, fontweight='bold')
    ax.set_title('Gene Ontology (GO) Term Counts by Class (v1.1 Corrected Pipeline)', fontsize=13, fontweight='bold')
    ax.legend(title="GO Class", fontsize=11)
    
    plt.tight_layout()
    plot_path = os.path.join(out_dir, "go_term_counts_horizontal.png")
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved horizontal GO plot to {plot_path}")

if __name__ == "__main__":
    main()
