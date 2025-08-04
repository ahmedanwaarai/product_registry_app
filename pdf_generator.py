from flask import render_template
from io import BytesIO
from datetime import datetime
from models import utc_to_pakistan

def generate_deal_pdf(deal):
    """Generate a PDF document for a deal with a modern layout"""
    try:
        # Try using WeasyPrint for better HTML-to-PDF conversion
        from weasyprint import HTML, CSS
        
        # Render the HTML template with deal data
        html_content = render_template('deal_pdf.html', deal=deal)
        
        # Generate PDF from HTML
        buffer = BytesIO()
        HTML(string=html_content).write_pdf(buffer)
        pdf_data = buffer.getvalue()
        buffer.close()
        
        return pdf_data
        
    except ImportError:
        # Fallback to ReportLab if WeasyPrint is not available
        return generate_deal_pdf_reportlab(deal)

def generate_deal_pdf_reportlab(deal):
    """Fallback PDF generation using ReportLab with updated layout (no prices)"""
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                          rightMargin=72, leftMargin=72,
                          topMargin=72, bottomMargin=36)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=10,
        alignment=1,
        textColor=colors.Color(0.051, 0.431, 0.992)  # Bootstrap primary blue
    )
    
    date_style = ParagraphStyle(
        'Date',
        parent=styles['Normal'],
        fontSize=12,
        alignment=2,  # Right alignment
        textColor=colors.grey
    )
    
    section_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=8,
        textColor=colors.Color(0.286, 0.333, 0.341)
    )
    
    # Header with title and date
    header_data = [[
        Paragraph("Product Registry Deal Document", title_style),
        Paragraph(f"Date: {utc_to_pakistan(datetime.utcnow()).split(' ')[0]}", date_style)
    ]]
    
    header_table = Table(header_data, colWidths=[4*inch, 2.5*inch])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
    ]))
    
    elements.append(header_table)
    elements.append(Spacer(1, 20))
    
    # Deal Information
    elements.append(Paragraph("Deal Information", section_style))
    deal_info_data = [
        ['Deal ID:', f"#{deal.id}"],
        ['Status:', deal.status.title()],
        ['Deal Type:', deal.deal_type.title() if deal.deal_type else 'Normal'],
        ['Created Date:', utc_to_pakistan(deal.created_at)]
    ]
    
    deal_info_table = Table(deal_info_data, colWidths=[2*inch, 4*inch])
    deal_info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.Color(0.969, 0.976, 0.980)),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.Color(0.871, 0.886, 0.902))
    ]))
    
    elements.append(deal_info_table)
    elements.append(Spacer(1, 20))
    
    # Parties Involved
    elements.append(Paragraph("Parties Involved", section_style))
    
    # Buyer info
    buyer_data = [[
        'Buyer Name:', deal.buyer.username,
        'Contact:', deal.buyer.email
    ], [
        'Mobile:', deal.buyer.mobile_number,
        'ID:', getattr(deal.buyer, 'id_number', 'N/A')
    ]]
    
    # Seller info
    if deal.seller:
        seller_data = [[
            'Seller Name:', deal.seller.username,
            'Contact:', deal.seller.email
        ], [
            'Mobile:', deal.seller.mobile_number,
            'ID:', getattr(deal.seller, 'id_number', 'N/A')
        ]]
    else:
        seller_data = [[
            'Seller Name:', deal.seller_name or 'N/A',
            'Contact:', deal.seller_mobile or 'N/A'
        ], [
            'Mobile:', deal.seller_mobile or 'N/A',
            'ID:', deal.seller_id_card or 'N/A'
        ]]
    
    parties_data = buyer_data + seller_data
    
    parties_table = Table(parties_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
    parties_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.Color(0.969, 0.976, 0.980)),
        ('BACKGROUND', (2, 0), (2, -1), colors.Color(0.969, 0.976, 0.980)),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.Color(0.871, 0.886, 0.902))
    ]))
    
    elements.append(parties_table)
    elements.append(Spacer(1, 20))
    
    # Products Involved (NO PRICES)
    elements.append(Paragraph(f"Products Involved ({len(deal.deal_items)} items)", section_style))
    
    products_data = [['Product Name', 'Serial Number', 'Brand', 'Category']]
    
    for item in deal.deal_items:
        products_data.append([
            item.product.name,
            item.product.serial_number,
            item.product.brand.name,
            item.product.category.name
        ])
    
    products_table = Table(products_data, colWidths=[2.2*inch, 1.8*inch, 1.5*inch, 1.5*inch])
    products_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.286, 0.333, 0.341)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.Color(0.980, 0.984, 0.988)),
        ('GRID', (0, 0), (-1, -1), 1, colors.Color(0.871, 0.886, 0.902))
    ]))
    
    elements.append(products_table)
    elements.append(Spacer(1, 20))
    
    # Deal Description
    if deal.description:
        elements.append(Paragraph("Deal Description", section_style))
        desc_style = ParagraphStyle(
            'Description',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=15,
            leftIndent=20,
            fontName='Helvetica-Oblique'
        )
        elements.append(Paragraph(deal.description, desc_style))
        elements.append(Spacer(1, 20))
    
    # Approval Information
    if deal.approved_by:
        elements.append(Paragraph("Approval Information", section_style))
        approval_data = [
            ['Approved By:', 'Admin'],
            ['Approved On:', utc_to_pakistan(deal.approved_at) if deal.approved_at else 'N/A']
        ]
        if deal.approval_notes:
            approval_data.append(['Approval Notes:', deal.approval_notes])
        
        approval_table = Table(approval_data, colWidths=[2*inch, 4*inch])
        approval_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.Color(0.969, 0.976, 0.980)),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.Color(0.871, 0.886, 0.902))
        ]))
        
        elements.append(approval_table)
        elements.append(Spacer(1, 20))
    
    # Footer
    elements.append(Spacer(1, 30))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=10,
        alignment=1,
        textColor=colors.Color(0.424, 0.467, 0.514)
    )
    
    elements.append(Paragraph(f"Document generated on: {utc_to_pakistan(datetime.utcnow())}", footer_style))
    elements.append(Paragraph("For verification, please contact our support team", footer_style))
    
    # Build PDF
    doc.build(elements)
    
    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data
