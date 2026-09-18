# GeneOntology-Pipeline (v1.1.0) 🧬📊

[![Release](https://img.shields.io/badge/Release-v1.1.0-blue.svg)](https://github.com/YOUR_USERNAME/GeneOntology_v1.1/releases/tag/v1.1.0)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-brightgreen.svg)](https://www.python.org/)

An end-to-end Python/R pipeline for parsing **InterProScan** tabular protein annotations, resolving **Gene Ontology Consortium** (`go-basic.obo`) hierarchical terms, calculating domain distributions across **Biological Process**, **Cellular Component**, and **Molecular Function**, generating publication-ready high-resolution plots, and producing automated MS Word manuscript reports (`.docx`).

---

## 🌟 Major Enhancements in v1.1.0 (vs v1.0.0)

| Feature | Version 1.0.0 (Original) | Version 1.1.0 (Release Submission) |
| :--- | :--- | :--- |
| **Directory Structure** | Flat directory with mixed scripts & outputs | Modular standard structure (`scripts/`, `data/`, `results/`) |
| **Pipeline Runner** | Manual multi-step script invocations | Single master executable shell script (`run_pipeline.sh`) |
| **GO Term Delimiter** | Comma `,` only (missed multi-GO terms) | Both pipe `\|` & comma `,` (InterProScan standard) |
| **Data Parsing** | Hardcoded negative column indices | Named column selection & header cleaning |
| **Execution Mode** | GUI-blocking (`plt.show()`) | Headless backend (`matplotlib.use('Agg')`) |
| **Report Generation** | Manual text output | Automated MS Word (`.docx`) manuscript generator |
| **Visualization** | Single basic barplot | High-res PNG & PDF barplots, pie charts & horizontal plots |

---

## 📁 Repository Structure

```
GeneOntology_v1.1/
├── run_pipeline.sh              # Master executable pipeline runner script
├── scripts/                     # Python & R pipeline scripts
│   ├── run_gene_ontology.py     # Main GO annotation parsing & figure rendering
│   ├── build_go_word_doc.py     # Automated MS Word manuscript builder (.docx)
│   ├── go.py                    # Class-based GO hierarchy parser
│   ├── remove_empty.py          # Data cleaning helper utility
│   └── Untitled_21.R            # R ggplot2 visualization script
├── data/                        # Raw input datasets & ontologies
│   ├── Galaxy79-[InterProScan on dataset 78 (tsv)].tabular
│   ├── GO_Assignment.txt
│   └── go-basic.obo
├── results/                     # Generated output files & figures
│   ├── output_1.tsv             # Complete mapped GO annotation dataset
│   ├── GO_Domain_Summary_RANM35.csv  # Category summary statistics (BP, CC, MF)
│   ├── GO_Top10_Per_Category_RANM35.csv # Top 10 terms per category
│   ├── GO_Top10_Barplot_RANM35.png / .pdf # High-resolution top terms plot
│   ├── GO_Domain_PieChart_RANM35.png / .pdf # High-resolution domain pie chart
│   ├── go_term_counts_horizontal.png      # Horizontal barplot
│   └── Gene_Ontology_Analysis_RANM35.docx  # Full MS Word report with figures & text
├── requirements.txt             # Python dependencies
├── LICENSE                      # MIT Open-Source License
├── CITATION.cff                 # Citation metadata
└── README.md                    # Project documentation & user guide
```

---

## 🚀 Quick Start & Installation

### 1. Clone Repository
```bash
git clone https://github.com/YOUR_USERNAME/GeneOntology_v1.1.git
cd GeneOntology_v1.1
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

---

## 💻 Running the Pipeline

You can run the complete pipeline end-to-end with a single bash command:

```bash
chmod +x run_pipeline.sh
./run_pipeline.sh
```

Or execute individual modular scripts:

### Step 1: Data Processing & Plotting
```bash
python scripts/run_gene_ontology.py
```

### Step 2: MS Word Document Generator
```bash
python scripts/build_go_word_doc.py
```

---

## 📊 Sample Outputs

### Domain Distribution (RANM35)
- **Molecular Function**: 2,662 annotations (59.4%)
- **Biological Process**: 1,389 annotations (31.0%)
- **Cellular Component**: 430 annotations (9.6%)
- **Total Mapped Annotations**: 4,481 annotations across 1,683 unique genes

---

## 📜 Citation

If you use this pipeline in your research, please cite it as:
```bibtex
@software{GeneOntology_Pipeline_2026,
  author = {Microbiology Lab},
  title = {GeneOntology-Pipeline: Automated Gene Ontology Profiling and Manuscript Reporting (v1.1.0)},
  year = {2026},
  url = {https://github.com/YOUR_USERNAME/GeneOntology_v1.1}
}
```

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).
