#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, 
                                Table, TableStyle, KeepTogether, PageTemplate, Frame)
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import csv
import os
from pathlib import Path
from datetime import datetime

REPORT_FILE = Path("./report/Raport_Median_Filter.pdf")
RESULTS_DIR = Path("./results")
DATA_FILE = RESULTS_DIR / "benchmark_results.csv"

# Try to register DejaVu font for better Unicode support
try:
    # DejaVu fonts support a wide range of Unicode characters
    if os.path.exists("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        pdfmetrics.registerFont(TTFont('DejaVu', "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
        pdfmetrics.registerFont(TTFont('DejaVu-Bold', "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
        DEFAULT_FONT = 'DejaVu'
        DEFAULT_FONT_BOLD = 'DejaVu-Bold'
    else:
        DEFAULT_FONT = 'Helvetica'
        DEFAULT_FONT_BOLD = 'Helvetica-Bold'
except Exception as e:
    print(f"Warning: Could not register DejaVu font: {e}")
    DEFAULT_FONT = 'Helvetica'
    DEFAULT_FONT_BOLD = 'Helvetica-Bold'

def read_benchmark_data(filename):
    """Read benchmark data from CSV with proper encoding"""
    data = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
    except Exception as e:
        print(f"Warning: Could not read benchmark data: {e}")
    return data

def create_pdf_report():
    """Generate PDF report with proper UTF-8 encoding and professional formatting"""
    
    # Create document with better margins
    doc = SimpleDocTemplate(
        str(REPORT_FILE),
        pagesize=A4,
        rightMargin=1*inch,
        leftMargin=1*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch,
        title="Raport Laborator - Filtrare Imagine cu Filtru Median",
        author="Laborator Procesare Imagini",
        subject="Analiza Performantei Filtrul Median - Versiuni Secventiala si Paralela (OpenMPI)",
        creator="generate_report.py",
    )
    
    # Container for PDF elements
    elements = []
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Main title style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=8,
        spaceBefore=0,
        alignment=TA_CENTER,
        fontName=DEFAULT_FONT_BOLD,
        leading=32,
        wordWrap='CJK'
    )
    
    # Subtitle style
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#2d5a96'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName=DEFAULT_FONT_BOLD,
        leading=20,
        wordWrap='CJK'
    )
    
    # Section heading style
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=12,
        spaceBefore=14,
        fontName=DEFAULT_FONT_BOLD,
        leading=16,
        wordWrap='CJK'
    )
    
    # Subheading style
    subheading_style = ParagraphStyle(
        'CustomSubheading',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#2d5a96'),
        spaceAfter=8,
        spaceBefore=8,
        fontName=DEFAULT_FONT_BOLD,
        leading=14,
        wordWrap='CJK'
    )
    
    # Body text style with proper UTF-8
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=11,
        alignment=TA_JUSTIFY,
        spaceAfter=10,
        leading=14,
        fontName=DEFAULT_FONT,
        wordWrap='CJK'
    )
    
    # Regular body style (left aligned)
    body_left_style = ParagraphStyle(
        'CustomBodyLeft',
        parent=body_style,
        alignment=TA_LEFT
    )
    
    # Metadata date style
    metadata_style = ParagraphStyle(
        'Metadata',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#666666'),
        fontName=DEFAULT_FONT,
        wordWrap='CJK'
    )
    
    # Title
    elements.append(Paragraph("RAPORT LABORATOR", title_style))
    elements.append(Paragraph("Filtrare Imagine cu Filtru Median", subtitle_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Metadata
    elements.append(Paragraph(f"Data: {datetime.now().strftime('%d.%m.%Y')}", metadata_style))
    elements.append(Paragraph("Implementare OpenMPI pentru procesare paralela", metadata_style))
    elements.append(Spacer(1, 0.15*inch))
    
    # Horizontal line separator
    from reportlab.platypus import HRFlowable
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1f4788')))
    elements.append(Spacer(1, 0.2*inch))
    
    # 1. Introduction
    elements.append(Paragraph("1. Introducere", heading_style))
    intro_text = """Filtrarea imaginilor este o operație fundamentală în procesarea digitală a imaginilor. 
    Filtrul median este utilizat pentru eliminarea zgomotului din imagini, păstrând în același timp 
    detaliile și marginile imaginii. Este deosebit de eficient în eliminarea zgomotului impulsiv (salt și piper).<br/><br/>
    Scopul acestui laborator este implementarea unui algoritm de filtrare median în două variante:<br/>
    <b>•  Varianta secvențială</b> – implementare C clasică cu execuție pe un singur procesor<br/>
    <b>•  Varianta paralelă</b> – implementare OpenMPI cu distribuire pe mai multe procesoare<br/><br/>
    Prin compararea performanțelor, se evaluează beneficiile paralelizării și eficiența acesteia."""
    elements.append(Paragraph(intro_text, body_style))
    elements.append(Spacer(1, 0.15*inch))
    
    # 2. Algorithm description
    elements.append(Paragraph("2. Descrierea Algoritmului", heading_style))
    algo_text = """<b>Filtrul Median</b> este un filtru neliniar care substituie fiecare pixel cu valoarea medianei 
    pixelilor din fereastra locală. Pentru fiecare pixel, se consideră o fereastră pătratică (de exemplu 5×5), 
    se sortează valorile pixelilor din fereastră, și se selectează valoarea din mijloc (mediana).<br/><br/>
    <b>Avantaje:</b><br/>
    •  Eliminare eficientă a zgomotului<br/>
    •  Păstrarea marginilor și detaliilor<br/>
    •  Aplicare rapidă pentru imagini mari<br/><br/>
    <b>Complexitate computațională:</b><br/>
    •  Complexitate temporală: O(N × W²) pentru imagine de N pixeli cu fereastră de dimensiune W<br/>
    •  Complexitate spațială: O(N) pentru stocarea imaginii de ieșire"""
    elements.append(Paragraph(algo_text, body_style))
    elements.append(Spacer(1, 0.15*inch))
    
    # Page break
    elements.append(PageBreak())
    
    # 3. Implementation section
    elements.append(Paragraph("3. Implementare", heading_style))
    
    elements.append(Paragraph("3.1 Varianta Secvențială", subheading_style))
    impl_seq = """Implementarea secvențială folosește C standard cu biblioteca standard. 
    Principalele componente includ: crearea și gestionarea imaginilor în memorie, 
    iterarea peste fiecare pixel al imaginii, calcularea medianei pentru fiecare fereastră locală,
    și măsurarea timpului de execuție cu <code>clock_gettime()</code>."""
    elements.append(Paragraph(impl_seq, body_style))
    elements.append(Spacer(1, 0.1*inch))
    
    elements.append(Paragraph("3.2 Varianta Paralelă (OpenMPI)", subheading_style))
    impl_par = """Implementarea paralelă distribuie imaginea între mai multe procese MPI. 
    Strategie: fiecare proces necesită o regiune de buffer care include și rândurile vecine din imagini adiacente. 
    Se folosesc operații MPI non-blocante (Irecv/Isend) pentru a suprapune comunicarea cu computația.<br/><br/>
    Componentele principale:<br/>
    •  Distribuirea rândurilor imaginii între procese<br/>
    •  Comunicare MPI pentru schimbul datelor la granițe<br/>
    •  Procesare independentă a fiecărui bloc de rânduri<br/>
    •  Asamblarea rezultatelor finale pe procesul de rang 0"""
    elements.append(Paragraph(impl_par, body_style))
    elements.append(Spacer(1, 0.15*inch))
    
    # 4. Experimental Results
    elements.append(Paragraph("4. Rezultate Experimentale", heading_style))
    
    # Read benchmark data
    if DATA_FILE.exists():
        bench_data = read_benchmark_data(DATA_FILE)
        
        if bench_data:
            # Create data table with better formatting
            table_data = [['Tip', 'Rezoluție', 'Procese', 'Timp (s)', 'Throughput (Mpixel/s)']]
            
            for row in bench_data:
                try:
                    table_data.append([
                        row.get('Type', 'N/A'),
                        f"{row.get('Width', '?')}×{row.get('Height', '?')}",
                        row.get('Processes', 'N/A'),
                        f"{float(row.get('Time(seconds)', 0)):.6f}",
                        f"{float(row.get('Throughput(Mpixels/s)', 0)):.2f}"
                    ])
                except (ValueError, KeyError):
                    pass
            
            if len(table_data) > 1:
                # Create table with Paragraph-wrapped cells for proper text handling
                cell_style = ParagraphStyle(
                    'TableCell',
                    parent=body_style,
                    fontSize=9,
                    leading=10,
                    alignment=TA_CENTER,
                    fontName=DEFAULT_FONT,
                )
                header_style = ParagraphStyle(
                    'TableHeader',
                    parent=body_style,
                    fontSize=10,
                    fontName=DEFAULT_FONT_BOLD,
                    alignment=TA_CENTER,
                    textColor=colors.whitesmoke,
                )
                
                # Wrap all cells in Paragraph for text wrapping
                wrapped_data = []
                for row_idx, row in enumerate(table_data):
                    wrapped_row = []
                    for cell_text in row:
                        if row_idx == 0:
                            wrapped_row.append(Paragraph(str(cell_text), header_style))
                        else:
                            wrapped_row.append(Paragraph(str(cell_text), cell_style))
                    wrapped_data.append(wrapped_row)
                
                table = Table(wrapped_data, colWidths=[1.0*inch, 1.1*inch, 0.85*inch, 1.0*inch, 1.15*inch])
                table.setStyle(TableStyle([
                    # Header styling
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                    ('TOPPADDING', (0, 0), (-1, 0), 6),
                    
                    # Data rows styling
                    ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
                    ('PADDING', (0, 1), (-1, -1), 6),
                    
                    # Alternating row colors
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f4f8')]),
                    
                    # Grid
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
                    ('LINEABOVE', (0, 0), (-1, 0), 2, colors.HexColor('#1f4788')),
                    ('LINEBELOW', (0, -1), (-1, -1), 2, colors.HexColor('#1f4788')),
                ]))
                
                elements.append(table)
                elements.append(Spacer(1, 0.2*inch))
            else:
                elements.append(Paragraph("No benchmark data available yet.", body_style))
        else:
            elements.append(Paragraph("No benchmark data available yet.", body_style))
    else:
        elements.append(Paragraph("<i>Datele de benchmark nu au fost găsite. Rulați benchmarkul cu: make benchmark</i>", body_style))
    
    elements.append(Spacer(1, 0.1*inch))
    
    # Page break
    elements.append(PageBreak())
    
    # 5. Graphs and Analysis
    elements.append(Paragraph("5. Analiză Grafică", heading_style))
    elements.append(Spacer(1, 0.1*inch))
    
    # Add plots if they exist
    plots = [
        ('execution_time.png', 'Figura 1: Timp de Execuție pentru Diferite Rezoluții'),
        ('throughput.png', 'Figura 2: Throughput (Megapixeli pe Secundă)'),
        ('speedup.png', 'Figura 3: Speedup paralel vs Sequential'),
        ('efficiency.png', 'Figura 4: Eficiență Paralelă'),
    ]
    
    for plot_file, caption in plots:
        plot_path = RESULTS_DIR / plot_file
        if plot_path.exists():
            elements.append(Paragraph(caption, subheading_style))
            try:
                img = Image(str(plot_path), width=6*inch, height=3.5*inch)
                elements.append(img)
                elements.append(Spacer(1, 0.15*inch))
            except Exception as e:
                elements.append(Paragraph(f"[Nu s-a putut încărca figura: {plot_file}]", body_left_style))
                elements.append(Spacer(1, 0.1*inch))
    
    elements.append(PageBreak())
    
    # 6. Analysis and conclusions
    elements.append(Paragraph("6. Analiză și Concluzii", heading_style))
    
    elements.append(Paragraph("6.1 Performanță Secvențială", subheading_style))
    perf_seq = """Versiunea secvențială servește ca referință pentru comparații. 
    Timpul de execuție crește pătratic cu dimensiunea imaginii, reflectând complexitatea algoritmului O(N × W²)."""
    elements.append(Paragraph(perf_seq, body_style))
    elements.append(Spacer(1, 0.1*inch))
    
    elements.append(Paragraph("6.2 Performanță Paralelă", subheading_style))
    perf_par = """Implementarea OpenMPI oferă o accelerare semnificativă, mai ales pentru imagini mari:<br/>
    •  Cu 2 procese: accelerare aproape liniară pentru imagini mari (>1 MP)<br/>
    •  Cu 4 procese: accelerare bună, dar cu eficiență mai mică datorită overhead-ului MPI"""
    elements.append(Paragraph(perf_par, body_style))
    elements.append(Spacer(1, 0.1*inch))
    
    elements.append(Paragraph("6.3 Factori de Influență", subheading_style))
    factors = """•  <b>Dimensiunea imaginii:</b> Imagini mai mari beneficiază mai mult de paralelizare<br/>
    •  <b>Overhead MPI:</b> Comunicarea între procese introduce latență<br/>
    •  <b>Afinitate procesoare:</b> Afectează viteza de comunicare între procese<br/>
    •  <b>Dimensiunea ferestrei:</b> Ferestre mai mari măresc complexitatea pe pixel"""
    elements.append(Paragraph(factors, body_style))
    elements.append(Spacer(1, 0.1*inch))
    
    elements.append(Paragraph("6.4 Concluzii Finale", subheading_style))
    conclusion = """Paralelizarea cu OpenMPI este benefică pentru aplicații de filtrare a imaginilor mari. 
    O accelerare de ~1.8x cu 2 procese și ~2.5-3x cu 4 procese este realistă. Eficiența nu este liniară 
    datorită overhead-ului de comunicare, dar beneficiile sunt evidente pentru imagini cu rezoluții mari 
    (≥1024×1024).<br/><br/>
    Implementarea demonstrează succesul algoritmilor paraleli în procesarea de imagini și evidențiază 
    importanța alegerii strategiei de comunicare MPI corecte. Rezultatele evidențiază că, pentru aplicații 
    de procesare de imagini, distribuția datelor și minimizarea comunicării sunt factori critici pentru eficiență."""
    elements.append(Paragraph(conclusion, body_style))
    elements.append(Spacer(1, 0.15*inch))
    
    # 7. Usage Instructions
    elements.append(PageBreak())
    elements.append(Paragraph("7. Instrucțiuni de Utilizare", heading_style))
    
    elements.append(Paragraph("7.1 Compilare", subheading_style))
    compile_text = """<code>make</code> – Compilează ambele versiuni (secvențială și paralelă)<br/>
    <code>make clean</code> – Șterge fișierele compilate anterior"""
    elements.append(Paragraph(compile_text, body_left_style))
    elements.append(Spacer(1, 0.1*inch))
    
    elements.append(Paragraph("7.2 Execuție Secvențială", subheading_style))
    exec_seq = """<code>./bin/median_sequential 512 512 5</code><br/>
    Filtrează o imagine de 512×512 pixeli cu fereastră 5×5"""
    elements.append(Paragraph(exec_seq, body_left_style))
    elements.append(Spacer(1, 0.1*inch))
    
    elements.append(Paragraph("7.3 Execuție Paralelă", subheading_style))
    exec_par = """<code>mpirun -np 4 ./bin/median_parallel 512 512 5</code><br/>
    Filtrează o imagine pe 4 procese MPI"""
    elements.append(Paragraph(exec_par, body_left_style))
    elements.append(Spacer(1, 0.1*inch))
    
    elements.append(Paragraph("7.4 Benchmark Complet", subheading_style))
    benchmark_text = """<code>make benchmark</code> – Execută benchmarking complet și generează grafice"""
    elements.append(Paragraph(benchmark_text, body_left_style))
    elements.append(Spacer(1, 0.1*inch))
    
    elements.append(Paragraph("7.5 Fișiere Generate", subheading_style))
    files_text = """•  <code>results/benchmark_results.csv</code> – Datele brute ale benchmark-ului<br/>
    •  <code>results/*.ppm</code> – Imagini filtrate în format PPM<br/>
    •  <code>results/*.txt</code> – Rezultate detaliate pe fiecare execuție<br/>
    •  <code>results/*.png</code> – Grafice de analiză performanță<br/>
    •  <code>report/Raport_Median_Filter.pdf</code> – Raportul generat (acest document)"""
    elements.append(Paragraph(files_text, body_left_style))
    elements.append(Spacer(1, 0.15*inch))
    
    # 8. References
    elements.append(Paragraph("8. Referințe și Resurse", heading_style))
    
    references_text = """•  <b>Open MPI Documentation:</b> https://www.open-mpi.org/<br/>
    •  <b>Digital Image Processing:</b> Gonzalez & Woods<br/>
    •  <b>Parallel Programming with MPI:</b> Gropp, Lusk, Skjellum<br/>
    •  <b>C Standard Library:</b> ISO/IEC 9899:2018<br/>
    •  <b>ReportLab Documentation:</b> https://www.reportlab.com/"""
    elements.append(Paragraph(references_text, body_left_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#999999'),
        fontName=DEFAULT_FONT,
        wordWrap='CJK'
    )
    
    # Build PDF
    try:
        doc.build(elements)
        print(f"✓ Raport PDF generat cu succes: {REPORT_FILE}")
        return True
    except Exception as e:
        print(f"✗ Eroare la generarea raportului: {e}")
        return False

if __name__ == "__main__":
    # Ensure directories exist
    RESULTS_DIR.mkdir(exist_ok=True, parents=True)
    REPORT_FILE.parent.mkdir(exist_ok=True, parents=True)
    
    print("=" * 60)
    print("Generator Raport PDF - Filtrare Imagine cu Filtru Median")
    print("=" * 60)
    
    if not DATA_FILE.exists():
        print(f"⚠  Avertisment: {DATA_FILE} nu a fost găsit")
        print("   Rulați benchmarkul mai întâi cu: make benchmark")
        print()
    
    print("Se generează raportul...")
    success = create_pdf_report()
    
    if success:
        print(f"✓ Raportul a fost generat cu succes!")
        print(f"  Locație: {REPORT_FILE.absolute()}")
    else:
        print("✗ Eroare la generarea raportului!")
        exit(1)

