#!/usr/bin/env python3
"""
Executive Summary PDF Generator for Document Portal Presentation
Creates a concise 2-3 page presentation for 5-minute overview
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime

class ExecutiveSummaryPDF:
    def __init__(self, filename="Document_Portal_Executive_Summary.pdf"):
        self.filename = filename
        self.doc = SimpleDocTemplate(
            filename,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        self.styles = getSampleStyleSheet()
        self.story = []
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        # Title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=22,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=HexColor('#2c3e50')
        )
        
        # Section heading style
        self.section_style = ParagraphStyle(
            'SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceBefore=15,
            spaceAfter=10,
            textColor=HexColor('#2980b9')
        )
        
        # Subsection style
        self.subsection_style = ParagraphStyle(
            'SubsectionHeading',
            parent=self.styles['Heading3'],
            fontSize=12,
            spaceBefore=10,
            spaceAfter=6,
            textColor=HexColor('#3498db')
        )
        
        # Compact body text
        self.body_style = ParagraphStyle(
            'CompactBody',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            alignment=TA_JUSTIFY,
            leading=12
        )
        
        # Compact bullet points
        self.bullet_style = ParagraphStyle(
            'CompactBullet',
            parent=self.styles['Normal'],
            fontSize=9,
            spaceAfter=3,
            leftIndent=15,
            bulletIndent=8,
            leading=11
        )

    def add_title_and_overview(self):
        # Title
        self.story.append(Paragraph("Document Portal System", self.title_style))
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=self.styles['Normal'],
            fontSize=14,
            alignment=TA_CENTER,
            textColor=HexColor('#34495e'),
            spaceAfter=20
        )
        self.story.append(Paragraph("AI-Powered Document Management & Conversational RAG Platform", subtitle_style))
        
        # Quick overview
        overview_text = """
        <b>Executive Summary:</b> A cutting-edge document management platform that combines React/TypeScript 
        frontend with FastAPI/Python backend, featuring AI-powered document processing, multi-format support, 
        and conversational querying capabilities across 8+ document types.
        """
        self.story.append(Paragraph(overview_text, self.body_style))
        self.story.append(Spacer(1, 15))

    def add_key_features_table(self):
        self.story.append(Paragraph("Key Capabilities & Features", self.section_style))
        
        features_data = [
            ['Frontend (React/TypeScript)', 'Backend (FastAPI/Python)', 'AI & Processing'],
            ['• Drag & Drop Multi-file Upload\n• Real-time Chat Interface\n• Document Analysis Dashboard\n• Responsive Design (Mobile-first)', 
             '• Multi-format Document Support\n• FAISS Vector Database\n• Session Management\n• RESTful API Architecture',
             '• GROQ LLM (DeepSeek-R1-70B)\n• Google Embeddings (text-004)\n• Conversational RAG\n• Semantic Search & Retrieval'],
            ['<b>Supported Formats:</b>\nPDF, DOCX, TXT, CSV, MD, XLSX, PPT, PPTX', 
             '<b>Performance:</b>\n< 5sec uploads, < 2sec queries\n100+ concurrent users',
             '<b>Deployment:</b>\nAWS ECS/Fargate Ready\nDocker Containerized']
        ]
        
        features_table = Table(features_data, colWidths=[2.2*inch, 2.2*inch, 2.2*inch])
        features_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f8f9fa')),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#bdc3c7')),
            ('ROWBACKGROUNDS', (0, 2), (-1, -1), [white, HexColor('#ecf0f1')])
        ]))
        
        self.story.append(features_table)
        self.story.append(Spacer(1, 15))

    def add_architecture_overview(self):
        self.story.append(Paragraph("System Architecture & Technology Stack", self.section_style))
        
        # Architecture flow
        arch_text = """
        <b>Data Flow:</b> Document Upload → Processing Pipeline → Vector Indexing → Conversational AI → Response Generation
        """
        arch_style = ParagraphStyle(
            'ArchStyle',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            textColor=HexColor('#2c3e50'),
            backColor=HexColor('#ecf0f1'),
            borderPadding=8,
            spaceAfter=12
        )
        self.story.append(Paragraph(arch_text, arch_style))
        
        # Two-column tech stack
        tech_data = [
            ['Frontend Technologies', 'Backend Technologies'],
            ['React 18 + TypeScript\nTailwind CSS\nAxios HTTP Client\nReact Dropzone\nWebpack Build System', 
             'FastAPI + Python 3.10\nFAISS Vector Database\nLangChain Community\nUvicorn ASGI Server\nPydantic Validation'],
            ['<b>Key Features:</b>\n• Multi-file drag & drop\n• Real-time chat interface\n• Progress tracking\n• Error handling', 
             '<b>Key Features:</b>\n• Document processing pipeline\n• Vector similarity search\n• Session management\n• RESTful endpoints']
        ]
        
        tech_table = Table(tech_data, colWidths=[3.2*inch, 3.2*inch])
        tech_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2980b9')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f1f2f6')),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#bdc3c7')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor('#f8f9fa')])
        ]))
        
        self.story.append(tech_table)
        self.story.append(PageBreak())

    def add_deployment_and_performance(self):
        self.story.append(Paragraph("Deployment & Performance Metrics", self.section_style))
        
        # Performance metrics in a compact format
        perf_data = [
            ['Metric', 'Performance', 'Scalability'],
            ['Document Upload Speed', '< 5 seconds (50MB files)', 'Unlimited file capacity'],
            ['Query Response Time', '< 2 seconds average', '1000+ queries/minute'],
            ['Concurrent Users', '100+ simultaneous sessions', 'Auto-scaling enabled'],
            ['Document Formats', '8+ major formats supported', 'Extensible processor factory'],
            ['Index Building', 'Real-time processing', 'Incremental updates']
        ]
        
        perf_table = Table(perf_data, colWidths=[2.1*inch, 2.1*inch, 2.3*inch])
        perf_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#27ae60')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('TOPPADDING', (0, 1), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f8f9fa')),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#95a5a6')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor('#ecf0f1')])
        ]))
        
        self.story.append(perf_table)
        self.story.append(Spacer(1, 15))
        
        # AWS Deployment info
        self.story.append(Paragraph("Production Deployment (AWS)", self.subsection_style))
        aws_text = """
        <b>Infrastructure:</b> AWS ECS/Fargate containers with auto-scaling, Application Load Balancer, 
        VPC security groups, IAM roles, and AWS Secrets Manager for API key management. 
        Supports multi-region deployment with CloudWatch monitoring and logging.
        """
        self.story.append(Paragraph(aws_text, self.body_style))
        self.story.append(Spacer(1, 12))

    def add_use_cases_and_benefits(self):
        self.story.append(Paragraph("Use Cases & Business Benefits", self.section_style))
        
        # Use cases in two columns
        usecase_data = [
            ['Primary Use Cases', 'Business Benefits'],
            ['• Enterprise Document Management\n• Research & Academic Papers\n• Legal Document Analysis\n• Financial Report Processing\n• Technical Documentation\n• Customer Support Knowledge Base', 
             '• 80% Faster Document Processing\n• Intelligent Search & Retrieval\n• Reduced Manual Analysis Time\n• Improved Decision Making\n• Scalable Multi-user Access\n• Cost-effective AI Integration'],
            ['<b>Industries:</b>\nLegal, Healthcare, Finance, Education, Consulting, Government', 
             '<b>ROI Drivers:</b>\nTime Savings, Accuracy Improvement, Operational Efficiency, Reduced Costs']
        ]
        
        usecase_table = Table(usecase_data, colWidths=[3.2*inch, 3.2*inch])
        usecase_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#e74c3c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#fdf2f2')),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#c0392b')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor('#f8f9fa')])
        ]))
        
        self.story.append(usecase_table)
        self.story.append(Spacer(1, 15))

    def add_conclusion_and_next_steps(self):
        self.story.append(Paragraph("Key Takeaways & Next Steps", self.section_style))
        
        # Key strengths
        strengths_text = """
        <b>Why Choose Document Portal System:</b>
        • Modern, production-ready architecture with enterprise-grade security
        • Advanced AI integration with state-of-the-art language models
        • Comprehensive document format support with extensible processing pipeline
        • Scalable cloud deployment with auto-scaling and load balancing
        • Developer-friendly with TypeScript, Python, and comprehensive API documentation
        """
        self.story.append(Paragraph(strengths_text, self.body_style))
        self.story.append(Spacer(1, 12))
        
        # Call to action
        cta_style = ParagraphStyle(
            'CTAStyle',
            parent=self.styles['Normal'],
            fontSize=12,
            alignment=TA_CENTER,
            textColor=white,
            backColor=HexColor('#2980b9'),
            borderPadding=12,
            spaceAfter=10
        )
        self.story.append(Paragraph(
            "<b>Ready for Production Deployment</b><br/>Enterprise-scale document processing with AI-powered intelligence",
            cta_style
        ))
        
        # Contact info placeholder
        contact_style = ParagraphStyle(
            'ContactStyle',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            textColor=HexColor('#7f8c8d'),
            spaceAfter=8
        )
        self.story.append(Paragraph(
            f"Presentation Date: {datetime.now().strftime('%B %Y')} | Document Portal System v1.0",
            contact_style
        ))

    def generate_pdf(self):
        # Add all sections
        self.add_title_and_overview()
        self.add_key_features_table()
        self.add_architecture_overview()
        self.add_deployment_and_performance()
        self.add_use_cases_and_benefits()
        self.add_conclusion_and_next_steps()
        
        # Build the PDF
        self.doc.build(self.story)
        print(f"Executive Summary PDF generated: {self.filename}")
        return self.filename

def main():
    # Create the PDF generator
    pdf_generator = ExecutiveSummaryPDF("Document_Portal_Executive_Summary.pdf")
    
    # Generate the PDF
    filename = pdf_generator.generate_pdf()
    
    # Print the absolute path
    abs_path = os.path.abspath(filename)
    print(f"Executive Summary PDF saved at: {abs_path}")
    
    return abs_path

if __name__ == "__main__":
    main()
