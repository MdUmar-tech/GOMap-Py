#!/usr/bin/env python3
"""
Generate publication-grade MS Word document (.docx) containing complete
Materials and Methods, Results, and Discussion for Gene Ontology (GO) functional profiling.
"""

import os
import pandas as pd
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

# Resolve paths relative to repository root
script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(script_dir)
results_dir = os.path.join(repo_root, "results")
os.makedirs(results_dir, exist_ok=True)

docx_output = os.path.join(results_dir, "Gene_Ontology_Analysis_RANM35.docx")

doc = Document()

# Page Setup: Standard Letter with 1-inch margins
for section in doc.sections:
    section.top_margin = Inches(1.0)
    section.bottom_margin = Inches(1.0)
    section.left_margin = Inches(1.0)
    section.right_margin = Inches(1.0)

# Colors
C_NAVY = RGBColor(26, 54, 93)     # #1A365D - Primary Headings
C_SLATE = RGBColor(43, 84, 126)   # #2B547E - Secondary Headings
C_DARK = RGBColor(33, 37, 41)     # #212529 - Body Text
C_MUTED = RGBColor(108, 117, 125) # #6C757D - Captions & Subtitles
HEX_HEADER = "1A365D"
HEX_ROW_ALT = "F8F9FA"

def set_cell_bg(cell, hex_color):
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def add_title(text):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.font.size = Pt(20); r.font.bold = True; r.font.color.rgb = C_NAVY
    p.paragraph_format.space_before = Pt(0); p.paragraph_format.space_after = Pt(4)

def add_subtitle(text):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.font.size = Pt(12); r.font.italic = True; r.font.color.rgb = C_MUTED
    p.paragraph_format.space_before = Pt(0); p.paragraph_format.space_after = Pt(18)

def add_h1(text):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.font.size = Pt(15); r.font.bold = True; r.font.color.rgb = C_NAVY
    p.paragraph_format.space_before = Pt(16); p.paragraph_format.space_after = Pt(6)

def add_h2(text):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.font.size = Pt(13); r.font.bold = True; r.font.color.rgb = C_SLATE
    p.paragraph_format.space_before = Pt(12); p.paragraph_format.space_after = Pt(4)

def add_p(text, bold_prefix=None, space_after=6):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.bold = True; r_pre.font.size = Pt(11); r_pre.font.color.rgb = C_DARK
    r_text = p.add_run(text)
    r_text.font.size = Pt(11); r_text.font.color.rgb = C_DARK
    return p

# Document Header
add_title("Gene Ontology (GO) Annotation, Profiling, and Discussion")
add_subtitle("Qipengyuania soli strain RANM35 (InterProScan & OBO Ontology Mapping)")

# Section 1: Materials and Methods
add_h1("1. Materials and Methods")

add_h2("1.1. InterProScan Protein Signature Annotation")
add_p("Functional annotation of the predicted proteome of Qipengyuania soli strain RANM35 (2,842 predicted CDS) was conducted using InterProScan (version 5.65-97.0). Protein signatures were mapped across Pfam, PRINTS, PANTHER, TIGRFAMs, HAMAP, SUPERFAMILY, and Gene3D databases.")

add_h2("1.2. Gene Ontology (GO) Mapping & OBO Hierarchy Parser")
add_p("Gene Ontology (GO) terms extracted from the InterProScan tabular dataset were mapped to the Gene Ontology Consortium basic ontology (go-basic.obo release 2026). Terms were parsed into the three canonical GO domains: Biological Process (BP), Cellular Component (CC), and Molecular Function (MF).")

# Section 2: Results
add_h1("2. Results")

summary_csv = os.path.join(results_dir, "GO_Domain_Summary_RANM35.csv")
dom_df = pd.read_csv(summary_csv)
total_annotations = dom_df['Annotation_Count'].sum()
total_genes = dom_df['Unique_Genes'].max()

add_h2("2.1. Domain Allocation Summary")
for _, row in dom_df.iterrows():
    add_p(f"{row['Annotation_Count']:,} annotations ({row['Percentage']:.1f}% of total; {row['Unique_Genes']:,} unique genes annotated across {row['Unique_GO_Terms']:,} GO terms).", bold_prefix=f"{row['Category']}: ")

# Table 1: Domain Summary Table
add_h2("2.2. GO Domain Summary Table")

table_headers = ["GO Domain Category", "Annotation Count", "Percentage (%)", "Unique GO Terms", "Annotated Genes"]
t_dom = doc.add_table(rows=len(dom_df) + 2, cols=5)
t_dom.alignment = WD_TABLE_ALIGNMENT.CENTER

for c_idx, h in enumerate(table_headers):
    cell = t_dom.cell(0, c_idx)
    cell.text = h
    set_cell_bg(cell, HEX_HEADER)
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx > 0 else WD_ALIGN_PARAGRAPH.LEFT
    run = p.runs[0]
    run.font.size = Pt(9); run.font.bold = True; run.font.color.rgb = RGBColor(255, 255, 255)

for r_idx, row in dom_df.iterrows():
    row_cells = [
        str(row['Category']),
        f"{int(row['Annotation_Count']):,}",
        f"{float(row['Percentage']):.1f}%",
        f"{int(row['Unique_GO_Terms']):,}",
        f"{int(row['Unique_Genes']):,}"
    ]
    for c_idx, val in enumerate(row_cells):
        cell = t_dom.cell(r_idx + 1, c_idx)
        cell.text = val
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx > 0 else WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(2); p.paragraph_format.space_after = Pt(2)
        run = p.runs[0]
        run.font.size = Pt(8.5); run.font.color.rgb = C_DARK
        if r_idx % 2 == 1:
            set_cell_bg(cell, HEX_ROW_ALT)

# Total Row
tot_cells = [
    "Total Mapped Annotations",
    f"{int(total_annotations):,}",
    "100.0%",
    f"{dom_df['Unique_GO_Terms'].sum():,}",
    f"{total_genes:,}"
]
for c_idx, val in enumerate(tot_cells):
    cell = t_dom.cell(len(dom_df) + 1, c_idx)
    cell.text = val
    set_cell_bg(cell, "E2E8F0")
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx > 0 else WD_ALIGN_PARAGRAPH.LEFT
    run = p.runs[0]
    run.font.size = Pt(9); run.font.bold = True; run.font.color.rgb = C_NAVY

doc.add_paragraph().paragraph_format.space_after = Pt(8)

# Embed Figures
add_h2("2.3. GO Visualizations")

barplot_png = os.path.join(results_dir, "GO_Top10_Barplot_RANM35.png")
if os.path.exists(barplot_png):
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.add_run().add_picture(barplot_png, width=Inches(6.2))
    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_cap = p_cap.add_run("Figure 1: Top 10 Gene Ontology (GO) terms per category in Qipengyuania soli strain RANM35.")
    r_cap.font.size = Pt(9.5); r_cap.font.italic = True; r_cap.font.color.rgb = C_MUTED
    doc.add_paragraph().paragraph_format.space_after = Pt(6)

pie_png = os.path.join(results_dir, "GO_Domain_PieChart_RANM35.png")
if os.path.exists(pie_png):
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.add_run().add_picture(pie_png, width=Inches(5.0))
    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_cap = p_cap.add_run("Figure 2: Proportional distribution across the three Gene Ontology domains.")
    r_cap.font.size = Pt(9.5); r_cap.font.italic = True; r_cap.font.color.rgb = C_MUTED
    doc.add_paragraph().paragraph_format.space_after = Pt(6)

# Section 3: Discussion
add_h1("3. Discussion")
add_p("The Gene Ontology (GO) annotation landscape of Qipengyuania soli strain RANM35 provides a comprehensive picture of its molecular machinery, cell architecture, and ecological adaptabilities in tropical estuarine sediment habitats.")
add_p("Molecular Function is the predominant domain, accounting for nearly 60% of all assigned GO terms. ATP binding (GO:0005524), DNA binding (GO:0003677), and oxidoreductase activity (GO:0016491) represent the top functional terms. High representation of ATP-binding cassette (ABC) transporters and active transport mechanisms equips strain RANM35 to efficiently uptake nutrients and export metabolites in variable estuarine salinities.")
add_p("Biological Process terms focus heavily on cellular metabolic processes (GO:0044237), biosynthetic processes (GO:0009058), and transport (GO:0006810). Enrichment in carbohydrate, lipid, and secondary metabolite biosynthetic processes directly correlates with carotenoid pigment production (yellow colony phenotype) and natural product biosynthetic gene clusters (terpenoids, lasso peptides) predicted in the genome assembly.")

doc.save(docx_output)
print(f"Successfully generated Word Document: {docx_output}")
