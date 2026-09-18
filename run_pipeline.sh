#!/usr/bin/env bash
# ==============================================================================
# Gene Ontology (GO) Analysis Pipeline v1.1 Master Runner Script
# Organism: Qipengyuania soli strain RANM35
# Description: Executes end-to-end GO annotation parsing, taxonomy/domain 
#              classification, visualization, and MS Word report generation.
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "======================================================================"
echo " Starting Gene Ontology Analysis Pipeline (v1.1.0)"
echo " Repository Root: $SCRIPT_DIR"
echo " Time: $(date)"
echo "======================================================================"

# Step 1: Execute Gene Ontology Processing and Visualization Pipeline
echo ""
echo "[Step 1/2] Running GO Annotation Processing and Figure Generation..."

if [ -x "/opt/miniconda3/bin/conda" ]; then
    /opt/miniconda3/bin/conda run -n bioinfo python scripts/run_gene_ontology.py
else
    python3 scripts/run_gene_ontology.py
fi

# Step 2: Build Publication-Grade Word Document Report (.docx)
echo ""
echo "[Step 2/2] Generating MS Word Document Report..."
python3 scripts/build_go_word_doc.py

echo ""
echo "======================================================================"
echo " Pipeline Execution Completed Successfully!"
echo " Results stored in: $SCRIPT_DIR/results/"
echo " Files generated:"
echo "   - Table S1 (Full Annotations):  results/GO_Assignment.txt"
echo "   - Table S2 (Domain Summary):    results/GO_Domain_Summary_RANM35.csv"
echo "   - Table S3 (Top 10 Terms):      results/GO_Top10_Per_Category_RANM35.csv"
echo "   - Figure 1 (Barplot PNG/PDF):   results/GO_Top10_Barplot_RANM35.png / .pdf"
echo "   - Figure 2 (Pie Chart PNG/PDF): results/GO_Domain_PieChart_RANM35.png / .pdf"
echo "   - Manuscript Document:          results/Gene_Ontology_Analysis_RANM35.docx"
echo "======================================================================"
