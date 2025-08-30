#!/usr/bin/env python3
"""
Enhanced PDF Generator with Frontend Mockups for Document Portal Presentation
Creates visual mockups and UI representations for better presentation clarity
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, KeepTogether
from reportlab.lib.colors import HexColor, black, white, grey
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing, Rect, String, Circle, Line
from reportlab.graphics.widgetbase import Widget
from reportlab.graphics import renderPDF
from datetime import datetime

class UImockupWidget(Widget):
    """Custom widget for creating UI mockups"""
    
    def __init__(self, width=400, height=300, title="UI Component"):
        Widget.__init__(self)
        self.width = width
        self.height = height
        self.title = title
        
    def draw(self):
        drawing = Drawing(self.width, self.height)
        
        # Main container
        drawing.add(Rect(0, 0, self.width, self.height, 
                        fillColor=HexColor('#f8f9fa'), 
                        strokeColor=HexColor('#dee2e6'), 
                        strokeWidth=1))
        
        # Header
        drawing.add(Rect(0, self.height-40, self.width, 40, 
                        fillColor=HexColor('#3498db'), 
                        strokeColor=HexColor('#2980b9'), 
                        strokeWidth=1))
        
        # Title
        drawing.add(String(10, self.height-25, self.title, 
                          fontName='Helvetica-Bold', 
                          fontSize=12, 
                          fillColor=white))
        
        return drawing

class EnhancedPresentationPDF:
    def __init__(self, filename="Document_Portal_Presentation_Enhanced.pdf"):
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
            fontSize=24,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=HexColor('#2c3e50')
        )
        
        # Section heading style
        self.section_style = ParagraphStyle(
            'SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=18,
            spaceBefore=15,
            spaceAfter=10,
            textColor=HexColor('#2980b9')
        )
        
        # Subsection style
        self.subsection_style = ParagraphStyle(
            'SubsectionHeading',
            parent=self.styles['Heading3'],
            fontSize=14,
            spaceBefore=10,
            spaceAfter=6,
            textColor=HexColor('#3498db')
        )
        
        # Body text
        self.body_style = ParagraphStyle(
            'CompactBody',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            alignment=TA_JUSTIFY,
            leading=12
        )
        
        # Bullet points
        self.bullet_style = ParagraphStyle(
            'CompactBullet',
            parent=self.styles['Normal'],
            fontSize=9,
            spaceAfter=3,
            leftIndent=15,
            bulletIndent=8,
            leading=11
        )

    def create_upload_interface_mockup(self):
        """Create a visual mockup of the upload interface"""
        drawing = Drawing(500, 300)
        
        # Main container
        drawing.add(Rect(10, 10, 480, 280, 
                        fillColor=white, 
                        strokeColor=HexColor('#dee2e6'), 
                        strokeWidth=2))
        
        # Header
        drawing.add(Rect(10, 250, 480, 40, 
                        fillColor=HexColor('#3498db'), 
                        strokeColor=HexColor('#2980b9'), 
                        strokeWidth=1))
        
        drawing.add(String(20, 265, "Multi-Document Upload Interface", 
                          fontName='Helvetica-Bold', 
                          fontSize=14, 
                          fillColor=white))
        
        # Upload area
        drawing.add(Rect(30, 150, 440, 80, 
                        fillColor=HexColor('#f8f9fa'), 
                        strokeColor=HexColor('#3498db'), 
                        strokeWidth=2,
                        strokeDashArray=[5, 5]))
        
        # Upload icon (circle)
        drawing.add(Circle(250, 190, 20, 
                          fillColor=HexColor('#3498db'), 
                          strokeColor=HexColor('#2980b9')))
        
        drawing.add(String(180, 165, "Drag & Drop Multiple Files Here", 
                          fontName='Helvetica-Bold', 
                          fontSize=12, 
                          fillColor=HexColor('#3498db')))
        
        drawing.add(String(200, 150, "or click to browse", 
                          fontName='Helvetica', 
                          fontSize=10, 
                          fillColor=HexColor('#7f8c8d')))
        
        # File list area
        drawing.add(String(30, 130, "Uploaded Files:", 
                          fontName='Helvetica-Bold', 
                          fontSize=10, 
                          fillColor=HexColor('#2c3e50')))
        
        # Sample uploaded files
        file_colors = [HexColor('#27ae60'), HexColor('#e74c3c'), HexColor('#f39c12')]
        file_names = ["Document.pdf ✓", "Report.xlsx ✓", "Data.csv ⏳"]
        
        for i, (name, color) in enumerate(zip(file_names, file_colors)):
            y_pos = 110 - i * 20
            drawing.add(Rect(30, y_pos, 15, 15, 
                            fillColor=color, 
                            strokeColor=color))
            drawing.add(String(50, y_pos + 3, name, 
                              fontName='Helvetica', 
                              fontSize=9, 
                              fillColor=HexColor('#2c3e50')))
        
        # Support formats
        drawing.add(String(30, 30, "Supported: PDF, DOCX, TXT, CSV, MD, XLSX, PPT, PPTX", 
                          fontName='Helvetica', 
                          fontSize=8, 
                          fillColor=HexColor('#7f8c8d')))
        
        return drawing

    def create_chat_interface_mockup(self):
        """Create a visual mockup of the chat interface"""
        drawing = Drawing(500, 350)
        
        # Main container
        drawing.add(Rect(10, 10, 480, 330, 
                        fillColor=white, 
                        strokeColor=HexColor('#dee2e6'), 
                        strokeWidth=2))
        
        # Header
        drawing.add(Rect(10, 300, 480, 40, 
                        fillColor=HexColor('#2980b9'), 
                        strokeColor=HexColor('#2980b9'), 
                        strokeWidth=1))
        
        drawing.add(String(20, 315, "Conversational RAG Interface", 
                          fontName='Helvetica-Bold', 
                          fontSize=14, 
                          fillColor=white))
        
        # Chat messages area
        # User message
        drawing.add(Rect(100, 250, 350, 30, 
                        fillColor=HexColor('#e3f2fd'), 
                        strokeColor=HexColor('#2196f3'), 
                        strokeWidth=1))
        drawing.add(String(110, 260, "What are the key findings in the uploaded financial reports?", 
                          fontName='Helvetica', 
                          fontSize=9, 
                          fillColor=HexColor('#1976d2')))
        
        # AI response
        drawing.add(Rect(50, 180, 400, 60, 
                        fillColor=HexColor('#f1f8e9'), 
                        strokeColor=HexColor('#4caf50'), 
                        strokeWidth=1))
        drawing.add(String(60, 220, "Based on the uploaded documents, I found several key insights:", 
                          fontName='Helvetica', 
                          fontSize=9, 
                          fillColor=HexColor('#2e7d32')))
        drawing.add(String(60, 205, "• Revenue increased by 15% compared to last quarter", 
                          fontName='Helvetica', 
                          fontSize=8, 
                          fillColor=HexColor('#2e7d32')))
        drawing.add(String(60, 190, "• Operating expenses were reduced by 8%", 
                          fontName='Helvetica', 
                          fontSize=8, 
                          fillColor=HexColor('#2e7d32')))
        
        # Input area
        drawing.add(Rect(30, 120, 400, 25, 
                        fillColor=HexColor('#f8f9fa'), 
                        strokeColor=HexColor('#dee2e6'), 
                        strokeWidth=1))
        drawing.add(String(35, 128, "Type your question here...", 
                          fontName='Helvetica', 
                          fontSize=9, 
                          fillColor=HexColor('#6c757d')))
        
        # Send button
        drawing.add(Rect(440, 120, 40, 25, 
                        fillColor=HexColor('#007bff'), 
                        strokeColor=HexColor('#0056b3'), 
                        strokeWidth=1))
        drawing.add(String(455, 128, "Send", 
                          fontName='Helvetica-Bold', 
                          fontSize=8, 
                          fillColor=white))
        
        # Document context indicator
        drawing.add(String(30, 100, "Context: 3 documents indexed | Session: financial_analysis_2025", 
                          fontName='Helvetica', 
                          fontSize=8, 
                          fillColor=HexColor('#6c757d')))
        
        # Features sidebar
        drawing.add(String(30, 80, "Features:", 
                          fontName='Helvetica-Bold', 
                          fontSize=9, 
                          fillColor=HexColor('#2c3e50')))
        features = ["• Multi-document querying", "• Context preservation", "• Real-time responses", "• Session management"]
        for i, feature in enumerate(features):
            drawing.add(String(30, 65 - i * 12, feature, 
                              fontName='Helvetica', 
                              fontSize=8, 
                              fillColor=HexColor('#495057')))
        
        return drawing

    def create_analysis_dashboard_mockup(self):
        """Create a visual mockup of the analysis dashboard"""
        drawing = Drawing(500, 300)
        
        # Main container
        drawing.add(Rect(10, 10, 480, 280, 
                        fillColor=white, 
                        strokeColor=HexColor('#dee2e6'), 
                        strokeWidth=2))
        
        # Header
        drawing.add(Rect(10, 250, 480, 40, 
                        fillColor=HexColor('#17a2b8'), 
                        strokeColor=HexColor('#138496'), 
                        strokeWidth=1))
        
        drawing.add(String(20, 265, "Document Analysis Dashboard", 
                          fontName='Helvetica-Bold', 
                          fontSize=14, 
                          fillColor=white))
        
        # Metrics cards
        metrics = [
            ("Documents", "15", HexColor('#28a745')),
            ("Total Words", "45,231", HexColor('#ffc107')),
            ("Avg. Size", "2.3MB", HexColor('#17a2b8')),
            ("Processing", "< 2s", HexColor('#6f42c1'))
        ]
        
        for i, (label, value, color) in enumerate(metrics):
            x_pos = 30 + i * 110
            # Card background
            drawing.add(Rect(x_pos, 200, 100, 40, 
                            fillColor=color, 
                            strokeColor=color, 
                            strokeWidth=1))
            # Value
            drawing.add(String(x_pos + 10, 225, value, 
                              fontName='Helvetica-Bold', 
                              fontSize=12, 
                              fillColor=white))
            # Label
            drawing.add(String(x_pos + 10, 210, label, 
                              fontName='Helvetica', 
                              fontSize=8, 
                              fillColor=white))
        
        # Document list
        drawing.add(String(30, 180, "Document Analysis Results:", 
                          fontName='Helvetica-Bold', 
                          fontSize=11, 
                          fillColor=HexColor('#2c3e50')))
        
        # Table header
        drawing.add(Rect(30, 155, 440, 20, 
                        fillColor=HexColor('#e9ecef'), 
                        strokeColor=HexColor('#dee2e6'), 
                        strokeWidth=1))
        drawing.add(String(35, 160, "Document", 
                          fontName='Helvetica-Bold', 
                          fontSize=9, 
                          fillColor=HexColor('#495057')))
        drawing.add(String(200, 160, "Type", 
                          fontName='Helvetica-Bold', 
                          fontSize=9, 
                          fillColor=HexColor('#495057')))
        drawing.add(String(300, 160, "Status", 
                          fontName='Helvetica-Bold', 
                          fontSize=9, 
                          fillColor=HexColor('#495057')))
        drawing.add(String(400, 160, "Insights", 
                          fontName='Helvetica-Bold', 
                          fontSize=9, 
                          fillColor=HexColor('#495057')))
        
        # Sample rows
        docs = [
            ("Financial_Report_Q4.pdf", "PDF", "✓ Analyzed", "📊 Charts"),
            ("Customer_Data.csv", "CSV", "✓ Processed", "📈 Stats"),
            ("Meeting_Notes.docx", "DOCX", "⏳ Processing", "📝 Text")
        ]
        
        for i, (name, doc_type, status, insight) in enumerate(docs):
            y_pos = 135 - i * 20
            # Alternating row colors
            bg_color = HexColor('#f8f9fa') if i % 2 == 0 else white
            drawing.add(Rect(30, y_pos, 440, 20, 
                            fillColor=bg_color, 
                            strokeColor=HexColor('#dee2e6'), 
                            strokeWidth=0.5))
            
            drawing.add(String(35, y_pos + 5, name[:20] + "...", 
                              fontName='Helvetica', 
                              fontSize=8, 
                              fillColor=HexColor('#495057')))
            drawing.add(String(200, y_pos + 5, doc_type, 
                              fontName='Helvetica', 
                              fontSize=8, 
                              fillColor=HexColor('#495057')))
            drawing.add(String(300, y_pos + 5, status, 
                              fontName='Helvetica', 
                              fontSize=8, 
                              fillColor=HexColor('#495057')))
            drawing.add(String(400, y_pos + 5, insight, 
                              fontName='Helvetica', 
                              fontSize=8, 
                              fillColor=HexColor('#495057')))
        
        # Export button
        drawing.add(Rect(380, 30, 80, 25, 
                        fillColor=HexColor('#28a745'), 
                        strokeColor=HexColor('#1e7e34'), 
                        strokeWidth=1))
        drawing.add(String(405, 38, "Export", 
                          fontName='Helvetica-Bold', 
                          fontSize=9, 
                          fillColor=white))
        
        return drawing

    def create_architecture_diagram(self):
        """Create a simplified architecture diagram"""
        drawing = Drawing(500, 200)
        
        # Frontend box
        drawing.add(Rect(30, 120, 120, 60, 
                        fillColor=HexColor('#61dafb'), 
                        strokeColor=HexColor('#282c34'), 
                        strokeWidth=2))
        drawing.add(String(60, 145, "Frontend", 
                          fontName='Helvetica-Bold', 
                          fontSize=12, 
                          fillColor=HexColor('#282c34')))
        drawing.add(String(35, 130, "React + TypeScript", 
                          fontName='Helvetica', 
                          fontSize=9, 
                          fillColor=HexColor('#282c34')))
        
        # Arrow 1
        drawing.add(Line(150, 150, 190, 150, strokeColor=HexColor('#495057'), strokeWidth=2))
        drawing.add(String(160, 155, "HTTP/REST", 
                          fontName='Helvetica', 
                          fontSize=8, 
                          fillColor=HexColor('#495057')))
        
        # Backend box
        drawing.add(Rect(190, 120, 120, 60, 
                        fillColor=HexColor('#306998'), 
                        strokeColor=HexColor('#ffd43b'), 
                        strokeWidth=2))
        drawing.add(String(230, 145, "Backend", 
                          fontName='Helvetica-Bold', 
                          fontSize=12, 
                          fillColor=white))
        drawing.add(String(195, 130, "FastAPI + Python", 
                          fontName='Helvetica', 
                          fontSize=9, 
                          fillColor=white))
        
        # Arrow 2
        drawing.add(Line(310, 150, 350, 150, strokeColor=HexColor('#495057'), strokeWidth=2))
        drawing.add(String(320, 155, "Vector DB", 
                          fontName='Helvetica', 
                          fontSize=8, 
                          fillColor=HexColor('#495057')))
        
        # AI/Database box
        drawing.add(Rect(350, 120, 120, 60, 
                        fillColor=HexColor('#ff6b6b'), 
                        strokeColor=HexColor('#c92a2a'), 
                        strokeWidth=2))
        drawing.add(String(390, 145, "AI Engine", 
                          fontName='Helvetica-Bold', 
                          fontSize=12, 
                          fillColor=white))
        drawing.add(String(355, 130, "FAISS + GROQ LLM", 
                          fontName='Helvetica', 
                          fontSize=9, 
                          fillColor=white))
        
        # Data flow
        drawing.add(String(50, 100, "User Interaction", 
                          fontName='Helvetica', 
                          fontSize=9, 
                          fillColor=HexColor('#495057')))
        drawing.add(String(210, 100, "Document Processing", 
                          fontName='Helvetica', 
                          fontSize=9, 
                          fillColor=HexColor('#495057')))
        drawing.add(String(370, 100, "AI Analysis", 
                          fontName='Helvetica', 
                          fontSize=9, 
                          fillColor=HexColor('#495057')))
        
        # Document types
        drawing.add(String(150, 70, "Supported Formats:", 
                          fontName='Helvetica-Bold', 
                          fontSize=10, 
                          fillColor=HexColor('#2c3e50')))
        drawing.add(String(130, 55, "PDF • DOCX • TXT • CSV • MD • XLSX • PPT • PPTX", 
                          fontName='Helvetica', 
                          fontSize=9, 
                          fillColor=HexColor('#495057')))
        
        # Performance indicators
        drawing.add(String(30, 30, "Performance: < 5s upload • < 2s queries • 100+ concurrent users", 
                          fontName='Helvetica-Bold', 
                          fontSize=9, 
                          fillColor=HexColor('#28a745')))
        
        return drawing

    def add_cover_page(self):
        # Title
        self.story.append(Spacer(1, 0.5*inch))
        self.story.append(Paragraph("Document Portal System", self.title_style))
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=self.styles['Normal'],
            fontSize=16,
            alignment=TA_CENTER,
            textColor=HexColor('#34495e'),
            spaceAfter=30
        )
        self.story.append(Paragraph("AI-Powered Document Management Platform", subtitle_style))
        
        # Add architecture diagram
        self.story.append(self.create_architecture_diagram())
        self.story.append(Spacer(1, 0.3*inch))
        
        # Key stats
        stats_text = """
        <b>Enterprise-Ready Solution:</b> Modern web architecture with AI-powered document processing, 
        supporting 8+ file formats with real-time conversational querying capabilities.
        """
        self.story.append(Paragraph(stats_text, self.body_style))
        
        self.story.append(PageBreak())

    def add_frontend_capabilities_with_mockups(self):
        self.story.append(Paragraph("Frontend Capabilities & User Interface", self.section_style))
        
        # Technology overview
        tech_text = """
        <b>Modern React Architecture:</b> Built with React 18, TypeScript, and Tailwind CSS for 
        responsive design and optimal user experience across all devices.
        """
        self.story.append(Paragraph(tech_text, self.body_style))
        self.story.append(Spacer(1, 10))
        
        # Upload interface mockup
        self.story.append(Paragraph("1. Multi-Document Upload Interface", self.subsection_style))
        self.story.append(self.create_upload_interface_mockup())
        self.story.append(Spacer(1, 10))
        
        # Features list
        upload_features = [
            "Drag & drop multiple files simultaneously",
            "Real-time upload progress tracking",
            "Client-side validation and error handling",
            "Support for 8+ document formats",
            "Batch processing with individual status monitoring"
        ]
        
        for feature in upload_features:
            self.story.append(Paragraph(f"• {feature}", self.bullet_style))
        
        self.story.append(PageBreak())
        
        # Chat interface
        self.story.append(Paragraph("2. Conversational RAG Interface", self.subsection_style))
        self.story.append(self.create_chat_interface_mockup())
        self.story.append(Spacer(1, 10))
        
        chat_features = [
            "Natural language querying across all uploaded documents",
            "Context-aware responses with document citations",
            "Real-time message streaming for immediate feedback",
            "Session-based conversation history preservation",
            "Multi-turn dialogue with memory retention"
        ]
        
        for feature in chat_features:
            self.story.append(Paragraph(f"• {feature}", self.bullet_style))
        
        self.story.append(PageBreak())

    def add_analysis_dashboard_with_mockup(self):
        self.story.append(Paragraph("3. Document Analysis Dashboard", self.subsection_style))
        self.story.append(self.create_analysis_dashboard_mockup())
        self.story.append(Spacer(1, 10))
        
        analysis_features = [
            "Real-time document processing statistics",
            "Visual analytics and metadata display",
            "Document structure and content insights",
            "Export capabilities for processed data",
            "Search integration across document corpus"
        ]
        
        for feature in analysis_features:
            self.story.append(Paragraph(f"• {feature}", self.bullet_style))
        
        self.story.append(Spacer(1, 15))

    def add_backend_architecture(self):
        self.story.append(Paragraph("Backend Architecture & AI Processing", self.section_style))
        
        # Technology stack table
        tech_data = [
            ['Component', 'Technology', 'Purpose'],
            ['Web Framework', 'FastAPI + Python 3.10', 'High-performance async API server'],
            ['Vector Database', 'FAISS', 'Similarity search and retrieval'],
            ['Language Model', 'GROQ DeepSeek-R1-70B', 'Natural language understanding'],
            ['Embeddings', 'Google Text-Embedding-004', 'Semantic text representation'],
            ['Document Processing', 'LangChain Community', 'Multi-format document parsing'],
            ['Server', 'Uvicorn ASGI', 'Production-ready web server']
        ]
        
        tech_table = Table(tech_data, colWidths=[2*inch, 2.2*inch, 2.3*inch])
        tech_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2980b9')),
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
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#dee2e6')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor('#f1f3f4')])
        ]))
        
        self.story.append(tech_table)
        self.story.append(Spacer(1, 15))
        
        # Processing pipeline
        pipeline_text = """
        <b>Document Processing Pipeline:</b><br/>
        Upload → Format Detection → Content Extraction → Text Chunking → 
        Vector Embedding → FAISS Indexing → Retrieval Ready
        """
        pipeline_style = ParagraphStyle(
            'PipelineStyle',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            textColor=HexColor('#2c3e50'),
            backColor=HexColor('#e8f4fd'),
            borderPadding=10,
            spaceAfter=15
        )
        self.story.append(Paragraph(pipeline_text, pipeline_style))

    def add_performance_and_deployment(self):
        self.story.append(Paragraph("Performance Metrics & Deployment", self.section_style))
        
        # Performance metrics
        perf_data = [
            ['Metric', 'Performance', 'Scalability Features'],
            ['Document Upload', '< 5 seconds (50MB)', 'Parallel processing support'],
            ['Query Response', '< 2 seconds average', 'Optimized vector search'],
            ['Concurrent Users', '100+ simultaneous', 'Auto-scaling enabled'],
            ['Index Building', 'Real-time processing', 'Incremental updates'],
            ['Document Capacity', 'Unlimited storage', 'Cloud-native architecture'],
            ['File Formats', '8+ major types', 'Extensible processor factory']
        ]
        
        perf_table = Table(perf_data, colWidths=[2*inch, 2*inch, 2.5*inch])
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
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#dee2e6')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor('#f1f3f4')])
        ]))
        
        self.story.append(perf_table)
        self.story.append(Spacer(1, 15))
        
        # AWS deployment info
        aws_text = """
        <b>Production-Ready AWS Deployment:</b> Containerized deployment with ECS/Fargate, 
        auto-scaling, load balancing, VPC security, IAM roles, and Secrets Manager integration. 
        Monitoring via CloudWatch with comprehensive logging and health checks.
        """
        self.story.append(Paragraph(aws_text, self.body_style))

    def add_conclusion_with_cta(self):
        self.story.append(Spacer(1, 20))
        self.story.append(Paragraph("Business Value & Next Steps", self.section_style))
        
        # Value proposition
        value_data = [
            ['Business Benefit', 'Technical Advantage'],
            ['80% faster document processing\nReduced manual analysis time\nImproved decision-making speed\nScalable multi-user access', 
             'Modern React/TypeScript frontend\nHigh-performance Python backend\nAdvanced AI integration\nEnterprise-grade security'],
            ['ROI through operational efficiency\nCost-effective AI implementation\nReduced infrastructure overhead\nImproved user productivity', 
             'Cloud-native architecture\nAuto-scaling capabilities\nComprehensive monitoring\nExtensible design patterns']
        ]
        
        value_table = Table(value_data, colWidths=[3.2*inch, 3.2*inch])
        value_table.setStyle(TableStyle([
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
        
        self.story.append(value_table)
        self.story.append(Spacer(1, 20))
        
        # Call to action
        cta_style = ParagraphStyle(
            'CTAStyle',
            parent=self.styles['Normal'],
            fontSize=14,
            alignment=TA_CENTER,
            textColor=white,
            backColor=HexColor('#2980b9'),
            borderPadding=15,
            spaceAfter=10
        )
        self.story.append(Paragraph(
            "<b>Ready for Enterprise Deployment</b><br/>Transform your document management with AI-powered intelligence",
            cta_style
        ))

    def generate_pdf(self):
        # Add all sections
        self.add_cover_page()
        self.add_frontend_capabilities_with_mockups()
        self.add_analysis_dashboard_with_mockup()
        self.add_backend_architecture()
        self.add_performance_and_deployment()
        self.add_conclusion_with_cta()
        
        # Build the PDF
        self.doc.build(self.story)
        print(f"Enhanced PDF with mockups generated: {self.filename}")
        return self.filename

def main():
    # Create the enhanced PDF generator
    pdf_generator = EnhancedPresentationPDF("Document_Portal_Presentation_With_Mockups.pdf")
    
    # Generate the PDF
    filename = pdf_generator.generate_pdf()
    
    # Print the absolute path
    abs_path = os.path.abspath(filename)
    print(f"Enhanced PDF with UI mockups saved at: {abs_path}")
    
    return abs_path

if __name__ == "__main__":
    main()
