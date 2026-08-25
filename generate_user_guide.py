"""
NHS Personalised Care Dashboard - PDF User Guide Generator
Run: python generate_user_guide.py
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.linecharts import HorizontalLineChart
import matplotlib.pyplot as plt
import io
from PIL import Image as PILImage

class UserGuideGenerator:
    def __init__(self, filename="nhs_personalised_care_guide.pdf"):
        self.filename = filename
        self.doc = SimpleDocTemplate(filename, pagesize=A4, 
                                   rightMargin=72, leftMargin=72,
                                   topMargin=72, bottomMargin=72)
        self.styles = self._create_styles()
        self.story = []
        
    def _create_styles(self):
        """Create custom styles for the PDF"""
        styles = getSampleStyleSheet()
        
        # Title style
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#005EB8'),
            alignment=TA_CENTER,
            spaceAfter=30,
            fontName='Helvetica-Bold'
        ))
        
        # Section header
        styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=styles['Heading2'],
            fontSize=18,
            textColor=colors.HexColor('#003D7A'),
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        ))
        
        # Subsection header
        styles.add(ParagraphStyle(
            name='SubSectionHeader',
            parent=styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#005EB8'),
            spaceAfter=8,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Body text
        styles.add(ParagraphStyle(
            name='CustomBody',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#212121'),
            spaceAfter=8,
            fontName='Helvetica'
        ))
        
        # Bullet point
        styles.add(ParagraphStyle(
            name='BulletPoint',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#212121'),
            spaceAfter=4,
            leftIndent=20,
            fontName='Helvetica'
        ))
        
        # Footer
        styles.add(ParagraphStyle(
            name='Footer',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#6B6B6B'),
            alignment=TA_CENTER,
            fontName='Helvetica'
        ))
        
        return styles
    
    def add_title_page(self):
        """Add title page"""
        self.story.append(Spacer(1, 2*inch))
        
        # NHS Logo placeholder
        self.story.append(Paragraph(
            "🏥 NHS Personalised Care", 
            self.styles['CustomTitle']
        ))
        
        self.story.append(Spacer(1, 0.5*inch))
        self.story.append(Paragraph(
            "User Guide & Dashboard Tutorial", 
            self.styles['SubSectionHeader']
        ))
        
        self.story.append(Spacer(1, 0.5*inch))
        self.story.append(Paragraph(
            f"Version 2.0 • {datetime.now().strftime('%B %d, %Y')}", 
            self.styles['CustomBody']
        ))
        
        self.story.append(Spacer(1, 2*inch))
        self.story.append(Paragraph(
            "NHS England Comprehensive Model for Personalised Care", 
            self.styles['CustomBody']
        ))
        
        self.story.append(PageBreak())
    
    def add_table_of_contents(self):
        """Add table of contents"""
        self.story.append(Paragraph("Table of Contents", self.styles['SectionHeader']))
        self.story.append(Spacer(1, 0.2*inch))
        
        toc_items = [
            ("1. Introduction", 1),
            ("2. Getting Started", 2),
            ("3. Dashboard Overview", 3),
            ("4. Patient Management", 4),
            ("5. Goal Management", 5),
            ("6. Outcome Tracking", 6),
            ("7. AI Insights", 7),
            ("8. Clinical Notes", 8),
            ("9. Settings & Configuration", 9),
            ("10. Troubleshooting", 10),
            ("11. API Reference", 11),
        ]
        
        for item, page in toc_items:
            self.story.append(Paragraph(
                f"{item} ..................................... {page}", 
                self.styles['CustomBody']
            ))
        
        self.story.append(PageBreak())
    
    def add_introduction(self):
        """Add introduction section"""
        self.story.append(Paragraph("1. Introduction", self.styles['SectionHeader']))
        
        intro_text = """
        The NHS Personalised Care System is a comprehensive healthcare management platform 
        designed to implement the NHS England Comprehensive Model for Personalised Care. 
        This system helps patients and healthcare providers track health goals, monitor outcomes, 
        and leverage AI-powered insights for better health management.
        """
        self.story.append(Paragraph(intro_text, self.styles['CustomBody']))
        
        self.story.append(Spacer(1, 0.2*inch))
        
        features = [
            "✅ Patient Management with NHS numbers",
            "✅ Personalised Care Plans",
            "✅ Goal Tracking with progress indicators",
            "✅ Outcome Measurement against targets",
            "✅ Patient Activation Measure (PAM) scoring",
            "✅ AI-powered risk prediction and recommendations",
            "✅ Clinical Notes with sentiment analysis",
            "✅ Offline-first Progressive Web App",
            "✅ Real-time updates via WebSocket"
        ]
        
        for feature in features:
            self.story.append(Paragraph(feature, self.styles['BulletPoint']))
        
        self.story.append(PageBreak())
    
    def add_getting_started(self):
        """Add getting started section"""
        self.story.append(Paragraph("2. Getting Started", self.styles['SectionHeader']))
        
        # Access instructions
        self.story.append(Paragraph("2.1 Accessing the Application", self.styles['SubSectionHeader']))
        
        access_steps = [
            "1. Open your web browser",
            "2. Navigate to: https://nhs-personalised-care.vercel.app",
            "3. The dashboard will load automatically",
            "4. Use the sidebar to navigate between sections"
        ]
        
        for step in access_steps:
            self.story.append(Paragraph(step, self.styles['BulletPoint']))
        
        self.story.append(Spacer(1, 0.2*inch))
        
        # Demo accounts
        self.story.append(Paragraph("2.2 Demo Accounts", self.styles['SubSectionHeader']))
        
        demo_data = [
            ["NHS Number", "Name", "Role"],
            ["NHS123456", "Sarah Johnson", "Patient"],
            ["NHS789012", "James Smith", "Patient"],
            ["NHS345678", "Aisha Patel", "Patient"]
        ]
        
        table = Table(demo_data, colWidths=[2*inch, 2*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#005EB8')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F5F7FA')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E8ECF0'))
        ]))
        
        self.story.append(table)
        self.story.append(PageBreak())
    
    def add_dashboard_overview(self):
        """Add dashboard overview section with chart"""
        self.story.append(Paragraph("3. Dashboard Overview", self.styles['SectionHeader']))
        
        self.story.append(Paragraph(
            "The dashboard provides a comprehensive overview of your health status and progress.",
            self.styles['CustomBody']
        ))
        
        self.story.append(Spacer(1, 0.2*inch))
        
        # Create a sample chart
        chart = self._create_sample_chart()
        self.story.append(chart)
        
        self.story.append(Spacer(1, 0.2*inch))
        
        # Dashboard components
        components = [
            ("Patient Activation Measure (PAM)", "Shows the patient's activation level and score"),
            ("Statistics Cards", "Displays goals, completion rate, outcomes, and decisions"),
            ("Risk Assessment", "Shows current risk level and factors"),
            ("Recent Activity", "Lists recent actions and updates")
        ]
        
        for title, desc in components:
            self.story.append(Paragraph(f"<b>{title}</b>", self.styles['SubSectionHeader']))
            self.story.append(Paragraph(desc, self.styles['CustomBody']))
        
        self.story.append(PageBreak())
    
    def _create_sample_chart(self):
        """Create a sample chart for the PDF"""
        drawing = Drawing(400, 200)
        
        # Create a simple bar chart
        bc = VerticalBarChart()
        bc.x = 50
        bc.y = 50
        bc.width = 300
        bc.height = 120
        bc.data = [[10, 8, 5, 3, 2]]
        bc.categoryAxis.categoryNames = ['Total', 'Active', 'Completed', 'Partial', 'Abandoned']
        bc.categoryAxis.labels.boxAnchor = 'ne'
        bc.categoryAxis.labels.dx = 8
        bc.categoryAxis.labels.dy = -2
        bc.categoryAxis.labels.angle = 0
        bc.valueAxis.valueMin = 0
        bc.valueAxis.valueMax = 12
        bc.bars[0].fillColor = colors.HexColor('#005EB8')
        
        drawing.add(bc)
        return drawing
    
    def add_patient_management(self):
        """Add patient management section"""
        self.story.append(Paragraph("4. Patient Management", self.styles['SectionHeader']))
        
        steps = [
            ("4.1 Adding a New Patient", [
                "Click '+ New Patient' button",
                "Fill in NHS Number, Name, Date of Birth, and Gender",
                "Click 'Add Patient' to save"
            ]),
            ("4.2 Switching Patients", [
                "Navigate to the 'Patients' tab",
                "Click 'Select' next to the desired patient",
                "The dashboard will update with their data"
            ])
        ]
        
        for title, steps_list in steps:
            self.story.append(Paragraph(title, self.styles['SubSectionHeader']))
            for step in steps_list:
                self.story.append(Paragraph(step, self.styles['BulletPoint']))
            self.story.append(Spacer(1, 0.1*inch))
        
        self.story.append(PageBreak())
    
    def add_goal_management(self):
        """Add goal management section"""
        self.story.append(Paragraph("5. Goal Management", self.styles['SectionHeader']))
        
        self.story.append(Paragraph("5.1 Creating a Goal", self.styles['SubSectionHeader']))
        steps = [
            "Navigate to the 'Goals' tab",
            "Click '+ New Goal'",
            "Enter a description (e.g., 'Walk 30 minutes daily')",
            "Select a domain (Physical Health, Mental Health, etc.)",
            "Add steps to break down the goal",
            "Set a target date",
            "Click 'Create Goal'"
        ]
        
        for step in steps:
            self.story.append(Paragraph(step, self.styles['BulletPoint']))
        
        self.story.append(Spacer(1, 0.2*inch))
        
        self.story.append(Paragraph("5.2 Goal Status Types", self.styles['SubSectionHeader']))
        statuses = [
            ("<b>Planned</b>", "Goal created but not started"),
            ("<b>In Progress</b>", "Actively working on the goal"),
            ("<b>Achieved</b>", "Successfully completed"),
            ("<b>Partially Achieved</b>", "Made progress but not complete"),
            ("<b>Abandoned</b>", "No longer pursuing")
        ]
        
        for status, desc in statuses:
            self.story.append(Paragraph(f"• {status}: {desc}", self.styles['CustomBody']))
        
        self.story.append(PageBreak())
    
    def add_outcome_tracking(self):
        """Add outcome tracking section"""
        self.story.append(Paragraph("6. Outcome Tracking", self.styles['SectionHeader']))
        
        self.story.append(Paragraph("6.1 Recording an Outcome", self.styles['SubSectionHeader']))
        steps = [
            "Navigate to the 'Outcomes' tab",
            "Click '+ Record Outcome'",
            "Enter the metric name (e.g., 'Blood Pressure')",
            "Select the domain",
            "Enter the current value",
            "Optionally enter a target value",
            "Click 'Record Outcome'"
        ]
        
        for step in steps:
            self.story.append(Paragraph(step, self.styles['BulletPoint']))
        
        self.story.append(Spacer(1, 0.2*inch))
        
        self.story.append(Paragraph("6.2 Understanding Outcomes", self.styles['SubSectionHeader']))
        self.story.append(Paragraph(
            "Outcomes show your progress toward health targets. The system automatically "
            "tracks whether you've achieved your target value.",
            self.styles['CustomBody']
        ))
        
        self.story.append(PageBreak())
    
    def add_ai_insights(self):
        """Add AI insights section"""
        self.story.append(Paragraph("7. AI Insights", self.styles['SectionHeader']))
        
        self.story.append(Paragraph("7.1 What AI Insights Provide", self.styles['SubSectionHeader']))
        insights = [
            ("Risk Assessment", "Predicts your health risk level based on data"),
            ("PAM Prediction", "Forecasts future activation scores"),
            ("Recommendations", "Suggests actions to improve health"),
            ("Domain Scores", "Shows performance in different health areas")
        ]
        
        for title, desc in insights:
            self.story.append(Paragraph(f"<b>{title}</b>: {desc}", self.styles['CustomBody']))
        
        self.story.append(Spacer(1, 0.2*inch))
        
        self.story.append(Paragraph("7.2 Generating Insights", self.styles['SubSectionHeader']))
        steps = [
            "Navigate to the 'Insights' tab",
            "Click 'Refresh' to generate new insights",
            "Review the risk assessment and recommendations",
            "Use the insights to inform health decisions"
        ]
        
        for step in steps:
            self.story.append(Paragraph(step, self.styles['BulletPoint']))
        
        self.story.append(PageBreak())
    
    def add_clinical_notes(self):
        """Add clinical notes section"""
        self.story.append(Paragraph("8. Clinical Notes", self.styles['SectionHeader']))
        
        self.story.append(Paragraph("8.1 Adding a Clinical Note", self.styles['SubSectionHeader']))
        steps = [
            "Navigate to the 'Notes' tab",
            "Click '+ Add Note'",
            "Enter the clinical note text",
            "Enter the author name",
            "Click 'Save Note'"
        ]
        
        for step in steps:
            self.story.append(Paragraph(step, self.styles['BulletPoint']))
        
        self.story.append(Spacer(1, 0.2*inch))
        
        self.story.append(Paragraph("8.2 Sentiment Analysis", self.styles['SubSectionHeader']))
        self.story.append(Paragraph(
            "The system automatically analyzes the sentiment of clinical notes:",
            self.styles['CustomBody']
        ))
        
        sentiments = [
            ("😊 Positive", "Indicates improvement or positive outlook"),
            ("😐 Neutral", "Objective clinical observation"),
            ("😔 Negative", "Indicates concerns or decline")
        ]
        
        for sentiment, desc in sentiments:
            self.story.append(Paragraph(f"• {sentiment}: {desc}", self.styles['CustomBody']))
        
        self.story.append(PageBreak())
    
    def add_settings(self):
        """Add settings section"""
        self.story.append(Paragraph("9. Settings & Configuration", self.styles['SectionHeader']))
        
        self.story.append(Paragraph("9.1 Changing Patients", self.styles['SubSectionHeader']))
        steps = [
            "Go to the 'Settings' tab",
            "Select a patient from the dropdown",
            "The dashboard will update with their data"
        ]
        
        for step in steps:
            self.story.append(Paragraph(step, self.styles['BulletPoint']))
        
        self.story.append(Spacer(1, 0.2*inch))
        
        self.story.append(Paragraph("9.2 Data Management", self.styles['SubSectionHeader']))
        
        self.story.append(Paragraph(
            "<b>Export Data</b>: Downloads all data as a JSON file",
            self.styles['CustomBody']
        ))
        self.story.append(Paragraph(
            "<b>Clear Data</b>: Deletes all data for the current patient",
            self.styles['CustomBody']
        ))
        
        self.story.append(PageBreak())
    
    def add_troubleshooting(self):
        """Add troubleshooting section"""
        self.story.append(Paragraph("10. Troubleshooting", self.styles['SectionHeader']))
        
        issues = [
            ("Dashboard not loading", "Check internet connection or refresh the page"),
            ("Data not showing", "Ensure you're logged in and have selected a patient"),
            ("API errors", "Check the Vercel logs for details"),
            ("PWA not installing", "Use HTTPS or localhost for installation")
        ]
        
        for issue, solution in issues:
            self.story.append(Paragraph(f"<b>{issue}</b>", self.styles['SubSectionHeader']))
            self.story.append(Paragraph(f"Solution: {solution}", self.styles['CustomBody']))
            self.story.append(Spacer(1, 0.1*inch))
        
        self.story.append(PageBreak())
    
    def add_api_reference(self):
        """Add API reference section"""
        self.story.append(Paragraph("11. API Reference", self.styles['SectionHeader']))
        
        apis = [
            ("GET", "/api/health", "Health check"),
            ("GET", "/api/person/{nhs}", "Get patient details"),
            ("POST", "/api/person", "Create new patient"),
            ("GET", "/api/goals/{id}", "Get patient goals"),
            ("POST", "/api/goal", "Create new goal"),
            ("GET", "/api/outcomes/{id}", "Get patient outcomes"),
            ("POST", "/api/outcome", "Record an outcome"),
            ("GET", "/api/pam/{id}", "Get PAM scores"),
            ("POST", "/api/pam", "Record PAM score"),
            ("GET", "/api/notes/{id}", "Get clinical notes"),
            ("POST", "/api/note", "Add clinical note"),
            ("GET", "/api/insights/{id}", "Get AI insights"),
            ("GET", "/api/population", "Get population statistics")
        ]
        
        # Convert to table
        table_data = [["Method", "Endpoint", "Description"]]
        for method, endpoint, desc in apis:
            table_data.append([method, endpoint, desc])
        
        table = Table(table_data, colWidths=[1*inch, 2.2*inch, 2.8*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#005EB8')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F5F7FA')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E8ECF0'))
        ]))
        
        self.story.append(table)
        self.story.append(PageBreak())
    
    def add_footer(self):
        """Add footer"""
        self.story.append(Spacer(1, 0.5*inch))
        self.story.append(Paragraph(
            "NHS England Comprehensive Model for Personalised Care",
            self.styles['Footer']
        ))
        self.story.append(Paragraph(
            f"Documentation generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            self.styles['Footer']
        ))
    
    def generate(self):
        """Generate the PDF"""
        self.add_title_page()
        self.add_table_of_contents()
        self.add_introduction()
        self.add_getting_started()
        self.add_dashboard_overview()
        self.add_patient_management()
        self.add_goal_management()
        self.add_outcome_tracking()
        self.add_ai_insights()
        self.add_clinical_notes()
        self.add_settings()
        self.add_troubleshooting()
        self.add_api_reference()
        self.add_footer()
        
        self.doc.build(self.story)
        print(f"✅ PDF generated: {self.filename}")
        print(f"📄 Location: {os.path.abspath(self.filename)}")

def main():
    # Check if reportlab is installed
    try:
        import reportlab
    except ImportError:
        print("❌ ReportLab not installed. Installing...")
        os.system("pip install reportlab")
        print("✅ ReportLab installed. Please run the script again.")
        return
    
    # Generate the PDF
    generator = UserGuideGenerator()
    generator.generate()

if __name__ == '__main__':
    main()