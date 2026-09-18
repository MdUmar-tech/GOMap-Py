#!/usr/bin/env python3
"""
Gene Ontology (GO) Annotation, Classification, and Visualization Pipeline (v1.1).
Parses InterProScan tabular output, maps OBO ontology terms, computes domain statistics,
generates publication-grade figures, and exports summary tables.
"""

import os
import re
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg') # Headless backend
import matplotlib.pyplot as plt
import seaborn as sns

# Resolve paths dynamically relative to repository root
script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(script_dir)
data_dir = os.path.join(repo_root, "data")
results_dir = os.path.join(repo_root, "results")
os.makedirs(results_dir, exist_ok=True)

tsv_path = os.path.join(data_dir, "Galaxy79-[InterProScan on dataset 78 (tsv)].tabular")
obo_path = os.path.join(data_dir, "go-basic.obo")

# --- STEP 1: PARSE OBO ONTOLOGY FILE ---
def parse_obo(file_path):
    print("Parsing go-basic.obo...")
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
            elif line.startswith("is_obsolete:") and "true" in line:
                current_term["obsolete"] = True

        if current_term and "id" in current_term:
            terms[current_term["id"]] = current_term
    print(f"Loaded {len(terms)} GO terms from OBO file.")
    return terms

terms = parse_obo(obo_path)

# --- STEP 2: EXTRACT GO ASSIGNMENTS FROM INTERPROSCAN OUTPUT ---
print("Extracting GO assignments from InterProScan tabular output...")
data_rows = []

if os.path.exists(tsv_path):
    with open(tsv_path, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 14:
                gene_id = parts[0]
                go_str = parts[13] # 14th column
                if go_str and go_str != '-':
                    go_tokens = [g.strip() for g in re.split(r'[,|]', go_str) if g.strip().startswith('GO:')]
                    for go_id in go_tokens:
                        data_rows.append({'Gene_ID': gene_id, 'GO_ID': go_id})
    df_raw = pd.DataFrame(data_rows).drop_duplicates()
else:
    # Fallback to pre-extracted data/GO_Assignment.txt if raw TSV not present
    txt_path = os.path.join(data_dir, "GO_Assignment.txt")
    print(f"Reading pre-extracted {txt_path}...")
    df_raw = pd.read_csv(txt_path, sep='\t')
    df_raw.columns = ['Gene_ID', 'GO_ID']
    df_raw = df_raw.drop_duplicates()

print(f"Extracted {len(df_raw)} unique (Gene_ID, GO_ID) pairs across {df_raw['Gene_ID'].nunique()} annotated genes.")

# Save clean GO assignment text file
assignment_txt = os.path.join(data_dir, "GO_Assignment.txt")
df_raw.to_csv(assignment_txt, sep='\t', index=False)

# --- STEP 3: MAP GO TERMS TO NAMESPACE & DESCRIPTION ---
mapped_rows = []
for _, row in df_raw.iterrows():
    gene_id = row['Gene_ID']
    go_id = row['GO_ID']
    if go_id in terms:
        t_info = terms[go_id]
        name = t_info.get("name", "Unknown")
        namespace = t_info.get("namespace", "Unknown")
        mapped_rows.append({
            'Gene_ID': gene_id,
            'GO_ID': go_id,
            'Name': name,
            'Namespace': namespace,
            'Label': f"{name} ({go_id})"
        })

df_mapped = pd.DataFrame(mapped_rows).drop_duplicates()
print(f"Successfully mapped {len(df_mapped)} GO term annotations.")

# Save mapped dataset
df_mapped.to_csv(os.path.join(results_dir, "output_1.tsv"), sep='\t', index=False)

# --- STEP 4: DOMAIN DISTRIBUTION STATISTICS ---
namespace_labels = {
    'biological_process': 'Biological Process',
    'cellular_component': 'Cellular Component',
    'molecular_function': 'Molecular Function'
}

df_mapped['Category'] = df_mapped['Namespace'].map(namespace_labels).fillna(df_mapped['Namespace'])

domain_stats = df_mapped.groupby('Category').agg(
    Annotation_Count=('GO_ID', 'count'),
    Unique_GO_Terms=('GO_ID', 'nunique'),
    Unique_Genes=('Gene_ID', 'nunique')
).reset_index()

total_annotations = domain_stats['Annotation_Count'].sum()
domain_stats['Percentage'] = (domain_stats['Annotation_Count'] / total_annotations) * 100

print("\n=== GO DOMAIN SUMMARY ===")
print(domain_stats)
domain_stats.to_csv(os.path.join(results_dir, "GO_Domain_Summary_RANM35.csv"), index=False)

# --- STEP 5: TOP 10 GO TERMS PER CATEGORY ---
term_counts = df_mapped.groupby(['Category', 'Namespace', 'GO_ID', 'Name', 'Label']).size().reset_index(name='Count')

top10_list = []
for cat_name, group in term_counts.groupby('Category'):
    top10_cat = group.sort_values(by='Count', ascending=False).head(10)
    top10_list.append(top10_cat)

df_top10 = pd.concat(top10_list, ignore_index=True)
df_top10.to_csv(os.path.join(results_dir, "GO_Top10_Per_Category_RANM35.csv"), index=False)

# --- STEP 6: PUBLICATION-GRADE PLOTS ---
sns.set_theme(style="whitegrid", font="sans-serif")
plt.rcParams.update({'font.size': 11, 'pdf.fonttype': 42})

category_colors = {
    'Biological Process': '#2ca02c',   # Green
    'Cellular Component': '#d95f02',   # Coral/Red
    'Molecular Function': '#1f77b4'    # Blue
}

# 6.1. TOP 10 GO TERMS PER CATEGORY BARPLOT
fig, ax = plt.subplots(figsize=(14, 10))
df_top10_sorted = df_top10.sort_values(by=['Category', 'Count'], ascending=[True, True])

bars = sns.barplot(
    data=df_top10_sorted,
    y="Label",
    x="Count",
    hue="Category",
    palette=category_colors,
    dodge=False,
    ax=ax
)

ax.set_xlabel("Number of Gene Annotations (Count)", fontsize=12, fontweight='bold', labelpad=10)
ax.set_ylabel("Gene Ontology Term", fontsize=12, fontweight='bold', labelpad=10)
ax.set_title("Top 10 Gene Ontology (GO) Terms per Category for Qipengyuania soli strain RANM35", fontsize=13, fontweight='bold', pad=15)

for bar in ax.patches:
    width = bar.get_width()
    if width > 0:
        ax.annotate(f'{int(width)}',
                    xy=(width, bar.get_y() + bar.get_height() / 2),
                    xytext=(5, 0),
                    textcoords="offset points",
                    ha='left', va='center', fontsize=9.5, fontweight='bold')

ax.legend(title="GO Domain Category", title_fontsize=11, frameon=True, loc='lower right', fontsize=10)
plt.tight_layout()

barplot_png = os.path.join(results_dir, "GO_Top10_Barplot_RANM35.png")
barplot_pdf = os.path.join(results_dir, "GO_Top10_Barplot_RANM35.pdf")
plt.savefig(barplot_png, dpi=300, bbox_inches='tight')
plt.savefig(barplot_pdf, bbox_inches='tight')
plt.close()
print(f"Saved Top 10 Barplot to {barplot_png}")

# 6.2. GO DOMAIN PIE CHART
fig, ax = plt.subplots(figsize=(8, 8))
wedges, texts, autotexts = ax.pie(
    domain_stats['Annotation_Count'],
    labels=domain_stats['Category'],
    autopct='%1.1f%%',
    startangle=140,
    colors=[category_colors[c] for c in domain_stats['Category']],
    wedgeprops=dict(width=0.4, edgecolor='w', linewidth=2),
    pctdistance=0.75
)

plt.setp(autotexts, size=11, weight="bold", color="white")
plt.setp(texts, size=11, weight="bold")
ax.set_title("Gene Ontology (GO) Category Distribution (Q. soli RANM35)", fontsize=13, fontweight='bold', pad=20)

plt.tight_layout()
piechart_png = os.path.join(results_dir, "GO_Domain_PieChart_RANM35.png")
piechart_pdf = os.path.join(results_dir, "GO_Domain_PieChart_RANM35.pdf")
plt.savefig(piechart_png, dpi=300, bbox_inches='tight')
plt.savefig(piechart_pdf, bbox_inches='tight')
plt.close()
print(f"Saved Domain Pie Chart to {piechart_png}")

print("\nData processing and plot generation completed successfully!")
