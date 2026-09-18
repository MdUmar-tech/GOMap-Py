library(dplyr)
library(ggplot2)
library(tidyr)
# Read the tabular file
#data <- read.delim("Galaxy176-[InterProScan_on_data_174_(tsv)].tabular", sep="\t", header=FALSE)
data <- read.delim("GO_Assignment_2.txt", sep="\t", header=TRUE)

# Extract the GO IDs from column 2
#extracted_data <- data[, c(1, 14)]
extracted_data <- data[, c(1, 5)]
# Remove empty values and "-"
extracted_data <- extracted_data[extracted_data[, 2] != "" & extracted_data[, 2] != "-", ]
View(extracted_data)
#data<-distinct(data, V1, V14, .keep_all = TRUE)same as unique
#df_split <- separate_rows(df, GO, sep = "\\|")
# Separate the multiple GO values into different rows
# Make the resulting dataframe unique
#df_split_unique <- unique(df_split)
unique_data <- extracted_data %>%#skip
  separate_rows(V14, sep = "\\|")%>%unique
nrow(unique_data)
#6415
# Extract the unique GO IDs
#go_ids <- unique_data$V14
#go_ids <- unlist(unique_data[, 2])
go_ids <- unlist(extracted_data[, 2])
length(go_ids)

#num_unique_genes <- length(unique(unique_data$V1))
#2328
num_unique_genes <- length(unique(extracted_data$id))
#5931
#num_unique_GO_Term <- length(unique(unique_data$V14))
#1313
num_unique_GO_Term <- length(unique(extracted_data$GO))
View(go_ids)
# Extract the unique GO IDs and gene_ids

#gene_ids <- unique_data$V1
gene_ids <- extracted_data$id
# Read the go-basic.obo file
go_data <- readLines("go-basic.obo")

# Create an empty dataframe to store the results
result <- data.frame(Gene_ID = character(),GO_ID = character(), Name = character(), Namespace = character(), stringsAsFactors = FALSE)

# Process each line in the go-basic.obo file
for (i in 1:(length(go_data) - 1)) {
  line <- go_data[i]
  
  if (grepl("^id:", line)) {
    go_id <- strsplit(line, " ")[[1]][2]
    
    # Check if the current GO ID exists in the extracted GO IDs
    if (go_id %in% go_ids) {
      # Find the corresponding gene_id
      gene_id <- gene_ids[go_ids == go_id]
    
      # Extract the name and namespace information
      name <- ""
      namespace <- ""
      
      while (!grepl("^is_a:", go_data[i])) {
        if (grepl("^name:", go_data[i])) {
          name <- strsplit(go_data[i], "name: ")[[1]][2]
        } else if (grepl("^namespace:", go_data[i])) {
          namespace <- strsplit(go_data[i], "namespace: ")[[1]][2]
        }
        i <- i + 1
      }
      
      # Create a temporary dataframe with the extracted information
      temp_df <-data.frame(Gene_ID = gene_id,GO_ID = go_id, Name = name, Namespace = namespace, stringsAsFactors = FALSE)
      # Append the temporary dataframe to the result dataframe
      result <- rbind(result, temp_df)
      }
  }
}
# Remove rows with missing gene ID or GO ID
result <- result[complete.cases(result[c("Gene_ID", "GO_ID")]), ]
# Save the result dataframe as a TSV file
write.table(result, "output_1.tsv", sep="\t", quote=FALSE, row.names=FALSE)

#################################################################################
data<-result
View(data)
data$Name <- paste(data$Name, "(", data$GO_ID, ")", sep = "")
category_counts <- table(data$Namespace, data$Name)
View(category_counts)
print(category_counts)
# Paste the GO_ID into the Name column


# Get the top 10 categories for each namespace
top_10_molecular <- names(sort(category_counts["molecular_function", ], decreasing = TRUE))[1:10]
top_10_biological <- names(sort(category_counts["biological_process", ], decreasing = TRUE))[1:10]
top_10_cellular <- names(sort(category_counts["cellular_component", ], decreasing = TRUE))[1:10]


# Create a data frame with the category name and count
top_10_data <- data.frame(
  Category = c(top_10_molecular, top_10_biological, top_10_cellular),
  Namespace = rep(c("molecular_function", "biological_process", "cellular_component"), each = 10),
  Count = c(
    category_counts["molecular_function", top_10_molecular],
    category_counts["biological_process", top_10_biological],
    category_counts["cellular_component", top_10_cellular]
  )
)

top_10_data$Category <- factor(top_10_data$Category, levels = unique(top_10_data$Category[order(top_10_data$Namespace, top_10_data$Count)]), ordered = TRUE)
# Set the labels for each category in the 'Namespace' variable
namespaces_labels <- c(
  "molecular_function" = "Molecular Function",
  "biological_process" = "Biological Process",
  "cellular_component" = "Cellular Component"
)

ggplot(top_10_data, aes(x = Category, y = Count, fill = Namespace)) +
  geom_col(position = "dodge", width = 0.5) +
  geom_text(aes(label = Count), vjust = 0.5, hjust=0, position = position_dodge(width = 0.5)) +
  theme_bw() +
  coord_flip()+
  labs(x = "GO Term", y = "Count", fill = "GO Category")+
  scale_fill_manual(values = c(
    "molecular_function" = "blue",
    "biological_process" = "green",
    "cellular_component" = "red"
  ), labels = namespaces_labels)+
  
  theme(panel.grid.major = element_blank(), panel.grid.minor = element_blank())

ggsave("your_plot_name.png",  device = "png", width = 17, height = 10)

