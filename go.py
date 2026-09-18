import pandas as pd

def parse_obo(file_path):
    terms = {}
    current_term = {}
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line == "[Term]":
                current_term = {}
            elif line.startswith("id:"):
                current_term["id"] = line.split(": ")[1]
            elif line.startswith("name:"):
                current_term["name"] = line.split(": ")[1]
            elif line.startswith("namespace:"):
                current_term["namespace"] = line.split(": ")[1]
            elif line.startswith("is_a:"):
                parent = line.split(": ")[1].split()[0]
                current_term.setdefault("parents", []).append(parent)
            elif line.startswith("relationship:"):
                parts = line.split(" ")
                rel_type = parts[1]
                if rel_type in ["part_of", "regulates", "negatively_regulates", "positively_regulates"]:
                    parent = parts[2]
                    current_term.setdefault("parents", []).append(parent)
            elif line == "":
                if "id" in current_term:
                    terms[current_term["id"]] = current_term
    return terms

def find_related_terms(go_id, terms):
    related_ids = set()

    def get_ancestors_and_descendants(id):
        if id in terms:
            related_ids.add(id)
            if "parents" in terms[id]:
                for parent in terms[id]["parents"]:
                    get_ancestors_and_descendants(parent)

    get_ancestors_and_descendants(go_id)
    return list(related_ids)

def get_level(go_id, terms):
    level = 0
    while go_id in terms and "parents" in terms[go_id]:
        parent_id = terms[go_id]["parents"][0]  # Considering a single parent for simplicity
        if parent_id in terms:
            go_id = parent_id
            level += 1
        else:
            break
    return level

def process_data(input_file):
    new_rows = []
    with open(input_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                parts = line.split('\t')
                id_value = parts[0]
                go_ids = parts[1].split(',')  # Split GO IDs based on comma
                
                for go_id in go_ids:
                    new_rows.append({'id': id_value, 'GO_ID': go_id.strip()})  # Append a new row for each GO ID
            
    return new_rows


def main():
    file_path = 'go-basic.obo'
    terms = parse_obo(file_path)

    input_file_path = 'GO_Assignment.txt'
    #input_file_path = 'tbt.txt'
    
    processed_data = process_data(input_file_path)
    #df = pd.read_csv(processed_data, delimiter='\t')

    processed_data = process_data(input_file_path)
    
    df = pd.DataFrame(processed_data)  # Create DataFrame from processed_data
    print(df)
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
                "Class": namespace  # Add the namespace to the data
            })

    result_df = pd.DataFrame(data)
    print(result_df)
    result_df.to_csv('result_df.csv', index=False)
    unique_go_count = result_df['Level GO ID'].nunique()
    unique_gene_id_count = result_df['Gene ID'].nunique()
    print(unique_go_count)
    filtered_df = result_df[result_df['Level'] == 1]
    print(filtered_df)
    #filtered_df.to_csv('result_df_level2.csv', index=False)
    #filtered_df = filtered_df.drop(columns=filtered_df.columns['GO ID', 'Level']) #or ['GO ID', 'Level']# Drop the last column ('Level')
    # Drop 'GO ID' and 'Level' columns by index
    #filtered_df = filtered_df.drop(columns=[filtered_df.columns[-4], filtered_df.columns[-1]])
    #filtered_df = filtered_df.drop(columns=[filtered_df.columns[-4], filtered_df.columns[-1]])
    #filtered_df = filtered_df.drop(filtered_df.columns[[1, 2]])#, axis=1, inplace=True
    #subset_columns = ['Gene ID', 'Hierarchy', 'Level GO ID']
    #unique_filtered_df = filtered_df.drop_duplicates()#(subset=subset_columns)
    # Drop duplicate rows based on the specified subset of columns
    filtered_df = filtered_df.drop(columns=filtered_df.columns[-2]) #or ['GO ID', 'Level']# Drop the last column ('Level')
    filtered_df = filtered_df.drop(columns=filtered_df.columns[-4]) 
    unique_filtered_df = filtered_df.drop_duplicates()
    # Assuming you have already created unique_filtered_df


    print(unique_filtered_df.columns)
    grouped_df = unique_filtered_df.groupby(['Hierarchy', 'Level GO ID', 'Class']).size().reset_index(name='Counts')
    
    grouped_df['TotalGOid'] = unique_go_count
    grouped_df['TotalGeneAnnotated'] = unique_gene_id_count
    print(grouped_df)
    grouped_df.to_csv('grouped_df.csv', index=False)
    result_df.to_csv('result_df.csv', index=False)
    print(grouped_df)
    class_counts = grouped_df.groupby('Class')['Counts'].sum().reset_index()

    # Find the counts for each class using column names
    biological_process_genes = class_counts.loc[class_counts['Class'] == "biological_process", 'Counts'].values[0]
    cellular_component_genes = class_counts.loc[class_counts['Class'] == "cellular_component", 'Counts'].values[0]
    molecular_function_genes = class_counts.loc[class_counts['Class'] == "molecular_function", 'Counts'].values[0]
    total =biological_process_genes + cellular_component_genes + molecular_function_genes
    result_text = (
        f"The presented data depicts the distribution of gene annotations among different functional categories based on Gene Ontology terms (GOIDs)."
        f"A total of {biological_process_genes + cellular_component_genes + molecular_function_genes} genes were assigned to {len(class_counts)} distinct GO term annotations, "
        f"which were then categorized into three primary domains: cellular components, biological processes, and molecular functions. "
        f"Specifically, {biological_process_genes} genes were classified as biological processes, "
        f"{cellular_component_genes} genes as cellular components, and {molecular_function_genes} genes as molecular functions." 
        f"The cumulative count of annotations across all categories amounts to {total}, indicating that some genes bear multiple annotations across diverse categories." 
        f"This underscores the intricate nature of gene functions, wherein individual genes can partake in numerous molecular activities, biological processes, or cellular locales. "
    )

    print(result_text)



if __name__ == "__main__":
    main()


import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Read the data from the file
#data = pd.read_csv("grouped_df.csv", sep="\t")
data = pd.read_csv("grouped_df.csv", sep=",")
print(data)
data = data.rename(columns={'Hierarchy': 'Description', 'Level GO ID': 'GOid'})


#data.columns = ['Description', 'GOid', 'Class', 'Counts']

print(data)
# Filter the data based on selected columns
selected_data = data[['Description', 'GOid', 'Class', 'Counts']]

# Merge GOid and Description columns
selected_data['Label'] = selected_data['Description'] + ' (' + selected_data['GOid'] + ')'

# Sort the data by Counts in increasing order
sorted_data = selected_data.sort_values(by='Counts')

# Define a color palette
color_palette = sns.color_palette("husl", n_colors=len(sorted_data['Class'].unique()))

# Create a horizontal bar plot using Matplotlib
fig, ax = plt.subplots(figsize=(16, 17))  # Increase the figure size for larger y-axis labels

# Increase the height parameter for wider bars
bar_height = 0.6  # Adjust the value to control the width of the bars
for idx, (label, label_data) in enumerate(sorted_data.groupby('Class')):
    bars = ax.barh(label_data['Label'], label_data['Counts'], color=color_palette[idx], height=bar_height, label=label)
    
    # Annotate each bar with its count value
    for bar in bars:
        ax.text(bar.get_width(), bar.get_y() + bar.get_height() / 2, f'{bar.get_width():,.0f}', 
                va='center', ha='left', fontsize=12, color='black')


# Customize the plot
ax.set_xlabel('Counts')
ax.set_ylabel('GO Terms')
ax.set_title('GO Term Counts by Class')
ax.set_xscale('log')  # Set x-axis to log scale
ax.legend()

# Adjust font size for tick labels and legend
plt.rc('xtick', labelsize=12)  # X-axis tick label font size
plt.rc('ytick', labelsize=12)  # Y-axis tick label font size
plt.rc('legend', fontsize=12)   # Legend font size

# Adjust the width of the plot
plt.subplots_adjust(left=0.2, right=0.9)  # Adjust left and right margins

plt.tight_layout()

# Save the image
plt.savefig("go_term_counts_horizontal.png")

# Show the plot
plt.show()
