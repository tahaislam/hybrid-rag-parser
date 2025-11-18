"""
Generate sample PDF files with diverse tables and content for testing the RAG system.
These PDFs contain different types of tables to test various query patterns.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import os

def create_project_budget_pdf():
    """Create a PDF with project budget and timeline tables."""
    filename = "data/project_budget.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    # Title
    title = Paragraph("<b>Software Development Project Plan</b>", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 0.3*inch))

    # Introduction
    intro = Paragraph("""
    This document outlines the budget and timeline for the Customer Portal Redesign project.
    The project aims to modernize our customer-facing web portal with improved UX/UI design,
    enhanced security features, and mobile responsiveness.
    """, styles['BodyText'])
    story.append(intro)
    story.append(Spacer(1, 0.3*inch))

    # Budget Table
    budget_header = Paragraph("<b>Project Budget Breakdown</b>", styles['Heading2'])
    story.append(budget_header)
    story.append(Spacer(1, 0.2*inch))

    budget_data = [
        ['Task', 'Estimated Hours', 'Rate ($/hr)', 'Total Cost'],
        ['Requirements Analysis', '40', '150', '$6,000'],
        ['UI/UX Design', '80', '120', '$9,600'],
        ['Software Development', '160', '140', '$22,400'],
        ['Testing & QA', '60', '100', '$6,000'],
        ['Documentation', '20', '80', '$1,600'],
        ['Project Management', '30', '160', '$4,800'],
        ['TOTAL', '390', '', '$50,400']
    ]

    budget_table = Table(budget_data, colWidths=[2.5*inch, 1.5*inch, 1.2*inch, 1.3*inch])
    budget_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(budget_table)
    story.append(Spacer(1, 0.4*inch))

    # Timeline Table
    timeline_header = Paragraph("<b>Project Timeline</b>", styles['Heading2'])
    story.append(timeline_header)
    story.append(Spacer(1, 0.2*inch))

    timeline_data = [
        ['Phase', 'Duration (weeks)', 'Start Date', 'End Date'],
        ['Requirements', '2', '2024-01-15', '2024-01-29'],
        ['Design', '4', '2024-01-30', '2024-02-26'],
        ['Development', '8', '2024-02-27', '2024-04-22'],
        ['Testing', '3', '2024-04-23', '2024-05-13'],
        ['Deployment', '1', '2024-05-14', '2024-05-20']
    ]

    timeline_table = Table(timeline_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    timeline_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(timeline_table)

    doc.build(story)
    print(f"✓ Created {filename}")

def create_financial_report_pdf():
    """Create a PDF with quarterly financial data."""
    filename = "data/financial_report.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    # Title
    title = Paragraph("<b>Quarterly Financial Report - Q4 2023</b>", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 0.3*inch))

    # Executive Summary
    summary = Paragraph("""
    <b>Executive Summary:</b><br/>
    The company achieved strong performance in Q4 2023, with total revenue reaching $2.8M,
    representing a 15% increase compared to Q3 2023. Operating expenses were well-controlled
    at $1.9M, resulting in a net profit of $900K for the quarter.
    """, styles['BodyText'])
    story.append(summary)
    story.append(Spacer(1, 0.3*inch))

    # Revenue Table
    revenue_header = Paragraph("<b>Revenue by Product Line</b>", styles['Heading2'])
    story.append(revenue_header)
    story.append(Spacer(1, 0.2*inch))

    revenue_data = [
        ['Product Line', 'Q3 2023', 'Q4 2023', 'Growth %'],
        ['Enterprise Software', '$1,200,000', '$1,400,000', '16.7%'],
        ['Cloud Services', '$800,000', '$950,000', '18.8%'],
        ['Professional Services', '$400,000', '$450,000', '12.5%'],
        ['TOTAL', '$2,400,000', '$2,800,000', '16.7%']
    ]

    revenue_table = Table(revenue_data, colWidths=[2.2*inch, 1.5*inch, 1.5*inch, 1.2*inch])
    revenue_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightblue),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(revenue_table)
    story.append(Spacer(1, 0.4*inch))

    # Expense Table
    expense_header = Paragraph("<b>Operating Expenses Breakdown</b>", styles['Heading2'])
    story.append(expense_header)
    story.append(Spacer(1, 0.2*inch))

    expense_data = [
        ['Category', 'Amount', 'Percentage of Total'],
        ['Salaries & Benefits', '$1,200,000', '63.2%'],
        ['Marketing & Sales', '$380,000', '20.0%'],
        ['Infrastructure', '$190,000', '10.0%'],
        ['R&D', '$95,000', '5.0%'],
        ['Other', '$35,000', '1.8%'],
        ['TOTAL', '$1,900,000', '100%']
    ]

    expense_table = Table(expense_data, colWidths=[2.5*inch, 1.8*inch, 2*inch])
    expense_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightcoral),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(expense_table)

    doc.build(story)
    print(f"✓ Created {filename}")

def create_research_data_pdf():
    """Create a PDF with research experiment results."""
    filename = "data/research_results.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    # Title
    title = Paragraph("<b>Machine Learning Model Performance Study</b>", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 0.3*inch))

    # Abstract
    abstract = Paragraph("""
    <b>Abstract:</b><br/>
    This study evaluates the performance of various machine learning models on a customer
    churn prediction dataset. We trained and tested five different algorithms using
    cross-validation and measured their accuracy, precision, recall, and F1 scores.
    The Random Forest model achieved the highest overall performance with 94.2% accuracy.
    """, styles['BodyText'])
    story.append(abstract)
    story.append(Spacer(1, 0.3*inch))

    # Results Table
    results_header = Paragraph("<b>Model Performance Comparison</b>", styles['Heading2'])
    story.append(results_header)
    story.append(Spacer(1, 0.2*inch))

    results_data = [
        ['Model', 'Accuracy', 'Precision', 'Recall', 'F1 Score', 'Training Time (min)'],
        ['Logistic Regression', '87.3%', '85.1%', '86.2%', '85.6%', '2.1'],
        ['Decision Tree', '89.5%', '88.0%', '89.1%', '88.5%', '3.5'],
        ['Random Forest', '94.2%', '93.8%', '94.5%', '94.1%', '12.3'],
        ['XGBoost', '93.8%', '93.2%', '94.0%', '93.6%', '15.7'],
        ['Neural Network', '91.6%', '90.5%', '91.8%', '91.1%', '28.4']
    ]

    results_table = Table(results_data, colWidths=[1.6*inch, 1*inch, 1*inch, 1*inch, 1*inch, 1.2*inch])
    results_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 2), (-1, 2), colors.lightgreen)  # Highlight best performer
    ]))
    story.append(results_table)
    story.append(Spacer(1, 0.3*inch))

    # Dataset Info
    dataset_header = Paragraph("<b>Dataset Characteristics</b>", styles['Heading2'])
    story.append(dataset_header)
    story.append(Spacer(1, 0.2*inch))

    dataset_data = [
        ['Characteristic', 'Value'],
        ['Total Samples', '50,000'],
        ['Training Set', '40,000 (80%)'],
        ['Test Set', '10,000 (20%)'],
        ['Number of Features', '23'],
        ['Class Balance', '30% churn, 70% retained'],
        ['Cross-validation Folds', '5']
    ]

    dataset_table = Table(dataset_data, colWidths=[3*inch, 2.5*inch])
    dataset_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(dataset_table)

    doc.build(story)
    print(f"✓ Created {filename}")

def create_product_specs_pdf():
    """Create a PDF with product specifications."""
    filename = "data/product_specs.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    # Title
    title = Paragraph("<b>CloudServer Pro X500 - Technical Specifications</b>", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 0.3*inch))

    # Overview
    overview = Paragraph("""
    The CloudServer Pro X500 is our flagship enterprise server solution, designed for
    high-performance computing workloads. It features the latest generation processors,
    massive memory capacity, and enterprise-grade redundancy features.
    """, styles['BodyText'])
    story.append(overview)
    story.append(Spacer(1, 0.3*inch))

    # Hardware Specs
    hw_header = Paragraph("<b>Hardware Specifications</b>", styles['Heading2'])
    story.append(hw_header)
    story.append(Spacer(1, 0.2*inch))

    hw_data = [
        ['Component', 'Specification'],
        ['Processor', 'Dual Intel Xeon Gold 6348 (28 cores each)'],
        ['RAM', '512 GB DDR4 ECC'],
        ['Storage', '8x 4TB NVMe SSD (RAID 10)'],
        ['Network', '4x 25GbE ports'],
        ['Power Supply', 'Dual redundant 2000W'],
        ['Form Factor', '2U Rackmount'],
        ['Warranty', '5 years enterprise support']
    ]

    hw_table = Table(hw_data, colWidths=[2*inch, 4.5*inch])
    hw_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.purple),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(hw_table)
    story.append(Spacer(1, 0.4*inch))

    # Performance Metrics
    perf_header = Paragraph("<b>Performance Benchmarks</b>", styles['Heading2'])
    story.append(perf_header)
    story.append(Spacer(1, 0.2*inch))

    perf_data = [
        ['Benchmark', 'Score', 'Industry Average'],
        ['CPU Performance (SPECint)', '385', '250'],
        ['Memory Bandwidth (GB/s)', '280', '180'],
        ['Storage IOPS (4K Random)', '2,500,000', '800,000'],
        ['Network Throughput (Gbps)', '98', '50'],
        ['Power Efficiency (Perf/Watt)', '92', '65']
    ]

    perf_table = Table(perf_data, colWidths=[2.8*inch, 1.5*inch, 2*inch])
    perf_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.navy),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(perf_table)

    doc.build(story)
    print(f"✓ Created {filename}")

def create_sales_report_pdf():
    """Create a PDF with regional sales data."""
    filename = "data/sales_report.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    # Title
    title = Paragraph("<b>Regional Sales Performance Report - 2023</b>", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 0.3*inch))

    # Summary
    summary = Paragraph("""
    This report provides a comprehensive overview of sales performance across all regions
    for fiscal year 2023. Overall, the company achieved $18.5M in sales, exceeding the
    annual target by 8%. The Asia-Pacific region showed exceptional growth at 45%.
    """, styles['BodyText'])
    story.append(summary)
    story.append(Spacer(1, 0.3*inch))

    # Regional Sales
    regional_header = Paragraph("<b>Sales by Region</b>", styles['Heading2'])
    story.append(regional_header)
    story.append(Spacer(1, 0.2*inch))

    regional_data = [
        ['Region', 'Q1', 'Q2', 'Q3', 'Q4', 'Total', 'Growth vs 2022'],
        ['North America', '$1.2M', '$1.4M', '$1.3M', '$1.5M', '$5.4M', '12%'],
        ['Europe', '$0.9M', '$1.0M', '$1.1M', '$1.2M', '$4.2M', '8%'],
        ['Asia-Pacific', '$0.8M', '$1.1M', '$1.3M', '$1.5M', '$4.7M', '45%'],
        ['Latin America', '$0.5M', '$0.6M', '$0.6M', '$0.7M', '$2.4M', '15%'],
        ['Middle East', '$0.4M', '$0.4M', '$0.5M', '$0.6M', '$1.9M', '22%'],
        ['TOTAL', '$3.8M', '$4.5M', '$4.8M', '$5.5M', '$18.5M', '18%']
    ]

    regional_table = Table(regional_data, colWidths=[1.4*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.9*inch, 1.1*inch])
    regional_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkorange),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightyellow),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(regional_table)
    story.append(Spacer(1, 0.4*inch))

    # Top Performers
    performers_header = Paragraph("<b>Top Sales Representatives</b>", styles['Heading2'])
    story.append(performers_header)
    story.append(Spacer(1, 0.2*inch))

    performers_data = [
        ['Name', 'Region', 'Total Sales', 'Deals Closed', 'Avg Deal Size'],
        ['Sarah Johnson', 'North America', '$2,100,000', '42', '$50,000'],
        ['Chen Wei', 'Asia-Pacific', '$1,850,000', '65', '$28,462'],
        ['Marcus Schmidt', 'Europe', '$1,650,000', '38', '$43,421'],
        ['Isabella Garcia', 'Latin America', '$1,420,000', '51', '$27,843'],
        ['Ahmed Hassan', 'Middle East', '$1,280,000', '29', '$44,138']
    ]

    performers_table = Table(performers_data, colWidths=[1.6*inch, 1.5*inch, 1.3*inch, 1.3*inch, 1.3*inch])
    performers_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(performers_table)

    doc.build(story)
    print(f"✓ Created {filename}")

def main():
    """Generate all sample PDFs."""
    print("Generating sample PDF files...")
    print()

    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)

    create_project_budget_pdf()
    create_financial_report_pdf()
    create_research_data_pdf()
    create_product_specs_pdf()
    create_sales_report_pdf()

    print()
    print("✓ All sample PDFs generated successfully!")
    print("Next steps:")
    print("1. Run 'python run_pipeline.py' to ingest these PDFs")
    print("2. Run 'python test_rag_queries.py' to test the RAG system")

if __name__ == "__main__":
    main()
