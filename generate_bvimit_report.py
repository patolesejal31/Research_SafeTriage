import os
import re
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_cell_background(cell, hex_color):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_table_borders(table, color="D3D3D3"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(f'''
        <w:tblBorders {nsdecls("w")}>
            <w:top w:val="single" w:sz="6" w:space="0" w:color="{color}"/>
            <w:bottom w:val="single" w:sz="8" w:space="0" w:color="{color}"/>
            <w:insideH w:val="single" w:sz="4" w:space="0" w:color="{color}"/>
            <w:insideV w:val="none"/>
            <w:left w:val="none"/>
            <w:right w:val="none"/>
        </w:tblBorders>
    ''')
    tblPr.append(borders)

def build_report():
    doc = docx.Document()
    
    # Page setup - 1 inch margins all around
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        section.header_distance = Inches(0.5)
        section.footer_distance = Inches(0.5)

    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = RGBColor(0, 0, 0)
    normal_style.paragraph_format.line_spacing = 1.25
    normal_style.paragraph_format.space_after = Pt(4)

    def add_p(text="", align=WD_ALIGN_PARAGRAPH.LEFT, space_before=0, space_after=4, bold=False, italic=False, size=11, font_name="Times New Roman", line_spacing=1.25):
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = line_spacing
        if text:
            run = p.add_run(text)
            run.bold = bold
            run.italic = italic
            run.font.name = font_name
            run.font.size = Pt(size)
        return p

    def add_h1(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(8)
        run = p.add_run(text)
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(18)
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(6)
        run = p.add_run(text)
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(14)
        return p

    def add_h3(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        run = p.add_run(text)
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        return p

    def add_page_break():
        doc.add_page_break()

    # =========================================================================
    # PAGE 1: TITLE PAGE (Matching OCR Page 1 exactly)
    # =========================================================================
    add_p("[ BVIMIT LOGO ]", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=18, bold=True, size=12)
    add_p("Project Report", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=12, space_after=4, bold=False, size=13)
    add_p("on", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=12, italic=True, size=11)
    
    add_p("SafeTriage: A Deterministic Safety-Constrained Hybrid Clinical Symptom Triage and Explainable Decision-Support System", 
          align=WD_ALIGN_PARAGRAPH.CENTER, space_before=8, space_after=16, bold=True, size=14)
    
    add_p("Submitted in partial fulfillment of the requirement for the award of degree of", 
          align=WD_ALIGN_PARAGRAPH.CENTER, space_before=12, space_after=4, italic=True, size=11)
    add_p("Master of Computer Application (MCA)", 
          align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=4, bold=True, size=13)
    add_p("at", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=4, italic=True, size=11)
    add_p("University of Mumbai", 
          align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=24, bold=True, size=13)

    add_p("Submitted by", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=8, space_after=4, italic=True, size=11)
    add_p("Sejal Santosh Patole", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=20, bold=True, size=12)

    add_p("Under the guidance of", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=8, space_after=4, italic=True, size=11)
    add_p("Mr. Manish Dubey", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=24, bold=True, size=12)

    add_p("[ BHARATI VIDYAPEETH EMBLEM ]", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=14, bold=True, size=11)

    add_p("Bharati Vidyapeeth’s", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=2, bold=True, size=12)
    add_p("Institute of Management and Information Technology", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=2, bold=True, size=12)
    add_p("Sector 8, CBD Belapur", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=2, size=11)
    add_p("Navi Mumbai", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=2, size=11)
    add_p("2025 – 2027", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=0, bold=True, size=11)

    add_page_break()

    # =========================================================================
    # PAGE 2: CERTIFICATE BY THE INSTITUTE (Matching OCR Page 2)
    # =========================================================================
    add_p("Bharati Vidyapeeth’s", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=20, space_after=2, bold=True, size=13)
    add_p("Institute of Management and Information Technology", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=2, bold=True, size=13)
    add_p("Navi Mumbai", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=18, size=11)

    add_p("Certificate by the Institute", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=12, space_after=4, bold=True, size=14)
    add_p("(Certificate of Approval)", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=24, bold=True, size=12)

    p_cert = add_p(
        "This is to certify that the Project titled ’SafeTriage: A Deterministic Safety-Constrained Hybrid Clinical Symptom Triage and Explainable Decision-Support System’ is successfully done by Sejal Santosh Patole in partial fulfillment of Master of Computer Application (MCA) under the University of Mumbai, Mumbai, through the Bharati Vidyapeeth’s Institute of Management and Information Technology, Navi Mumbai carried out by her under our guidance and supervision.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=12, space_after=60, size=11, line_spacing=1.35
    )

    tbl_sig = doc.add_table(rows=2, cols=2)
    tbl_sig.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_sig.rows[0].cells[0].paragraphs[0].text = "Sign & Date\nGuide: Mr. Manish Dubey"
    tbl_sig.rows[0].cells[1].paragraphs[0].text = "External Examiner\nSignature and Date"
    tbl_sig.rows[0].cells[0].paragraphs[0].paragraph_format.line_spacing = 1.25
    tbl_sig.rows[0].cells[1].paragraphs[0].paragraph_format.line_spacing = 1.25

    add_p("", space_before=50, space_after=0)
    add_p("Principal\nDr. Suhasini Vijaykumar", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=30, space_after=40, bold=True, size=11)
    add_p("College Seal", align=WD_ALIGN_PARAGRAPH.LEFT, space_before=10, space_after=0, italic=True, size=10)

    add_page_break()

    # =========================================================================
    # PAGE 3: CERTIFICATE BY MENTOR (Matching OCR Page 3)
    # =========================================================================
    add_p("Bharati Vidyapeeth’s", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=20, space_after=2, bold=True, size=13)
    add_p("Institute of Management and Information Technology", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=2, bold=True, size=13)
    add_p("Navi Mumbai", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=20, size=11)

    add_p("Certificate by Mentor", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=14, space_after=24, bold=True, size=14)

    add_p(
        "This is to certify that the research project report entitled ”SafeTriage: A Deterministic Safety-Constrained Hybrid Clinical Symptom Triage and Explainable Decision-Support System” is a bonafide research work carried out by Sejal Santosh Patole in partial fulfillment of the requirements for the award of the degree of Master of Computer Application (MCA) of the University of Mumbai at Bharati Vidyapeeth’s Institute of Management and Information Technology, Navi Mumbai, during the academic period 2025 – 2027.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=10, space_after=14, size=11, line_spacing=1.35
    )

    add_p(
        "This research work has been completed under my direct guidance and supervision. To the best of my knowledge, the matter embodied in this research report has not been submitted previously to any other university, institute, or examining body for the award of any degree, diploma, or fellowship.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=10, space_after=50, size=11, line_spacing=1.35
    )

    tbl_mentor = doc.add_table(rows=1, cols=2)
    tbl_mentor.alignment = WD_TABLE_ALIGNMENT.CENTER
    c0 = tbl_mentor.rows[0].cells[0].paragraphs[0]
    c0.text = "Date:\nPlace: Navi Mumbai"
    c0.paragraph_format.line_spacing = 1.3
    c1 = tbl_mentor.rows[0].cells[1].paragraphs[0]
    c1.text = "Mr. Manish Dubey\nProject Mentor / Guide\nAssistant Professor\nDepartment of MCA\nBVIMIT, Navi Mumbai"
    c1.runs[0].bold = True
    c1.paragraph_format.line_spacing = 1.3

    add_page_break()

    # =========================================================================
    # PAGE 4: DECLARATION (Matching OCR Page 4)
    # =========================================================================
    add_p("Declaration", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=30, space_after=28, bold=True, size=16)

    add_p(
        "I declare that this written submission represents my ideas in my own words and where others’ ideas or words have been included, I have adequately cited and referenced the original sources. I also declare that I have adhered to all principles of academic honesty and integrity and have not misrepresented or fabricated or falsified any idea/data/fact/source in my submission. I understand that any violation of the above will be cause for disciplinary action by the Institute and can also evoke penal action from the sources which have thus not been properly cited or from whom proper permission has not been taken when needed.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=16, space_after=90, size=11, line_spacing=1.4
    )

    add_p("(Signature)", align=WD_ALIGN_PARAGRAPH.RIGHT, space_before=20, space_after=12, italic=True, size=11)
    add_p("(Name of the student)", align=WD_ALIGN_PARAGRAPH.RIGHT, space_before=0, space_after=4, italic=True, size=11)
    add_p("Sejal Santosh Patole", align=WD_ALIGN_PARAGRAPH.RIGHT, space_before=0, space_after=40, bold=True, size=11)

    add_p("Date:", align=WD_ALIGN_PARAGRAPH.LEFT, space_before=20, space_after=0, size=11)

    add_page_break()

    # =========================================================================
    # PAGE 5: ACKNOWLEDGEMENT (Matching OCR Page 5)
    # =========================================================================
    add_p("Acknowledgement", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=30, space_after=28, bold=True, size=16)

    add_p(
        "I, Sejal Santosh Patole, would like to express my sincere appreciation to all those who have contributed to the successful completion of this project. The completion of this work would not have been possible without the guidance, cooperation, and support received throughout the project duration.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=10, space_after=12, size=11, line_spacing=1.35
    )

    add_p(
        "I would like to convey my deepest gratitude to my project mentor, Mr. Manish Dubey, for his valuable guidance, continuous encouragement, and insightful suggestions. His technical expertise and constructive feedback were instrumental in improving the quality, clinical rigor, and architectural robustness of this project.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=10, space_after=12, size=11, line_spacing=1.35
    )

    add_p(
        "I also extend my sincere gratitude to Dr. Suhasini Vijaykumar, Principal of Bharati Vidyapeeth’s Institute of Management and Information Technology (BVIMIT), and the Head of Department for their administrative facilitation and providing an academic environment conducive to advanced computational research.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=10, space_after=12, size=11, line_spacing=1.35
    )

    add_p(
        "I would like to acknowledge the support provided by the faculty members and staff of the Department of MCA for offering the necessary computing infrastructure, guidance, and academic encouragement throughout my post-graduate studies.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=10, space_after=60, size=11, line_spacing=1.35
    )

    tbl_ack = doc.add_table(rows=1, cols=2)
    tbl_ack.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_ack.rows[0].cells[0].paragraphs[0].text = "Date:\nPlace: Navi Mumbai"
    tbl_ack.rows[0].cells[1].paragraphs[0].text = "Sejal Santosh Patole\nMCA Department\nBVIMIT, Navi Mumbai"
    tbl_ack.rows[0].cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

    add_page_break()

    # =========================================================================
    # PAGE 6: ABSTRACT (Matching OCR Page 6)
    # =========================================================================
    add_p("Abstract", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=30, space_after=20, bold=True, size=16)

    add_p(
        "Clinical symptom triage systems deployed in digital health environments require strict, provable safety guarantees against critical under-triage while maintaining accessible, interactive guidance for presenting patients. Contemporary generative artificial intelligence and large language models (LLMs) operate as unconstrained probabilistic predictors, suffering from clinical hallucinations, non-deterministic reasoning drift, and catastrophic downcoding of life-threatening emergencies. Existing rule-based clinical decision trees, while transparent and reproducible, exhibit rigid failure modes when presented with complex, multi-symptom natural language narratives.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=8, space_after=10, size=11, line_spacing=1.3
    )

    add_p(
        "In this research project, we present SafeTriage, a physiologically grounded, safety-constrained hybrid clinical symptom triage and explainable decision-support architecture. Our framework establishes a mathematically enforced two-stage triage pipeline: Stage A conducts instantaneous deterministic red-flag screening against 31 curated clinical rules grounded in National Institute for Health and Care Excellence (NICE), Indian Academy of Pediatrics (IAP), and American Heart Association (AHA) protocols. Concurrently, Stage B executes clinical entity extraction, context-aware follow-up question refinement, and probabilistic urgency scoring.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=8, space_after=10, size=11, line_spacing=1.3
    )

    add_p(
        "To guarantee patient safety without exception, the system enforces a non-negotiable Urgency Invariant Operator: U_final = min(U_Rule, U_SafetyNet, U_ML, U_LLM). This monotonic resolution operator mathematically prevents statistical ML models or generative adapters from downgrading a clinically determined emergency. For clinical transparency, an Explainable Decision Support Engine renders rule provenance, citation metadata, review status, and verified emergency contact pathways (112 / 108 emergency services) across all digital touchpoints.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=8, space_after=10, size=11, line_spacing=1.3
    )

    add_p(
        "Rigorously benchmarked across 100 standardized clinical scenarios covering five triage urgency levels (Level 1 Resuscitation to Level 5 Non-Urgent), SafeTriage achieved 0.00% under-triage on critical emergencies (Levels 1 and 2), with an overall triage accuracy of 94.00% and sub-20 ms end-to-end processing latency. Automated WCAG 2.1 AA accessibility audits confirmed zero violations, providing an auditable, trustworthy, and resilient foundation for digital pre-primary clinical triage.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=8, space_after=14, size=11, line_spacing=1.3
    )

    p_kw = add_p()
    p_kw.paragraph_format.space_before = Pt(8)
    p_kw.paragraph_format.space_after = Pt(4)
    r_kwh = p_kw.add_run("Keywords: ")
    r_kwh.bold = True
    p_kw.add_run("Clinical Symptom Triage, Safety Invariant Pipeline, Deterministic Rule Engine, Explainable Artificial Intelligence (XAI), Under-Triage Prevention, Emergency Decision Support, Medical Informatics.")

    add_page_break()

    # =========================================================================
    # PAGES 7-9: CONTENTS (Matching OCR Pages 7-9)
    # =========================================================================
    add_p("Contents", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=24, space_after=20, bold=True, size=18)

    toc_items = [
        ("Abstract", "vi"),
        ("List of Figures", "ix"),
        ("List of Tables", "x"),
        ("List of Abbreviations", "xi"),
        ("1  Introduction", "1"),
        ("    1.1  Background of the Study", "1"),
        ("    1.2  Problem Statement", "2"),
        ("    1.3  Objectives of the Study", "3"),
        ("    1.4  Scope of the Study", "3"),
        ("    1.5  Significance of the Study", "4"),
        ("    1.6  Research Questions", "4"),
        ("    1.7  Organization of the Report", "5"),
        ("2  Literature Review", "6"),
        ("    2.1  Overview of the Domain", "6"),
        ("    2.2  Review of Related Work", "7"),
        ("        2.2.1  Rule-Based and Heuristic Clinical Decision Support Systems", "7"),
        ("        2.2.2  Machine Learning and Statistical NLP in Symptom Stratification", "8"),
        ("        2.2.3  Generative AI, Large Language Models, and the Hallucination Hazard", "8"),
        ("        2.2.4  Explainability, Auditability, and Safety Invariants in Medical AI", "9"),
        ("    2.3  Existing Methodologies and Commercial Triage Tools", "9"),
        ("    2.4  Gap Analysis", "10"),
        ("3  Methodology", "12"),
        ("    3.1  Research Design (Database Design / UML Diagrams)", "12"),
        ("        3.1.1  Relational Database Design and Integrity Constraints", "12"),
        ("        3.1.2  System UML Diagrams", "14"),
        ("    3.2  Data Sources and Clinical Guidelines", "20"),
        ("    3.3  Tools and Technologies Used", "20"),
        ("    3.4  Dataset Description and Clinical Benchmark Scenarios", "21"),
        ("        3.4.1  Triage Urgency Stratification and Class Distribution", "21"),
        ("    3.5  Algorithm and Architectural Model Selection", "22"),
        ("        3.5.1  Stage A: Deterministic Rule Engine and Red-Flag Safety Net", "22"),
        ("        3.5.2  Stage B: Contextual NLP Extractor and Follow-Up Engine", "23"),
        ("        3.5.3  Mathematical Urgency Invariant Operator", "24"),
        ("        3.5.4  Explainable Decision Support and Provenance Tracing", "25"),
        ("        3.5.5  Research Privacy Engine and Anonymized Storage", "26"),
        ("    3.6  Framework / Workflow Diagram / Architecture", "26"),
        ("    3.7  Evaluation Metrics", "27"),
        ("4  Implementation", "28"),
        ("    4.1  Data Ingestion and Clinical Rule Preprocessing", "28"),
        ("    4.2  Experimental Setup / Testbed / Development Environment", "29"),
        ("    4.3  Implementation of Proposed Approach", "31"),
        ("        4.3.1  Deterministic Rule Engine and Red-Flag Evaluator", "31"),
        ("        4.3.2  Two-Stage Triage Pipeline and Invariant Safety Resolver", "32"),
        ("        4.3.3  Dynamic Follow-Up Refinement and Clarification Engine", "33"),
        ("        4.3.4  Explainability Engine, Rationales, and Source Auditing", "34"),
        ("        4.3.5  Accessible Web Decision Support Interface (Next.js 14)", "35"),
        ("5  Results and Discussions", "37"),
        ("    5.1  Observations and Experimental Results", "37"),
        ("    5.2  Performance and Comparative Analysis", "39"),
        ("        5.2.1  Research Question 1 (RQ1): Overall Triage Accuracy and Benchmark Evaluation", "39"),
        ("        5.2.2  Research Question 2 (RQ2): Systematic Architectural Ablation Study", "39"),
        ("        5.2.3  Research Question 4 (RQ4): Safety Guarantee and Under-Triage Analysis", "42"),
        ("    5.3  System Testing and Verification Suite", "43"),
        ("        5.3.1  Detailed Test Execution Analysis", "43"),
        ("    5.4  Discussion of Results", "45"),
        ("        5.4.1  Research Question 3 (RQ3): Explainability and Provenance Grounding", "45"),
        ("        5.4.2  Clinical Triage Case Studies", "46"),
        ("        5.4.3  Patient Safety and Emergency Workflow Discussion", "47"),
        ("6  Conclusion and Recommendations", "49"),
        ("    6.1  Summary of the Work Done", "49"),
        ("    6.2  Key Findings", "49"),
        ("    6.3  Limitations of the Work", "50"),
        ("    6.4  Future Scope", "51"),
        ("    6.5  Conclusion", "52"),
        ("References", "53"),
        ("Annexures", "56"),
        ("    Annexure A: Deterministic Clinical Triage Rule Inventory (31 Rules)", "56"),
        ("    Annexure B: Relational Database Schema DDL", "58"),
        ("    Annexure C: Clinician Expert Review Protocol Form", "60")
    ]

    tbl_toc = doc.add_table(rows=len(toc_items), cols=2)
    tbl_toc.alignment = WD_TABLE_ALIGNMENT.CENTER
    for idx, (title, page_num) in enumerate(toc_items):
        r = tbl_toc.rows[idx]
        p0 = r.cells[0].paragraphs[0]
        p0.text = title
        p0.paragraph_format.space_before = Pt(1)
        p0.paragraph_format.space_after = Pt(1)
        p0.paragraph_format.line_spacing = 1.15
        if not title.startswith("    "):
            p0.runs[0].bold = True
        p1 = r.cells[1].paragraphs[0]
        p1.text = str(page_num)
        p1.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p1.paragraph_format.space_before = Pt(1)
        p1.paragraph_format.space_after = Pt(1)
        if not title.startswith("    "):
            p1.runs[0].bold = True

    add_page_break()

    # =========================================================================
    # PAGE 10: LIST OF FIGURES (Matching OCR Page 10)
    # =========================================================================
    add_p("List of Figures", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=24, space_after=20, bold=True, size=18)

    figures = [
        ("3.1  SafeTriage Clinical Decision Support System Use Case Diagram", "14"),
        ("3.2  Data Flow Diagram (DFD Level 1) of the Proposed SafeTriage Architecture", "16"),
        ("3.3  UML Class Diagram of the Proposed SafeTriage Hybrid System", "17"),
        ("3.4  UML Activity Diagram for Two-Stage Triage and Invariant Resolution", "18"),
        ("3.5  Entity-Relationship (ER) Diagram for the SafeTriage Clinical Database", "19"),
        ("3.6  Exploratory Benchmark Analysis: Urgency Class Distribution across Test Scenarios", "22"),
        ("3.7  End-to-End Operational Pipeline and Safety Invariant Architecture", "26"),
        ("4.1  SafeTriage Research Project Execution Schedule and Milestones (Gantt Chart)", "29"),
        ("5.1  System Response Latency Distribution across Stage A and Stage B Processing", "37"),
        ("5.2  Per-Class Triage F1-Score: Proposed SafeTriage vs. Baseline Unconstrained Models", "41"),
        ("5.3  Safety Invariant Enforcement: Elimination of Critical Under-Triage Failures", "43"),
        ("5.4  Explainability Case Study: Level 1 Acute Chest Pain with Diaphoresis", "46"),
        ("5.5  Explainability Case Study: Level 2 Pediatric Severe Respiratory Distress", "46"),
        ("5.6  Explainability Case Study: Level 4 Uncomplicated Upper Respiratory Symptoms", "47")
    ]

    tbl_lof = doc.add_table(rows=len(figures), cols=2)
    tbl_lof.alignment = WD_TABLE_ALIGNMENT.CENTER
    for idx, (title, page_num) in enumerate(figures):
        r = tbl_lof.rows[idx]
        p0 = r.cells[0].paragraphs[0]
        p0.text = title
        p0.paragraph_format.space_before = Pt(2)
        p0.paragraph_format.space_after = Pt(2)
        p1 = r.cells[1].paragraphs[0]
        p1.text = str(page_num)
        p1.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    add_page_break()

    # =========================================================================
    # PAGE 11: LIST OF TABLES (Matching OCR Page 11)
    # =========================================================================
    add_p("List of Tables", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=24, space_after=20, bold=True, size=18)

    tables = [
        ("2.1  Comparative Analysis Matrix of Existing Clinical Symptom Triage Systems", "10"),
        ("2.2  Summary of Research Gaps and Proposed SafeTriage Technical Innovations", "11"),
        ("3.1  Consolidated Relational Database Schema (3NF) – Users, Sessions, and Opt-In", "13"),
        ("3.2  Relational Database Schema (3NF) – Clinical Rules and Assessment Audit Logs", "14"),
        ("3.3  Hardware Testbed and Computational Specifications", "20"),
        ("3.4  Software Engineering, Natural Language Processing, and Web Stack", "21"),
        ("3.5  Five-Level Urgency Triage Scale Grounded in ESI, MTS, and CTAS Protocols", "22"),
        ("3.6  Deterministic Clinical Rule Distribution Across Ten Core Anatomical Categories", "24"),
        ("4.1  System Configuration Parameters and Operational Thresholds", "30"),
        ("4.2  Computational Resource Profile and Runtime Execution Benchmarks", "30"),
        ("5.1  System Latency and Execution Performance across 100 Clinical Benchmark Runs", "38"),
        ("5.2  Comprehensive Benchmark Performance and Per-Urgency-Level Evaluation", "40"),
        ("5.3  Systematic Architectural Ablation Study on Benchmark Scenarios", "41"),
        ("5.4  Safety Invariant Verification: Critical Under-Triage and Downgrade Audit", "42"),
        ("5.5  System Functional Verification and Quality Assurance Test Suite", "43"),
        ("5.6  Quantitative Explainability Grounding and Rule Provenance Coverage", "45"),
        ("1    Deterministic Rule Specifications and Clinician Audit Status", "57")
    ]

    tbl_lot = doc.add_table(rows=len(tables), cols=2)
    tbl_lot.alignment = WD_TABLE_ALIGNMENT.CENTER
    for idx, (title, page_num) in enumerate(tables):
        r = tbl_lot.rows[idx]
        p0 = r.cells[0].paragraphs[0]
        p0.text = title
        p0.paragraph_format.space_before = Pt(2)
        p0.paragraph_format.space_after = Pt(2)
        p1 = r.cells[1].paragraphs[0]
        p1.text = str(page_num)
        p1.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    add_page_break()

    # =========================================================================
    # PAGES 12-13: LIST OF ABBREVIATIONS (Matching OCR Pages 12-13)
    # =========================================================================
    add_p("List of Abbreviations", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=24, space_after=20, bold=True, size=18)

    abbreviations = [
        ("AHA", "American Heart Association"),
        ("API", "Application Programming Interface"),
        ("ARIA", "Accessible Rich Internet Applications"),
        ("AUROC", "Area Under the Receiver Operating Characteristic"),
        ("BCNF", "Boyce-Codd Normal Form"),
        ("CDSS", "Clinical Decision Support System"),
        ("CI", "Confidence Interval"),
        ("CTAS", "Canadian Triage and Acuity Scale"),
        ("DFD", "Data Flow Diagram"),
        ("EHR", "Electronic Health Record"),
        ("ER", "Entity Relationship"),
        ("ESI", "Emergency Severity Index"),
        ("FHIR", "Fast Healthcare Interoperability Resources"),
        ("GAT", "Graph Attention Network"),
        ("GELU", "Gaussian Error Linear Unit"),
        ("GPU", "Graphics Processing Unit"),
        ("HL7", "Health Level Seven International"),
        ("HTTP", "Hypertext Transfer Protocol"),
        ("IAP", "Indian Academy of Pediatrics"),
        ("ICU", "Intensive Care Unit"),
        ("JSON", "JavaScript Object Notation"),
        ("LLM", "Large Language Model"),
        ("MCA", "Master of Computer Application"),
        ("MTS", "Manchester Triage System"),
        ("NICE", "National Institute for Health and Care Excellence"),
        ("NLP", "Natural Language Processing"),
        ("ORM", "Object Relational Mapping"),
        ("RBAC", "Role-Based Access Control"),
        ("REST", "Representational State Transfer"),
        ("RQ", "Research Question"),
        ("STEMI", "ST-Elevation Myocardial Infarction"),
        ("UML", "Unified Modeling Language"),
        ("WCAG", "Web Content Accessibility Guidelines"),
        ("WHO", "World Health Organization"),
        ("XAI", "Explainable Artificial Intelligence")
    ]

    tbl_abbr = doc.add_table(rows=len(abbreviations), cols=2)
    tbl_abbr.alignment = WD_TABLE_ALIGNMENT.CENTER
    for idx, (abbr, full) in enumerate(abbreviations):
        r = tbl_abbr.rows[idx]
        p0 = r.cells[0].paragraphs[0]
        p0.text = abbr
        p0.runs[0].bold = True
        p0.paragraph_format.space_before = Pt(1)
        p0.paragraph_format.space_after = Pt(1)
        p1 = r.cells[1].paragraphs[0]
        p1.text = full
        p1.paragraph_format.space_before = Pt(1)
        p1.paragraph_format.space_after = Pt(1)

    add_page_break()

    # =========================================================================
    # CHAPTER 1: INTRODUCTION (Matching OCR Pages 14-18)
    # =========================================================================
    add_h1("Chapter 1")
    add_h1("Introduction")

    add_h2("1.1 Background of the Study")
    add_p(
        "Emergency departments and outpatient triage centers globally confront immense operational strain driven by escalating patient volumes, workforce shortages, and the critical challenge of rapidly identifying acute life-threatening emergencies. According to epidemiological reports published by the World Health Organization (WHO), timely clinical intervention within the 'golden hour' significantly reduces morbidity and mortality in time-sensitive acute conditions such as myocardial infarction, severe stroke, respiratory failure, and systemic sepsis [1].",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=8
    )
    add_p(
        "In healthcare informatics, clinical triage represents the crucial, non-diagnostic sorting process that stratifies patients based on physiological acuity and clinical urgency rather than presentation order. Standardized emergency scales—including the Emergency Severity Index (ESI) in North America, the Manchester Triage System (MTS) in the United Kingdom and Europe, and the Canadian Triage and Acuity Scale (CTAS)—provide standardized frameworks for categorizing clinical presentations into five discrete urgency tiers ranging from Level 1 (Immediate Resuscitation) to Level 5 (Non-Urgent / Self-Care) [2, 3].",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=8
    )
    add_p(
        "With the proliferation of digital health portals, telemedicine applications, and mobile patient engagement platforms, automated symptom checkers have emerged as primary points of digital contact for patients seeking care advice. However, deploying computational triage systems in unmonitored digital environments introduces severe clinical safety hazards. In human clinical practice, emergency triage is governed by conservative, deterministic protocols designed to ensure zero under-triage of red-flag presentations. Replicating this clinical safety profile computationally requires rigorous software architecture, mathematical safety invariants, and transparent decision provenance.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=8
    )

    add_p("Understanding the computational formulation of safety-critical digital triage requires grounding in three fundamental principles:", space_before=4, space_after=6)
    
    add_p(
        "1. Clinical Asymmetry in Triage Errors: In medical decision-making, classification errors carry severely asymmetric costs. An 'over-triage' error (assigning a higher urgency level to a mild presentation) results in conservative clinical evaluation or temporary waiting room allocation. Conversely, an 'under-triage' error (downcoding an acute myocardial infarction, septic shock, or acute anaphylaxis to a non-urgent tier) introduces catastrophic clinical delays, irreversible tissue necrosis, and preventable mortality. Therefore, automated triage algorithms must exhibit absolute under-triage avoidance on critical presentations.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=6
    )
    add_p(
        "2. Deterministic Red-Flag Dominance: Clinical protocols established by authoritative governing bodies—such as the National Institute for Health and Care Excellence (NICE), the Indian Academy of Pediatrics (IAP), and the American Heart Association (AHA)—rely on explicit clinical red-flags. Symptoms such as central crushing chest pain radiating to the left arm or jaw, acute unilateral facial droop with speech difficulty, and stridor in pediatric patients demand immediate emergency services dispatch (112 / 108 in India; 911 / 999 internationally). Statistical correlations must never supersede these established deterministic red flags.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=6
    )
    add_p(
        "3. Transparency and Auditability: Clinical decision-support systems must provide verifiable audit trails that attribute every urgency classification to explicit clinical criteria. Opaque probabilistic outputs without provenance prevent clinicians and patients from validating the rationale behind triage recommendations, undermining medical trust and regulatory compliance.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=10
    )

    add_h2("1.2 Problem Statement")
    add_p(
        "Despite substantial advances in artificial intelligence and natural language processing, existing digital symptom assessment platforms suffer from three fundamental architectural and safety bottlenecks:",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=6
    )
    add_p(
        "1. Probabilistic Drift and LLM Hallucinations: Commercial symptom checkers and emerging Large Language Model (LLM) agents model patient presentations as unconstrained token generation tasks. Because deep probabilistic language models optimize for semantic plausibility rather than clinical invariant preservation, they are vulnerable to hallucinated medical reasoning, inconsistent classifications across identical presentations, and catastrophic downcoding of critical emergencies when prompted with atypical or negated symptom descriptions.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=6
    )
    add_p(
        "2. Rigid Failure Modes in Traditional Rule Engines: Conventional rule-based expert systems utilize hardcoded, static decision trees. While deterministic and reproducible, traditional decision trees fail to parse free-form conversational natural language, cannot disambiguate contextual symptom negations (e.g., 'cough but no fever or shortness of breath'), and cannot dynamically formulate targeted follow-up clarification questions.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=6
    )
    add_p(
        "3. Diagnostic Overreach and Regulatory Ambiguity: Prevailing commercial applications frequently venture into automated differential diagnosis and prescription suggestions. Providing unverified disease diagnoses or drug recommendations violates medical device regulations (such as FDA Software as a Medical Device - SaMD guidelines and EU Medical Device Regulation), exposing patients to improper self-medication and legal liability.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=10
    )

    add_h2("1.3 Objectives of the Study")
    add_p(
        "To resolve these critical bottlenecks, this research pursues the following concrete engineering and clinical objectives:",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=6
    )
    add_p("1. Objective 1 (Deterministic Clinical Rule Formulation): Formulate and curate an auditable corpus of 31 deterministic clinical triage rules across ten anatomical presentation categories grounded in authoritative guidelines (NICE, IAP, AHA).", space_before=3, space_after=3)
    add_p("2. Objective 2 (Two-Stage Safety Architecture): Develop an end-to-end two-stage architecture coupling an instantaneous deterministic Stage A red-flag screen with a contextual Stage B natural language understanding and clarification module.", space_before=3, space_after=3)
    add_p("3. Objective 3 (Mathematical Urgency Invariant Operator): Mathematically specify and implement an Urgency Invariant Operator U_final = min(U_Rule, U_SafetyNet, U_ML, U_LLM) guaranteeing zero statistical downgrade of emergency presentations.", space_before=3, space_after=3)
    add_p("4. Objective 4 (Dynamic Clinical Clarification Engine): Engineer an adaptive follow-up module generating targeted safety-critical questions (e.g., patient age, symptom onset, progression) capped to prevent user cognitive fatigue.", space_before=3, space_after=3)
    add_p("5. Objective 5 (Explainable Decision Support and Provenance): Implement an auditable explainability engine providing clinical rationales, guideline references, and explicit clinician review statuses without diagnostic or drug claims.", space_before=3, space_after=3)
    add_p("6. Objective 6 (Accessible Full-Stack Deployment): Deploy an accessible, responsive web application adhering to WCAG 2.1 AA accessibility standards featuring persistent emergency service contact integration (112 / 108).", space_before=3, space_after=10)

    add_h2("1.4 Scope of the Study")
    add_p(
        "The investigative scope of this research is defined by the following methodological boundaries:",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=6
    )
    add_p("• Non-Diagnostic Triage Focus: The system performs non-diagnostic, non-prescriptive urgency sorting strictly into 5 standardized urgency tiers. It explicitly does not output disease diagnoses, differential probabilities, medication names, or dosage recommendations.", space_before=3, space_after=3)
    add_p("• Clinical Guideline Corpus: Rules are derived from published guidelines from NICE, IAP, and AHA, covering cardiovascular, respiratory, neurological, pediatric, gastrointestinal, systemic, and environmental emergency presentations.", space_before=3, space_after=3)
    add_p("• Privacy and Data Governance: Patient symptom free-text is processed transiently in memory. Raw symptom text storage is disabled by default, requiring explicit research opt-in with Argon2id cryptographic hashing.", space_before=3, space_after=3)
    add_p("• Evaluation Testbed: Quantitative validation is conducted across 100 standardized multi-symptom clinical benchmark scenarios spanning Levels 1 through 5, systematically evaluating under-triage rates and computational latency.", space_before=3, space_after=10)

    add_h2("1.5 Significance of the Study")
    add_p(
        "The significance of this study spans clinical safety, software engineering, and digital healthcare governance:",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=6
    )
    add_p("• Clinical Safety Impact: Enforcing a mathematical urgency invariant eliminates critical under-triage in digital pre-primary assessments, safeguarding presenting patients from fatal triage downcoding.", space_before=3, space_after=3)
    add_p("• Architectural Innovation: Demonstrates that hybridizing deterministic expert rules with probabilistic NLP combines the transparency and provable safety of symbolic AI with the flexibility of modern language parsing.", space_before=3, space_after=3)
    add_p("• Regulatory and Ethical Alignment: By strictly adhering to non-diagnostic urgency sorting and transparent rule provenance, SafeTriage provides a blueprint for legally compliant, ethically auditable medical AI decision-support.", space_before=3, space_after=10)

    add_h2("1.6 Research Questions")
    add_p("This dissertation investigates four formal Research Questions (RQs):", space_before=4, space_after=6)
    add_p("• RQ1 (Triage Accuracy and Efficacy): Does a hybrid safety-constrained triage architecture achieve competitive classification accuracy compared to unconstrained statistical models while maintaining clinical validity?", space_before=3, space_after=3)
    add_p("• RQ2 (Ablation Sensitivity): What are the individual contributions of Stage A deterministic screening, Stage B contextual follow-up, and the monotonic invariant operator?", space_before=3, space_after=3)
    add_p("• RQ3 (Explainability and Auditability): Can explicit rule provenance and rationale rendering provide satisfactory clinical auditability without relying on opaque post-hoc feature heatmaps?", space_before=3, space_after=3)
    add_p("• RQ4 (Provable Under-Triage Elimination): Does the mathematical invariant operator successfully achieve 0.00% under-triage across all evaluated emergency benchmark presentations?", space_before=3, space_after=10)

    add_h2("1.7 Organization of the Report")
    add_p("The remainder of this research project report is structured as follows:", space_before=4, space_after=6)
    add_p("• Chapter 2 (Literature Review): Surveys the clinical triage domain, reviews prior rule-based and deep learning CDSS architectures, analyzes LLM safety hazards, and establishes the formal gap analysis.", space_before=3, space_after=3)
    add_p("• Chapter 3 (Methodology): Details the relational database schema, UML specifications (Use Case, DFD, Class, Activity, ER), mathematical invariant operator, and the two-stage triage architecture.", space_before=3, space_after=3)
    add_p("• Chapter 4 (Implementation): Documents the software development stack, rule corpus engineering, backend FastAPI implementation, Next.js frontend architecture, and core code algorithms.", space_before=3, space_after=3)
    add_p("• Chapter 5 (Results and Discussions): Details empirical benchmark evaluations, latency telemetry, architectural ablations, test suite execution, and clinical case study analyses.", space_before=3, space_after=3)
    add_p("• Chapter 6 (Conclusion and Recommendations): Summarizes primary research milestones, addresses architectural limitations, provides actionable future scope recommendations, and concludes the study.", space_before=3, space_after=10)

    add_page_break()

    # =========================================================================
    # CHAPTER 2: LITERATURE REVIEW (Matching OCR Pages 19-24)
    # =========================================================================
    add_h1("Chapter 2")
    add_h1("Literature Review")

    add_h2("2.1 Overview of the Domain")
    add_p(
        "Clinical triage systems originated in military battlefield medicine to allocate scarce surgical resources efficiently. In contemporary civilian healthcare, emergency departments universally utilize standardized triage protocols to manage acute patient flow. The Manchester Triage System (MTS) employs standardized flowcharts with specific discriminators (e.g., airway compromise, severe pain) to allocate patients into five color-coded urgency bands: Immediate (Red), Very Urgent (Orange), Urgent (Yellow), Standard (Green), and Non-Urgent (Blue) [3]. Similarly, the Emergency Severity Index (ESI) evaluates patient acuity and anticipated healthcare resource utilization [2].",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=8
    )
    add_p(
        "With the growth of digital health platforms, digital pre-triage tools have been introduced to assist patients in selecting appropriate care pathways—such as calling emergency services, visiting an urgent care clinic, booking an outpatient consultation, or initiating self-care. However, translating emergency room triage logic into automated digital self-assessment software poses unique clinical, legal, and engineering challenges.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=8
    )

    add_h2("2.2 Review of Related Work")
    add_p(
        "Automated clinical decision-support systems have progressed through three primary paradigms: rule-based expert systems, statistical machine learning models, and contemporary generative AI language models.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=6
    )

    add_h3("2.2.1 Rule-Based and Heuristic Clinical Decision Support Systems")
    add_p(
        "Early biomedical artificial intelligence relied heavily on expert heuristic systems such as MYCIN and INTERNIST-1, which modeled medical reasoning as sets of deterministic production rules. Modern computerized clinical guidelines (e.g., NHS 111 online decision trees) continue to utilize structured question-and-answer trees. While these systems offer absolute reproducibility and verifiable compliance with established medical guidelines, they are brittle: they cannot interpret unstructured natural language, struggle with contradictory user inputs, and present rigid, lengthy questionnaires that induce user abandonment [4, 5].",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=6
    )

    add_h3("2.2.2 Machine Learning and Statistical NLP in Symptom Stratification")
    add_p(
        "To process conversational natural language, researchers introduced supervised machine learning classifiers (Support Vector Machines, Random Forests, Gradient Boosted Trees) trained on electronic medical records and extracted biomedical concepts [6]. While statistical classifiers effectively map symptom keywords to broad clinical categories, they operate as purely correlational models. They lack explicit awareness of clinical urgency constraints and can easily misclassify rare, high-stakes presentations when trained on imbalanced real-world data [7].",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=6
    )

    add_h3("2.2.3 Generative AI, Large Language Models, and the Hallucination Hazard")
    add_p(
        "Recent investigations have evaluated General-Purpose and Medical Large Language Models (LLMs) such as Med-PaLM and GPT-4 for clinical dialogue and triage assistance [8, 9]. While LLMs demonstrate remarkable linguistic fluency and clinical knowledge retrieval, medical informatics literature has uncovered alarming safety vulnerabilities. In a comprehensive audit of LLM-based triage responses, researchers observed frequent 'hallucinations', where models invented medical contraindications or asserted false reassurance in the presence of acute ischemic symptoms [10]. Most critically, unconstrained probabilistic generation allows catastrophic downcoding: slight phrasing modifications or the mention of mild co-occurring symptoms frequently led LLMs to downgrade acute myocardial infarction presentations to routine outpatient consultations [11].",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=6
    )

    add_h3("2.2.4 Explainability, Auditability, and Safety Invariants in Medical AI")
    add_p(
        "The black-box nature of deep neural networks has spurred extensive research in Explainable AI (XAI). In healthcare, post-hoc saliency methods (SHAP, Integrated Gradients) provide feature importance visualizations. However, research demonstrates that post-hoc explanations often diverge from actual model reasoning and provide no formal guarantee that the underlying decision followed clinical protocol [12]. In contrast, safety-critical systems in aerospace and industrial robotics enforce formal runtime safety invariants that actively bound model decisions. Applying formal safety invariants to digital clinical triage represents an emerging, highly promising frontier in medical software engineering.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=10
    )

    add_h2("2.3 Existing Methodologies and Commercial Triage Tools")
    add_p(
        "Table 2.1 presents a comprehensive comparative synthesis of existing clinical symptom assessment platforms, documenting their underlying architecture, triage methodology, explainability, and primary limitations.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=6
    )

    # TABLE 2.1
    t21_data = [
        ["System / Platform", "Core Architecture", "Safety & Triage Method", "Observed Limitations"],
        ["Babyl / Babylon Health [4]", "Probabilistic Graphical Model + Bayesian Trees", "Statistical disease likelihood scoring", "Diagnostic overreach; criticized by clinicians for missed emergencies."],
        ["Ada Health [5]", "Bayesian Network + Dynamic Questionnaire", "Dynamic probabilistic disease matching", "Lengthy 20+ question flows; black-box probability calculation."],
        ["Buoy Health [6]", "Rule-Assisted Statistical NLP", "Correlational symptom clustering", "Requires rigid search terms; potential under-triage on atypical chest pain."],
        ["K-Health [7]", "Supervised Deep Learning on EMR Data", "Historical cohort patient matching", "Prone to historic demographic bias; lacks deterministic red-flag guarantees."],
        ["Unconstrained LLMs [8, 9]", "Generative Pre-trained Transformers", "Unconstrained next-token generation", "Severe hallucination risk; non-deterministic downcoding; no audit trail."],
        ["SafeTriage (Proposed)", "Deterministic Rules + Contextual NLP + Safety Invariant", "Two-Stage Invariant Pipeline: U_final = min(Rules, SafetyNet, ML, LLM)", "Unified framework guaranteeing 0.00% under-triage with full provenance."]
    ]
    tbl21 = doc.add_table(rows=len(t21_data), cols=4)
    tbl21.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl21)
    for r_idx, row in enumerate(t21_data):
        for c_idx, val in enumerate(row):
            cell = tbl21.rows[r_idx].cells[c_idx]
            p = cell.paragraphs[0]
            p.text = val
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            set_cell_margins(cell, 80, 80, 100, 100)
            if r_idx == 0:
                p.runs[0].bold = True
                set_cell_background(cell, "F2F2F2")

    add_p("Table 2.1: Comparative Analysis Matrix of Existing Clinical Symptom Triage Systems", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=12, italic=True, size=10)

    add_h2("2.4 Gap Analysis")
    add_p("Critical synthesis of prior literature reveals three unresolved research gaps:", space_before=4, space_after=6)
    add_p("1. Research Gap 1 (Probabilistic Vulnerability in Critical Care): Existing statistical and generative AI triage systems lack hard, non-negotiable safety boundaries. They allow probabilistic models to override deterministic emergency protocols, leading to life-threatening under-triage.", space_before=3, space_after=3)
    add_p("2. Research Gap 2 (The Flexibility vs. Safety Trade-Off): Previous architectures forced a compromise between rigid, unengaging rule trees and flexible but dangerous generative models. A hybrid system combining natural language flexibility with provable deterministic safety has not been realized.", space_before=3, space_after=3)
    add_p("3. Research Gap 3 (Lack of Explainable Clinical Provenance): Current platforms generate opacity: they either return a bare urgency score or invent convincing but unverifiable narrative text. Transparent attribution connecting urgency levels to specific clinical guidelines and review statuses is absent.", space_before=3, space_after=8)

    # TABLE 2.2
    t22_data = [
        ["Research Dimension", "Current State & Limitation", "Proposed SafeTriage Technical Innovation"],
        ["Emergency Safety Modeling", "Statistical models can downcode emergencies under noisy input.", "Stage A deterministic red-flag screening with mathematical invariant override."],
        ["Architectural Coupling", "Loose coupling or unconstrained end-to-end deep learning.", "Strict two-stage pipeline enforcing U_final = min(U_Rule, U_SafetyNet, U_ML, U_LLM)."],
        ["Decision Explainability", "Opaque post-hoc heatmaps or hallucinated LLM text.", "Explicit rule provenance rendering, source guideline tracing, and audit logs."],
        ["Data Governance & Ethics", "User symptom logs stored indefinitely for ad profiling.", "Privacy-by-design: transient memory processing, Argon2id hashing, explicit opt-in."]
    ]
    tbl22 = doc.add_table(rows=len(t22_data), cols=3)
    tbl22.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl22)
    for r_idx, row in enumerate(t22_data):
        for c_idx, val in enumerate(row):
            cell = tbl22.rows[r_idx].cells[c_idx]
            p = cell.paragraphs[0]
            p.text = val
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            set_cell_margins(cell, 80, 80, 100, 100)
            if r_idx == 0:
                p.runs[0].bold = True
                set_cell_background(cell, "F2F2F2")

    add_p("Table 2.2: Summary of Research Gaps and Proposed SafeTriage Technical Innovations", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=12, italic=True, size=10)

    add_page_break()

    # =========================================================================
    # CHAPTER 3: METHODOLOGY (Matching OCR Pages 25-30)
    # =========================================================================
    add_h1("Chapter 3")
    add_h1("Methodology")

    add_h2("3.1 Research Design (Database Design / UML Diagrams)")
    add_p(
        "This research follows a rigorous empirical and architectural design structured around safety-constrained software engineering, clinical guideline formalization, and quantitative benchmark evaluation. To bridge clinical triage medicine with reliable software engineering, the system architecture couples standardized relational medical data persistence with comprehensive Unified Modeling Language (UML) specifications.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=8
    )

    add_h3("3.1.1 Relational Database Design and Integrity Constraints")
    add_p(
        "To manage user accounts, authentication credentials, clinical rules, assessment sessions, and audit telemetry systematically while maintaining complete patient privacy, a normalized relational database in Third Normal Form (3NF) was designed. Table 3.1 and Table 3.2 present the consolidated relational schema, data types, integrity constraints, and functional descriptions.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=6
    )

    # TABLE 3.1
    t31_data = [
        ["Attribute", "Data Type", "Constraint", "Clinical / Engineering Description"],
        ["Entity 1: users (User Authentication and Role Profiles)", "", "", ""],
        ["id", "VARCHAR(36)", "PRIMARY KEY", "Unique UUID identifying registered user or researcher."],
        ["email", "VARCHAR(255)", "UNIQUE, NOT NULL", "Anonymized user contact identifier."],
        ["password_hash", "VARCHAR(255)", "NOT NULL", "Cryptographic Argon2id salted credential hash."],
        ["role", "VARCHAR(20)", "CHECK(role IN ('user', 'researcher'))", "Role-Based Access Control (RBAC) permission level."],
        ["created_at", "DATETIME", "NOT NULL, DEFAULT NOW", "Timestamp of initial account registration."],
        ["Entity 2: user_privacy_preferences (Privacy and Opt-In State)", "", "", ""],
        ["user_id", "VARCHAR(36)", "PRIMARY KEY, FOREIGN KEY", "References users(id) ON DELETE CASCADE."],
        ["raw_text_opt_in", "BOOLEAN", "NOT NULL, DEFAULT FALSE", "Explicit consent for raw symptom text retention."],
        ["data_retention_days", "INTEGER", "CHECK(days >= 0)", "Configured retention window before automated purge."]
    ]
    tbl31 = doc.add_table(rows=len(t31_data), cols=4)
    tbl31.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl31)
    for r_idx, row in enumerate(t31_data):
        for c_idx, val in enumerate(row):
            cell = tbl31.rows[r_idx].cells[c_idx]
            p = cell.paragraphs[0]
            p.text = val
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            set_cell_margins(cell, 80, 80, 100, 100)
            if r_idx == 0 or val.startswith("Entity"):
                p.runs[0].bold = True
                set_cell_background(cell, "F2F2F2" if r_idx == 0 else "EAEAEA")

    add_p("Table 3.1: Consolidated Relational Database Schema (3NF) – Users, Sessions, and Opt-In", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=10, italic=True, size=10)

    # TABLE 3.2
    t32_data = [
        ["Attribute", "Data Type", "Constraint", "Clinical / Engineering Description"],
        ["Entity 3: triage_rules (Deterministic Clinical Rule Corpus)", "", "", ""],
        ["rule_id", "VARCHAR(64)", "PRIMARY KEY", "Unique rule identifier (e.g., RULE_CHEST_001)."],
        ["condition_category", "VARCHAR(64)", "NOT NULL", "Clinical category (cardiac, respiratory, neuro, etc.)."],
        ["urgency_level", "INTEGER", "CHECK(level IN (1, 2, 3, 4, 5))", "Assigned triage urgency tier (1 = Emergency, 5 = Non-Urgent)."],
        ["required_symptoms", "JSON", "NOT NULL", "List of mandatory positive clinical concept codes."],
        ["clinical_rationale", "TEXT", "NOT NULL", "Evidence-based justification for triage level."],
        ["guideline_source", "VARCHAR(128)", "NOT NULL", "Authoritative guideline citation (NICE, IAP, AHA)."],
        ["verified", "BOOLEAN", "NOT NULL, DEFAULT FALSE", "Clinician board review sign-off status."],
        ["Entity 4: assessment_records (Clinical Triage Audit Sessions)", "", "", ""],
        ["id", "VARCHAR(36)", "PRIMARY KEY", "Unique UUID identifying clinical assessment run."],
        ["user_id", "VARCHAR(36)", "FOREIGN KEY, NULLABLE", "References users(id) ON DELETE SET NULL (guest support)."],
        ["final_urgency_level", "INTEGER", "CHECK(level IN (1, 2, 3, 4, 5))", "Final safety-invariant resolved urgency score."],
        ["determining_component", "VARCHAR(64)", "NOT NULL", "Component setting final level (Rule, SafetyNet, ML, LLM)."],
        ["under_triage_flag", "BOOLEAN", "NOT NULL, DEFAULT FALSE", "Audit flag indicating potential safety breach (must be 0)."],
        ["created_at", "DATETIME", "NOT NULL, DEFAULT NOW", "Session execution timestamp for audit logging."]
    ]
    tbl32 = doc.add_table(rows=len(t32_data), cols=4)
    tbl32.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl32)
    for r_idx, row in enumerate(t32_data):
        for c_idx, val in enumerate(row):
            cell = tbl32.rows[r_idx].cells[c_idx]
            p = cell.paragraphs[0]
            p.text = val
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            set_cell_margins(cell, 80, 80, 100, 100)
            if r_idx == 0 or val.startswith("Entity"):
                p.runs[0].bold = True
                set_cell_background(cell, "F2F2F2" if r_idx == 0 else "EAEAEA")

    add_p("Table 3.2: Relational Database Schema (3NF) – Clinical Rules and Assessment Audit Logs", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=12, italic=True, size=10)

    add_h3("3.1.2 System UML Diagrams")
    add_p("To formalize the object-oriented architecture, operational interactions, and data transformations, five standardized UML diagrams were engineered.", space_before=4, space_after=6)

    add_p("Use Case Modeling", bold=True, space_before=4, space_after=2)
    add_p(
        "The system exposes four distinct operational actor roles: (1) Presenting Patient, who inputs symptom narratives, answers clarification questions, views urgency levels and emergency contacts (112/108), and manages personal data deletion; (2) Triage Clinician / Emergency Nurse, who reviews rule trigger rationales, audits assessment explanations, and executes emergency overrides; (3) Research Scientist, who evaluates benchmark datasets, inspects ablation metrics, and validates model accuracy; and (4) System Administrator, who manages rule deployments, monitors audit telemetry, and verifies zero-under-triage invariants.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=6
    )
    add_p("Figure 3.1: SafeTriage Clinical Decision Support System Use Case Diagram", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=8, italic=True, size=10)

    add_p("Data Flow Architecture (DFD Level 1)", bold=True, space_before=4, space_after=2)
    add_p(
        "The data flow architecture organizes data transformations across six distinct stages: (1) Symptom Narrative Ingestion; (2) Stage A Instantaneous Rule Evaluation; (3) Negation Detection and Clinical Concept Extraction; (4) Dynamic Clarification Generation; (5) Safety Invariant Resolution; and (6) Explainable Telemetry Rendering.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=6
    )
    add_p("Figure 3.2: Data Flow Diagram (DFD Level 1) of the Proposed SafeTriage Architecture", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=8, italic=True, size=10)

    add_p("UML Class Diagram", bold=True, space_before=4, space_after=2)
    add_p(
        "The object-oriented software architecture comprises nine primary classes: SymptomPresentation, RuleEngine, TriageRule, NLPExtractor, SafetyNet, FollowUpEngine, InvariantResolver, Explainer, and AssessmentRecord.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=6
    )
    add_p("Figure 3.3: UML Class Diagram of the Proposed SafeTriage Hybrid System", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=8, italic=True, size=10)

    add_p("UML Activity Diagram", bold=True, space_before=4, space_after=2)
    add_p(
        "The activity diagram partitions execution across three swimlanes: Patient Client, Stage A Fast-Path Engine, and Stage B Reasoning Engine. Immediate Level 1 triggers short-circuit directly to display the emergency modal and 112/108 tap-to-call links.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=6
    )
    add_p("Figure 3.4: UML Activity Diagram for Two-Stage Triage and Invariant Resolution", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=8, italic=True, size=10)

    add_p("Entity-Relationship (ER) Diagram", bold=True, space_before=4, space_after=2)
    add_p(
        "The ER diagram formalizes the structural database relationships between USERS (1:1) USER_PRIVACY_PREFERENCES, USERS (1:M) ASSESSMENT_RECORDS, and ASSESSMENT_RECORDS (M:M) TRIAGE_RULES via TRIGGERED_RULE_AUDIT bridge entities.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=6
    )
    add_p("Figure 3.5: Entity-Relationship (ER) Diagram for the SafeTriage Clinical Database", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=12, italic=True, size=10)

    add_h2("3.2 Data Sources and Clinical Guidelines")
    add_p(
        "Deterministic triage rules are curated from evidence-based clinical practice guidelines published by recognized medical authorities: National Institute for Health and Care Excellence (NICE) Clinical Guidelines (UK), Indian Academy of Pediatrics (IAP) Pediatric Emergency Triage Protocols, and American Heart Association (AHA) Acute Coronary Syndrome and Stroke Guidelines. In compliance with strict academic integrity, all rules carry a verified=false attribute pending formal clinical board sign-off.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=8
    )

    add_h2("3.3 Tools and Technologies Used")
    add_p("Table 3.3 and Table 3.4 detail the hardware and software technology stack used in development and benchmarking.", space_before=4, space_after=6)

    # TABLE 3.3
    t33_data = [
        ["Subsystem", "Component / Specification", "Operational Function"],
        ["Host Processor", "Intel / AMD Multi-Core x86_64 CPU", "FastAPI asynchronous service execution and NLP tokenization."],
        ["System Memory", "16.0 GB DDR4/DDR5 RAM", "In-memory rule indexing and fast pipeline execution."],
        ["Primary Storage", "512 GB PCIe NVMe M.2 SSD", "High-throughput rule loading and audit persistence."],
        ["Operating System", "Microsoft Windows 11 (64-bit)", "Primary development, testing, and deployment platform."]
    ]
    tbl33 = doc.add_table(rows=len(t33_data), cols=3)
    tbl33.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl33)
    for r_idx, row in enumerate(t33_data):
        for c_idx, val in enumerate(row):
            cell = tbl33.rows[r_idx].cells[c_idx]
            p = cell.paragraphs[0]
            p.text = val
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            set_cell_margins(cell, 80, 80, 100, 100)
            if r_idx == 0:
                p.runs[0].bold = True
                set_cell_background(cell, "F2F2F2")

    add_p("Table 3.3: Hardware Testbed and Computational Specifications", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=10, italic=True, size=10)

    # TABLE 3.4
    t34_data = [
        ["Framework / Tool", "Version", "Application in SafeTriage Architecture"],
        ["Python", ">= 3.11", "Core backend runtime and scientific data processing."],
        ["FastAPI", ">= 0.100.0", "Asynchronous RESTful API framework and OpenAPI documentation."],
        ["SQLAlchemy / SQLite", ">= 2.0.0", "Database ORM and persistent audit log storage."],
        ["Argon2id & PyJWT", ">= 23.1.0", "Cryptographic password hashing and stateless JWT session auth."],
        ["Next.js (App Router)", "14.x", "Full-stack React client framework with SSR and responsive UI."],
        ["TailwindCSS & Lucide", ">= 3.4.0", "Accessible component styling and clinical iconography."],
        ["Axe-Core", ">= 4.8.0", "Automated WCAG 2.1 AA accessibility auditing suite."]
    ]
    tbl34 = doc.add_table(rows=len(t34_data), cols=3)
    tbl34.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl34)
    for r_idx, row in enumerate(t34_data):
        for c_idx, val in enumerate(row):
            cell = tbl34.rows[r_idx].cells[c_idx]
            p = cell.paragraphs[0]
            p.text = val
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            set_cell_margins(cell, 80, 80, 100, 100)
            if r_idx == 0:
                p.runs[0].bold = True
                set_cell_background(cell, "F2F2F2")

    add_p("Table 3.4: Software Engineering, Natural Language Processing, and Web Stack", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=12, italic=True, size=10)

    add_h2("3.4 Dataset Description and Clinical Benchmark Scenarios")
    add_p(
        "To rigorously benchmark triage accuracy and safety invariant enforcement, a standardized benchmark suite of N = 100 clinical scenarios was compiled. Each scenario encapsulates a realistic patient symptom presentation, associated demographic parameters (age, biological sex), explicit negation tokens, and consensus ground-truth urgency classifications.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=6
    )

    # TABLE 3.5
    t35_data = [
        ["Urgency Tier", "Clinical Designation", "Target Response Time", "Benchmark Count (N = 100)"],
        ["Level 1", "Resuscitation / Immediate", "Immediate (0 minutes) – Call 112 / 108", "25 scenarios (25%)"],
        ["Level 2", "Emergency / Very Urgent", "< 15 minutes – Emergency Department", "25 scenarios (25%)"],
        ["Level 3", "Urgent / Critical Care", "< 60 minutes – Urgent Care Center", "20 scenarios (20%)"],
        ["Level 4", "Less Urgent / Semi-Urgent", "Same-day consultation / Clinic", "15 scenarios (15%)"],
        ["Level 5", "Non-Urgent / Self-Care", "Scheduled primary care / Home care", "15 scenarios (15%)"]
    ]
    tbl35 = doc.add_table(rows=len(t35_data), cols=4)
    tbl35.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl35)
    for r_idx, row in enumerate(t35_data):
        for c_idx, val in enumerate(row):
            cell = tbl35.rows[r_idx].cells[c_idx]
            p = cell.paragraphs[0]
            p.text = val
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            set_cell_margins(cell, 80, 80, 100, 100)
            if r_idx == 0:
                p.runs[0].bold = True
                set_cell_background(cell, "F2F2F2")

    add_p("Table 3.5: Five-Level Urgency Triage Scale Grounded in ESI, MTS, and CTAS Protocols", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=12, italic=True, size=10)

    add_h2("3.5 Algorithm and Architectural Model Selection")
    add_p(
        "The mathematical and algorithmic foundation of SafeTriage integrates five core functional modules:",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=6
    )

    add_h3("3.5.1 Stage A: Deterministic Rule Engine and Red-Flag Safety Net")
    add_p(
        "Stage A performs high-speed screening directly against 31 curated YAML rules. If any red-flag rule (Level 1) triggers, execution halts immediately and produces an emergency response without waiting for secondary statistical NLP models.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=3, space_after=6
    )

    add_h3("3.5.2 Stage B: Contextual NLP Extractor and Follow-Up Engine")
    add_p(
        "Stage B parses free-text presentation using regular expressions and negation-aware entity extraction. It identifies positive clinical concepts while discarding negated entities (e.g., 'no chest pain'). The FollowUpEngine evaluates missing critical parameters (e.g., age, onset duration) and dynamically poses up to 3 targeted clarification questions.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=3, space_after=6
    )

    add_h3("3.5.3 Mathematical Urgency Invariant Operator")
    add_p(
        "To guarantee that probabilistic NLP models or external adapters never downcode a life-threatening emergency, the final urgency is resolved through a monotonic invariant operator:",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=3, space_after=6
    )
    add_p("U_final = min( U_Rule, U_SafetyNet, U_ML, U_LLM )    (3.1)", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, space_before=6, space_after=6)
    add_p(
        "Because 1 represents the most acute emergency and 5 represents non-urgent care, the minimum operator ensures that the highest clinical urgency always dominates the final outcome.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=3, space_after=6
    )

    add_h3("3.5.4 Explainable Decision Support and Provenance Tracing")
    add_p(
        "The Explainer module constructs transparent audit rationales detailing which clinical rule triggered, the source guideline, review status, and safe emergency instructions without diagnostic speculation or medication advice.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=3, space_after=6
    )

    add_h3("3.5.5 Research Privacy Engine and Anonymized Storage")
    add_p(
        "User privacy is enforced by default. Symptom narratives are processed in volatile memory. Only structured concept codes and assigned urgency tiers are logged unless the user explicitly opts in to research storage.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=3, space_after=12
    )

    add_page_break()

    # =========================================================================
    # CHAPTER 4: IMPLEMENTATION (Matching OCR Pages 31-36)
    # =========================================================================
    add_h1("Chapter 4")
    add_h1("Implementation")

    add_h2("4.1 Data Ingestion and Clinical Rule Preprocessing")
    add_p(
        "Clinical rules are structured as declarative YAML documents. During application startup, the RuleEngine loads all rules into an indexed memory store, pre-compiling regular expressions for sub-millisecond evaluation.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=8
    )

    add_h2("4.2 Experimental Setup / Testbed / Development Environment")
    add_p(
        "Development and benchmarking were executed on a dedicated multi-core workstation. The backend exposes asynchronous RESTful endpoints via FastAPI running with Uvicorn workers. The frontend runs as a Next.js 14 client communicating via typed HTTP interfaces.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=6
    )
    add_p("Figure 4.1: SafeTriage Research Project Execution Schedule and Milestones (Gantt Chart)", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=8, italic=True, size=10)

    # TABLE 4.1 & 4.2
    t41_data = [
        ["Hyperparameter / Setting", "Configured Value", "Operational Rationale"],
        ["FastAPI Port", "8000", "Dedicated backend microservice communication port."],
        ["Frontend Port", "3000", "Next.js client-side interactive rendering port."],
        ["Max Follow-Up Questions", "3 questions", "Prevents user cognitive fatigue while capturing critical data."],
        ["JWT Token Expiry", "60 minutes", "Security window for authenticated researcher sessions."],
        ["Emergency Service Codes", "112 / 108", "Direct tap-to-call emergency lines for rapid ambulance dispatch."]
    ]
    tbl41 = doc.add_table(rows=len(t41_data), cols=3)
    tbl41.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl41)
    for r_idx, row in enumerate(t41_data):
        for c_idx, val in enumerate(row):
            cell = tbl41.rows[r_idx].cells[c_idx]
            p = cell.paragraphs[0]
            p.text = val
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            set_cell_margins(cell, 80, 80, 100, 100)
            if r_idx == 0:
                p.runs[0].bold = True
                set_cell_background(cell, "F2F2F2")

    add_p("Table 4.1: System Configuration Parameters and Operational Thresholds", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=12, italic=True, size=10)

    add_h2("4.3 Implementation of Proposed Approach")
    add_p("The complete implementation comprises modular Python backend components and Next.js frontend interfaces:", space_before=4, space_after=6)

    add_h3("4.3.1 Deterministic Rule Engine and Red-Flag Evaluator")
    add_p(
        "Listing 4.1 shows the core deterministic rule evaluation algorithm matching symptom presentations against structured YAML conditions.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=3, space_after=4
    )
    
    code_listing_1 = """def evaluate_stage_a(presentation: SymptomPresentation) -> Optional[TriageResult]:
    for rule in self.rules:
        if rule.urgency_level == 1 and rule.matches(presentation):
            return TriageResult(
                urgency_level=1,
                triggered_rule=rule.id,
                rationale=rule.rationale,
                emergency_override=True
            )
    return None"""
    p_code1 = doc.add_paragraph(code_listing_1)
    p_code1.style.font.name = 'Courier New'
    p_code1.style.font.size = Pt(9.5)
    p_code1.paragraph_format.line_spacing = 1.15
    add_p("Listing 4.1: Deterministic Stage A Red-Flag Evaluator", align=WD_ALIGN_PARAGRAPH.CENTER, italic=True, size=10, space_after=8)

    add_h3("4.3.2 Two-Stage Triage Pipeline and Invariant Safety Resolver")
    add_p(
        "Listing 4.2 implements the mathematical Urgency Invariant Operator resolving multi-component evaluations.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=3, space_after=4
    )
    code_listing_2 = """def resolve_invariant(u_rule: int, u_safety_net: int, u_ml: int, u_llm: int) -> int:
    # Mathematical Invariant: U_final = min(U_Rule, U_SafetyNet, U_ML, U_LLM)
    # Lower integer indicates higher clinical acuity (Level 1 = Emergency)
    final_urgency = min(u_rule, u_safety_net, u_ml, u_llm)
    assert final_urgency <= u_rule, "Safety Invariant Violated: Model downgraded rule urgency!"
    return final_urgency"""
    p_code2 = doc.add_paragraph(code_listing_2)
    p_code2.style.font.name = 'Courier New'
    p_code2.style.font.size = Pt(9.5)
    p_code2.paragraph_format.line_spacing = 1.15
    add_p("Listing 4.2: Mathematical Urgency Invariant Resolver", align=WD_ALIGN_PARAGRAPH.CENTER, italic=True, size=10, space_after=12)

    add_page_break()

    # =========================================================================
    # CHAPTER 5: RESULTS AND DISCUSSIONS (Matching OCR Pages 37-48)
    # =========================================================================
    add_h1("Chapter 5")
    add_h1("Results and Discussions")

    add_h2("5.1 Observations and Experimental Results")
    add_p(
        "Experimental validation of SafeTriage was conducted across the standardized 100-case clinical benchmark suite. System latency, classification accuracy, safety invariant compliance, and explainability provenance were rigorously evaluated.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=6
    )
    add_p("Figure 5.1: System Response Latency Distribution across Stage A and Stage B Processing", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=8, italic=True, size=10)

    # TABLE 5.2
    t52_data = [
        ["Triage Urgency Tier", "Clinical Classification", "SafeTriage Accuracy (%)", "Under-Triage Rate (%)", "Over-Triage Rate (%)"],
        ["Level 1", "Immediate Resuscitation", "100.00%", "0.00%", "0.00%"],
        ["Level 2", "Emergency / Very Urgent", "96.00%", "0.00%", "4.00%"],
        ["Level 3", "Urgent / Critical Care", "90.00%", "0.00%", "10.00%"],
        ["Level 4", "Less Urgent / Semi-Urgent", "93.33%", "0.00%", "6.67%"],
        ["Level 5", "Non-Urgent / Self-Care", "86.67%", "0.00%", "13.33%"],
        ["Overall Cohort", "Consolidated 100 Cases", "94.00%", "0.00%", "6.00%"]
    ]
    tbl52 = doc.add_table(rows=len(t52_data), cols=5)
    tbl52.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl52)
    for r_idx, row in enumerate(t52_data):
        for c_idx, val in enumerate(row):
            cell = tbl52.rows[r_idx].cells[c_idx]
            p = cell.paragraphs[0]
            p.text = val
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            set_cell_margins(cell, 80, 80, 100, 100)
            if r_idx == 0 or r_idx == len(t52_data) - 1:
                p.runs[0].bold = True
                set_cell_background(cell, "F2F2F2")

    add_p("Table 5.2: Comprehensive Benchmark Performance and Per-Urgency-Level Evaluation", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=12, italic=True, size=10)

    add_h2("5.2 Performance and Comparative Analysis")
    add_p(
        "As demonstrated in Table 5.2, SafeTriage achieved an extraordinary safety milestone: exactly 0.00% under-triage across all evaluated presentations. Over-triage was conservatively contained at 6.00%, ensuring that in cases of clinical ambiguity, the system defaults safely to higher caution without overwhelming emergency services.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=8
    )

    add_h3("5.2.2 Research Question 2 (RQ2): Systematic Architectural Ablation Study")
    add_p(
        "To quantify the individual safety and accuracy contributions of each architectural tier, four controlled ablation variants were evaluated. Table 5.3 summarizes the experimental outcomes.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=6
    )

    # TABLE 5.3
    t53_data = [
        ["Ablation Variant", "Architectural Configuration", "Overall Accuracy (%)", "Under-Triage Rate (%)", "Safety Invariant"],
        ["Variant 1: Rule-Only", "Stage A deterministic rules only; no NLP follow-up.", "84.00%", "0.00%", "Enforced"],
        ["Variant 2: ML-Only", "Statistical NLP classifier only; no rules.", "88.00%", "8.00%", "Disabled (Dangerous)"],
        ["Variant 3: Unconstrained Hybrid", "Rules + ML without monotonic min() invariant.", "91.00%", "5.00%", "Disabled (Violated)"],
        ["Variant 4: SafeTriage (Full)", "Two-stage pipeline + FollowUp + Invariant Operator.", "94.00%", "0.00%", "Strictly Enforced"]
    ]
    tbl53 = doc.add_table(rows=len(t53_data), cols=5)
    tbl53.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl53)
    for r_idx, row in enumerate(t53_data):
        for c_idx, val in enumerate(row):
            cell = tbl53.rows[r_idx].cells[c_idx]
            p = cell.paragraphs[0]
            p.text = val
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            set_cell_margins(cell, 80, 80, 100, 100)
            if r_idx == 0 or r_idx == len(t53_data) - 1:
                p.runs[0].bold = True
                set_cell_background(cell, "F2F2F2")

    add_p("Table 5.3: Systematic Architectural Ablation Study on Benchmark Scenarios", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=12, italic=True, size=10)

    add_h2("5.3 System Testing and Verification Suite")
    add_p(
        "To guarantee complete software robustness and clinical integrity, a formal automated verification suite comprising 12 test cases was executed. Table 5.5 details the test outcomes.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=6
    )

    # TABLE 5.5
    t55_data = [
        ["Test ID", "Subsystem Under Test", "Test Description", "Pass Criterion", "Result"],
        ["TC01", "Rule Engine", "Stage A red-flag instant match", "Trigger Level 1 in < 5 ms", "PASS"],
        ["TC02", "NLP Extractor", "Negation handling ('no chest pain')", "Chest pain marked negated", "PASS"],
        ["TC03", "Invariant Resolver", "Monotonic min() operator enforcement", "Final urgency <= rule urgency", "PASS"],
        ["TC04", "FollowUp Engine", "Dynamic clarification cap", "Max 3 questions presented", "PASS"],
        ["TC05", "Emergency Modal", "Level 1 immediate alert rendering", "112/108 tap-to-call links visible", "PASS"],
        ["TC06", "Privacy Engine", "Raw text opt-in default off", "Raw text not saved to DB", "PASS"],
        ["TC07", "Auth / RBAC", "Argon2id hashing & researcher route", "HTTP 403 on unauthorized access", "PASS"],
        ["TC08", "Axe-Core Audit", "WCAG 2.1 AA accessibility scan", "0 automated accessibility violations", "PASS"],
        ["TC09", "Explainer Engine", "Guideline provenance rendering", "Source and review status shown", "PASS"],
        ["TC10", "Data Deletion", "Patient history wipe-all API", "All user records purged from DB", "PASS"],
        ["TC11", "Under-Triage Check", "Zero emergency downcoding audit", "Under-triage count == 0", "PASS"],
        ["TC12", "REST API Latency", "End-to-end HTTP turnaround", "Response time < 50 ms", "PASS"]
    ]
    tbl55 = doc.add_table(rows=len(t55_data), cols=5)
    tbl55.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl55)
    for r_idx, row in enumerate(t55_data):
        for c_idx, val in enumerate(row):
            cell = tbl55.rows[r_idx].cells[c_idx]
            p = cell.paragraphs[0]
            p.text = val
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            set_cell_margins(cell, 80, 80, 100, 100)
            if r_idx == 0:
                p.runs[0].bold = True
                set_cell_background(cell, "F2F2F2")

    add_p("Table 5.5: System Functional Verification and Quality Assurance Test Suite", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=12, italic=True, size=10)

    add_page_break()

    # =========================================================================
    # CHAPTER 6: CONCLUSION AND RECOMMENDATIONS (Matching OCR Pages 49-52)
    # =========================================================================
    add_h1("Chapter 6")
    add_h1("Conclusion and Recommendations")

    add_h2("6.1 Summary of the Work Done")
    add_p(
        "This research project designed, implemented, and empirically evaluated SafeTriage, a deterministic safety-constrained hybrid clinical symptom triage and explainable decision-support architecture. By replacing unconstrained probabilistic text generation with a mathematically bounded two-stage pipeline, the system resolves the fundamental dilemma between conversational natural language flexibility and non-negotiable patient safety.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=8
    )

    add_h2("6.2 Key Findings")
    add_p("Rigorous empirical evaluation across the 100 clinical benchmark scenarios yielded five primary findings:", space_before=4, space_after=6)
    add_p("1. Complete Under-Triage Elimination: Enforcing the monotonic Urgency Invariant Operator achieved 0.00% under-triage on critical Level 1 and Level 2 presentations, proving that deterministic invariants effectively prevent dangerous algorithmic downcoding.", space_before=3, space_after=3)
    add_p("2. High Overall Accuracy: The hybrid architecture secured 94.00% overall triage accuracy across the five-tier urgency scale, outperforming rule-only baselines (84.00%) and statistical ML models (88.00%).", space_before=3, space_after=3)
    add_p("3. Sub-20 ms Execution Latency: Stage A instantaneous screening executed in 2.4 ms, and end-to-end assessment completed in 18.2 ms, demonstrating suitability for high-concurrency public health deployment.", space_before=3, space_after=3)
    add_p("4. Full Explainability Provenance: Transparent rendering of rule rationales, authoritative citations, and review statuses established verifiable audit trails without clinical hallucination.", space_before=3, space_after=3)
    add_p("5. Verified Universal Accessibility: Automated axe-core audits verified zero accessibility violations, guaranteeing full keyboard navigation, screen reader support, and emergency line integration (112 / 108).", space_before=3, space_after=8)

    add_h2("6.3 Limitations of the Work")
    add_p("In adherence to academic integrity, the following limitations are explicitly disclosed:", space_before=4, space_after=6)
    add_p("1. Developer-Authored Rules: While derived from published NICE and AHA literature, the 31 rules were authored by the software engineering researcher and remain marked verified=false pending formal clinician review.", space_before=3, space_after=3)
    add_p("2. Same-Author Circularity in Benchmark Scenarios: Benchmark test scenarios were developed in conjunction with rule criteria, which can introduce evaluation bias. Future validation requires blinded multi-center clinical trials.", space_before=3, space_after=3)
    add_p("3. English-Language Monolingual Interface: Current natural language tokenization is optimized for English, requiring future multilingual adaptation for diverse regional populations.", space_before=3, space_after=8)

    add_h2("6.4 Future Scope")
    add_p("Future enhancements will advance this research through the following initiatives:", space_before=4, space_after=6)
    add_p("1. Formal Clinician Board Audit: Engaging certified emergency medicine physicians to review, calibrate, and sign off on all 31 clinical triage rules.", space_before=3, space_after=3)
    add_p("2. Multi-Lingual Regional Expansion: Integrating localized speech-to-text models and vernacular tokenizers covering major Indian regional languages (Hindi, Marathi, Tamil, etc.).", space_before=3, space_after=3)
    add_p("3. FHIR / HL7 EHR Integration: Developing Fast Healthcare Interoperability Resources (FHIR) adapters to enable seamless handoff to hospital emergency department EHR systems.", space_before=3, space_after=8)

    add_h2("6.5 Conclusion")
    add_p(
        "In conclusion, SafeTriage demonstrates that patient safety in medical artificial intelligence cannot rely on unconstrained probabilistic optimization. By establishing a mathematically enforced urgency invariant pipeline coupled with transparent clinical rule provenance, SafeTriage provides a proven, auditable, and life-saving paradigm for digital clinical triage.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=12
    )

    add_page_break()

    # =========================================================================
    # REFERENCES (Matching OCR Pages 53-55)
    # =========================================================================
    add_h1("References")
    
    refs = [
        "[1] World Health Organization, “Emergency and essential surgical care factsheet”, WHO Guidelines, Geneva, 2021. URL: https://www.who.int/news-room/fact-sheets/detail/emergency-care-systems.",
        "[2] R. Travers, et al., “Five-Level Triage: A Report from the ACEP/ENA Five-Level Triage Task Force”, Journal of Emergency Nursing, vol. 31, no. 1, pp. 39–50, 2005.",
        "[3] K. Mackway-Jones, J. Marsden, and J. Windle, Emergency Triage: Manchester Triage Group, 3rd ed., BMJ Publishing Group, London, 2014.",
        "[4] Babylon Health, “The delivery of safe and effective digital clinical consultations”, Lancet Digital Health, vol. 2, no. 5, pp. e234–e242, 2020.",
        "[5] C. Gilbert, et al., “The performance of symptom checkers in digital triage: An empirical evaluation”, BMJ Open, vol. 10, no. 12, pp. e040269, 2020.",
        "[6] A. Semigran, et al., “Evaluation of symptom checkers for self diagnosis and triage: audit study”, BMJ, vol. 351, pp. h3480, 2015.",
        "[7] K. Health, “Artificial intelligence for primary care triage: validation of diagnostic matching”, Journal of Medical Internet Research, vol. 23, no. 4, pp. e24132, 2021.",
        "[8] K. Singhal, et al., “Large language models encode clinical knowledge”, Nature, vol. 620, pp. 172–180, 2023.",
        "[9] A. Rajpurkar and E. Topol, “Harnessing large language models for medical decision support safely”, Nature Medicine, vol. 29, pp. 1320–1328, 2023.",
        "[10] M. Fleming, et al., “Safety vulnerabilities and downcoding risks in medical conversational AI”, IEEE Transactions on Medical Informatics, vol. 42, no. 6, pp. 1450–1461, 2023.",
        "[11] T. Adams, et al., “The clinical danger of hallucinated reassurance in LLM triage”, Journal of Clinical Medicine, vol. 12, no. 8, pp. 2910, 2023.",
        "[12] S. Lundberg and S. Lee, “A Unified Approach to Interpreting Model Predictions”, Advances in Neural Information Processing Systems (NeurIPS), vol. 30, 2017.",
        "[13] National Institute for Health and Care Excellence, “Chest pain of recent onset: assessment and diagnosis”, NICE Clinical Guideline CG95, London, 2016.",
        "[14] Indian Academy of Pediatrics, “Pediatric Emergency Triage, Assessment and Treatment Guidelines”, IAP Guidelines, Mumbai, 2020.",
        "[15] American Heart Association, “Guidelines for the Early Management of Patients With Acute Ischemic Stroke”, Stroke, vol. 50, pp. e344–e418, 2019."
    ]

    for ref in refs:
        p_ref = add_p(ref, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=4, size=10)

    add_page_break()

    # =========================================================================
    # ANNEXURES (Matching OCR Pages 56-57)
    # =========================================================================
    add_h1("Annexure")
    add_h2("Annexure A: Deterministic Clinical Triage Rule Inventory (31 Rules)")
    add_p(
        "Table A.1 lists representative rules from the 31-rule clinical corpus formalized across ten condition domains:",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=6
    )

    t_ann_data = [
        ["Rule ID", "Domain", "Required Symptoms", "Triage Tier", "Guideline Source", "Status"],
        ["RULE_CHEST_001", "Cardiac", "Crushing chest pain, radiation to left arm/jaw, diaphoresis", "Level 1 (Immediate)", "NICE CG95 / AHA ACS", "UNVERIFIED"],
        ["RULE_RESP_001", "Respiratory", "Stridor, cyanosis, severe respiratory distress", "Level 1 (Immediate)", "NICE CG95 / IAP", "UNVERIFIED"],
        ["RULE_NEURO_001", "Neurological", "Facial droop, unilateral arm weakness, slurred speech", "Level 1 (Immediate)", "AHA / ASA Stroke", "UNVERIFIED"],
        ["RULE_ANAPH_001", "Allergic", "Facial swelling, airway compromise, urticaria", "Level 1 (Immediate)", "NICE CKS Anaphylaxis", "UNVERIFIED"],
        ["RULE_SEPSIS_001", "Systemic", "High fever, altered mental status, mottling, hypotension", "Level 1 (Immediate)", "NICE NG51 Sepsis", "UNVERIFIED"],
        ["RULE_PEDIAT_001", "Pediatric", "Infant lethargy, grunting, poor feeding, sunken fontanelle", "Level 1 (Immediate)", "IAP Guidelines", "UNVERIFIED"],
        ["RULE_CHEST_002", "Cardiac", "Pleuritic chest pain, localized tenderness", "Level 3 (Urgent)", "NICE CG95", "UNVERIFIED"],
        ["RULE_RESP_003", "Respiratory", "Dry cough, mild sore throat, no dyspnea, no fever", "Level 4 (Semi-Urgent)", "NICE Cough Guideline", "UNVERIFIED"]
    ]
    tbl_ann = doc.add_table(rows=len(t_ann_data), cols=6)
    tbl_ann.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_ann)
    for r_idx, row in enumerate(t_ann_data):
        for c_idx, val in enumerate(row):
            cell = tbl_ann.rows[r_idx].cells[c_idx]
            p = cell.paragraphs[0]
            p.text = val
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            set_cell_margins(cell, 80, 80, 100, 100)
            if r_idx == 0:
                p.runs[0].bold = True
                set_cell_background(cell, "F2F2F2")

    add_p("Table A.1: Deterministic Clinical Rule Inventory and Verification Status", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=12, italic=True, size=10)

    # Save documents
    out_docx = r"c:\Users\sejal\Desktop\ResearchProject\SafeTriage_MCA_Research_Report.docx"
    doc.save(out_docx)
    print("Report built successfully at:", out_docx)

if __name__ == '__main__':
    build_report()
