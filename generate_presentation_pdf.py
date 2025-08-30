#!/usr/bin/env python3
"""
PDF Generator for Document Portal Presentation
Converts the markdown presentation to a professional PDF format
"""

import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.colors import HexColor, black, white, blue
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from datetime import datetime

class DocumentPortalPDF:
    def __init__(self, filename="Document_Portal_Presentation.pdf"):
        self.filename = filename
        self.doc = SimpleDocTemplate(
            filename,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=1*inch,
            bottomMargin=1*inch
        )
        self.styles = getSampleStyleSheet()
        self.story = []
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        # Title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=HexColor('#2c3e50')
        )
        
        # Subtitle style
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=HexColor('#34495e')
        )
        
        # Section heading style
        self.section_style = ParagraphStyle(
            'SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=18,
            spaceBefore=20,
            spaceAfter=12,
            textColor=HexColor('#2980b9')
        )
        
        # Subsection style
        self.subsection_style = ParagraphStyle(
            'SubsectionHeading',
            parent=self.styles['Heading3'],
            fontSize=14,
            spaceBefore=15,
            spaceAfter=8,
            textColor=HexColor('#3498db')
        )
        
        # Body text style
        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            alignment=TA_JUSTIFY,
            leading=14
        )
        
        # Bullet point style
        self.bullet_style = ParagraphStyle(
            'BulletPoint',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=4,
            leftIndent=20,
            bulletIndent=10,
            leading=12
        )

    def add_cover_page(self):
        # Title
        self.story.append(Spacer(1, 1*inch))
        self.story.append(Paragraph("Document Portal System", self.title_style))
        self.story.append(Paragraph("Architecture & Technology Stack Overview", self.subtitle_style))
        
        # Date
        current_date = datetime.now().strftime("%B %Y")
        date_style = ParagraphStyle(
            'DateStyle',
            parent=self.styles['Normal'],
            fontSize=12,
            alignment=TA_CENTER,
            textColor=HexColor('#7f8c8d')
        )
        self.story.append(Spacer(1, 0.5*inch))
        self.story.append(Paragraph(f"Presentation Date: {current_date}", date_style))
        
        # Logo placeholder or company info
        self.story.append(Spacer(1, 1*inch))
        company_style = ParagraphStyle(
            'CompanyStyle',
            parent=self.styles['Normal'],
            fontSize=14,
            alignment=TA_CENTER,
            textColor=HexColor('#2c3e50')
        )
        self.story.append(Paragraph("AI-Powered Document Management Platform", company_style))
        
        self.story.append(PageBreak())

    def add_executive_summary(self):
        self.story.append(Paragraph("Executive Summary", self.section_style))
        
        summary_text = """
        The Document Portal System is a state-of-the-art AI-powered document management and 
        conversational RAG (Retrieval-Augmented Generation) platform that enables intelligent 
        document processing, analysis, and interactive querying across multiple document formats.
        """
        self.story.append(Paragraph(summary_text, self.body_style))
        self.story.append(Spacer(1, 12))
        
        # Key capabilities
        self.story.append(Paragraph("Key Capabilities", self.subsection_style))
        capabilities = [
            "Multi-format Document Support: PDF, DOCX, TXT, CSV, MD, XLSX, PPT, PPTX",
            "Conversational AI Interface: Natural language querying across documents",
            "Real-time Document Analysis: Instant insights and summaries",
            "Document Comparison: AI-powered comparative analysis",
            "Scalable Cloud Deployment: AWS ECS/Fargate ready"
        ]
        
        for capability in capabilities:
            self.story.append(Paragraph(f"• {capability}", self.bullet_style))
        
        self.story.append(PageBreak())

    def add_frontend_section(self):
        self.story.append(Paragraph("Frontend Architecture & Capabilities", self.section_style))
        
        # Technology Stack
        self.story.append(Paragraph("Technology Stack", self.subsection_style))
        frontend_tech = [
            "Framework: React 18 with TypeScript",
            "Styling: Tailwind CSS for responsive design",
            "State Management: React Hooks (useState, useEffect)",
            "HTTP Client: Axios with interceptors",
            "File Handling: React Dropzone for drag-and-drop uploads",
            "Icons: Heroicons for consistent UI elements",
            "Build Tool: Create React App with Webpack"
        ]
        
        for tech in frontend_tech:
            self.story.append(Paragraph(f"• {tech}", self.bullet_style))
        
        self.story.append(Spacer(1, 12))
        
        # Core Features
        self.story.append(Paragraph("Core Features", self.subsection_style))
        
        # Multi-Document Upload
        self.story.append(Paragraph("1. Multi-Document Upload Interface", self.subsection_style))
        upload_features = [
            "Drag & Drop Support: Intuitive file upload with visual feedback",
            "Multiple File Selection: Batch upload capability for efficient processing",
            "Real-time Progress Tracking: Individual file status monitoring",
            "Format Validation: Client-side file type and size validation",
            "Error Handling: Comprehensive error messaging and recovery"
        ]
        for feature in upload_features:
            self.story.append(Paragraph(f"• {feature}", self.bullet_style))
        
        # Interactive Chat
        self.story.append(Paragraph("2. Interactive Chat Interface", self.subsection_style))
        chat_features = [
            "Real-time Messaging: WebSocket-like experience with instant responses",
            "Context Preservation: Session-based conversation history",
            "Multi-document Querying: Cross-document intelligence",
            "Typing Indicators: Enhanced user experience with loading states",
            "Message History: Persistent conversation tracking"
        ]
        for feature in chat_features:
            self.story.append(Paragraph(f"• {feature}", self.bullet_style))
        
        # Document Analysis
        self.story.append(Paragraph("3. Document Analysis Dashboard", self.subsection_style))
        analysis_features = [
            "Visual Analytics: Document structure and content visualization",
            "Metadata Display: File properties and processing statistics",
            "Search Integration: Full-text search across uploaded documents",
            "Export Capabilities: Download processed data and insights"
        ]
        for feature in analysis_features:
            self.story.append(Paragraph(f"• {feature}", self.bullet_style))
        
        self.story.append(PageBreak())

    def add_backend_section(self):
        self.story.append(Paragraph("Backend Architecture & Capabilities", self.section_style))
        
        # Technology Stack
        self.story.append(Paragraph("Technology Stack", self.subsection_style))
        backend_tech = [
            "Framework: FastAPI (Python 3.10+)",
            "Vector Database: FAISS for similarity search",
            "Document Processing: LangChain Community",
            "AI Models: GROQ DeepSeek-R1-Distill-Llama-70B (LLM)",
            "Embeddings: Google Text-Embedding-004",
            "Server: Uvicorn ASGI server",
            "Configuration: YAML-based configuration management"
        ]
        
        for tech in backend_tech:
            self.story.append(Paragraph(f"• {tech}", self.bullet_style))
        
        self.story.append(Spacer(1, 12))
        
        # Processing Pipeline
        self.story.append(Paragraph("Core Processing Pipeline", self.subsection_style))
        pipeline_text = """
        DocumentProcessorFactory → ExcelProcessor/PDFProcessor → 
        TextSplitter → Embeddings → FAISS Index → Retriever
        """
        pipeline_style = ParagraphStyle(
            'PipelineStyle',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            textColor=HexColor('#34495e'),
            backColor=HexColor('#ecf0f1'),
            borderPadding=8
        )
        self.story.append(Paragraph(pipeline_text, pipeline_style))
        self.story.append(Spacer(1, 12))
        
        # Core Systems
        systems = [
            ("Document Ingestion System", [
                "Multi-format Support: Specialized processors for each file type",
                "Intelligent Chunking: Context-aware text segmentation",
                "Metadata Preservation: Document properties and structure retention",
                "Vector Indexing: High-performance similarity search preparation"
            ]),
            ("Conversational RAG Engine", [
                "Query Processing: Natural language understanding and intent recognition",
                "Context Retrieval: Semantic search across document corpus",
                "Response Generation: AI-powered answer synthesis",
                "Session Management: Multi-turn conversation state tracking"
            ]),
            ("Document Analysis Engine", [
                "Content Extraction: Text, tables, and metadata parsing",
                "Statistical Analysis: Document metrics and insights",
                "Structure Recognition: Heading hierarchy and section identification",
                "Relationship Mapping: Inter-document connection analysis"
            ])
        ]
        
        for system_name, features in systems:
            self.story.append(Paragraph(f"{system_name}", self.subsection_style))
            for feature in features:
                self.story.append(Paragraph(f"• {feature}", self.bullet_style))
            self.story.append(Spacer(1, 8))
        
        self.story.append(PageBreak())

    def add_deployment_section(self):
        self.story.append(Paragraph("Deployment & Performance", self.section_style))
        
        # AWS Deployment
        self.story.append(Paragraph("Production Deployment", self.subsection_style))
        deployment_features = [
            "AWS ECS/Fargate: Serverless container orchestration",
            "Load Balancing: High availability configuration",
            "Auto Scaling: Dynamic resource allocation",
            "Security: IAM roles and secrets management",
            "Monitoring: CloudWatch integration with custom metrics"
        ]
        for feature in deployment_features:
            self.story.append(Paragraph(f"• {feature}", self.bullet_style))
        
        self.story.append(Spacer(1, 12))
        
        # Performance Metrics
        self.story.append(Paragraph("Performance Metrics", self.subsection_style))
        
        # Create performance table
        performance_data = [
            ['Metric', 'Performance'],
            ['Document Upload', '< 5 seconds for 50MB files'],
            ['Query Processing', '< 2 seconds average response'],
            ['Index Building', 'Real-time for most document types'],
            ['Concurrent Users', 'Supports 100+ simultaneous sessions'],
            ['Document Capacity', 'Unlimited with proper storage'],
            ['File Format Support', '8+ major document types']
        ]
        
        performance_table = Table(performance_data, colWidths=[2.5*inch, 3*inch])
        performance_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#ecf0f1')),
            ('GRID', (0, 0), (-1, -1), 1, black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor('#f8f9fa')])
        ]))
        
        self.story.append(performance_table)
        self.story.append(Spacer(1, 12))
        
        # Security Features
        self.story.append(Paragraph("Security & Compliance", self.subsection_style))
        security_features = [
            "Data Protection: File validation and input sanitization",
            "Infrastructure Security: VPC configuration and security groups",
            "Encryption: SSL/TLS end-to-end encryption",
            "Access Control: Role-based permissions and IAM integration",
            "Audit Logging: Comprehensive security event tracking"
        ]
        for feature in security_features:
            self.story.append(Paragraph(f"• {feature}", self.bullet_style))

    def add_conclusion(self):
        self.story.append(Spacer(1, 20))
        self.story.append(Paragraph("Conclusion", self.section_style))
        
        conclusion_text = """
        The Document Portal System represents a cutting-edge solution for intelligent document 
        management, combining modern web technologies with advanced AI capabilities to deliver 
        a seamless user experience for document processing, analysis, and conversational querying.
        """
        self.story.append(Paragraph(conclusion_text, self.body_style))
        
        self.story.append(Spacer(1, 12))
        self.story.append(Paragraph("Key Strengths", self.subsection_style))
        strengths = [
            "Modern, scalable architecture with microservices design",
            "Comprehensive document format support across 8+ file types",
            "Advanced AI-powered features with state-of-the-art models",
            "Production-ready deployment with AWS cloud integration",
            "Extensible and maintainable codebase with TypeScript and Python"
        ]
        
        for strength in strengths:
            self.story.append(Paragraph(f"• {strength}", self.bullet_style))
        
        # Call to action
        self.story.append(Spacer(1, 20))
        cta_style = ParagraphStyle(
            'CTAStyle',
            parent=self.styles['Normal'],
            fontSize=12,
            alignment=TA_CENTER,
            textColor=HexColor('#2980b9'),
            backColor=HexColor('#f8f9fa'),
            borderPadding=10
        )
        self.story.append(Paragraph(
            "Ready for enterprise-scale document processing with enterprise-grade security and performance.",
            cta_style
        ))

    def generate_pdf(self):
        # Add all sections
        self.add_cover_page()
        self.add_executive_summary()
        self.add_frontend_section()
        self.add_backend_section()
        self.add_deployment_section()
        self.add_conclusion()
        
        # Build the PDF
        self.doc.build(self.story)
        print(f"PDF generated successfully: {self.filename}")
        return self.filename

def main():
    # Create the PDF generator
    pdf_generator = DocumentPortalPDF("Document_Portal_Presentation.pdf")
    
    # Generate the PDF
    filename = pdf_generator.generate_pdf()
    
    # Print the absolute path
    abs_path = os.path.abspath(filename)
    print(f"PDF saved at: {abs_path}")
    
    return abs_path

if __name__ == "__main__":
    main()
