import os
import datetime
from fpdf import FPDF
from jinja2 import Environment, FileSystemLoader

# Configuration
WHITEPAPER_TITLE = "RLG Data & RLG Fans: The Future of AI-Driven Insights"
WHITEPAPER_AUTHOR = "RLG Data Team"
WHITEPAPER_VERSION = "1.0"
OUTPUT_DIR = "generated_whitepapers"
TEMPLATE_DIR = "templates"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

class WhitepaperGenerator:
    def __init__(self, title, author, version):
        self.title = title
        self.author = author
        self.version = version
        self.date = datetime.datetime.now().strftime("%B %d, %Y")
        self.env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    
    def generate_content(self):
        """Generates the whitepaper content dynamically."""
        template = self.env.get_template("whitepaper_template.html")
        return template.render(
            title=self.title,
            author=self.author,
            version=self.version,
            date=self.date,
            competitive_analysis=self.get_competitive_analysis(),
            compliance_section=self.get_compliance_section(),
            scraping_tools=self.get_scraping_and_ai_section(),
            super_tool_info=self.get_rlg_super_tool_section()
        )
    
    def get_competitive_analysis(self):
        """Returns a structured competitive analysis comparing RLG Data & RLG Fans with competitors."""
        return """
        RLG Data & RLG Fans surpass competitors such as Brandwatch, Brand24, Mention, and Sprout Social 
        by offering AI-powered automation, region-specific pricing, real-time data insights, and deep 
        compliance monitoring. Our competitive advantage lies in scalability, accuracy, and affordability.
        """

    def get_compliance_section(self):
        """Returns information about RLG Data’s compliance and security measures."""
        return """
        RLG Data ensures full compliance with global regulations, including GDPR, CCPA, and AI ethics 
        frameworks. Our automated compliance tools protect user data while enabling scalable insights 
        without violating privacy laws.
        """

    def get_scraping_and_ai_section(self):
        """Returns details about RLG Data’s AI scraping and analytics tools."""
        return """
        Our AI-powered web scraping tool automates data collection from millions of sources, providing 
        users with real-time insights, keyword monitoring, sentiment analysis, and market trends. 
        Our ethical scraping ensures compliance and accuracy.
        """

    def get_rlg_super_tool_section(self):
        """Returns an overview of the RLG Super Tool and its value to users."""
        return """
        The RLG Super Tool is a comprehensive solution integrating social listening, SEO tracking, 
        competitive analysis, automated content marketing, and advanced reporting. It centralizes 
        data into a single dashboard for maximum efficiency.
        """

    def save_as_pdf(self, content):
        """Generates a PDF from the given content."""
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        
        # Title
        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 10, self.title, ln=True, align="C")
        pdf.ln(10)
        
        # Author & Date
        pdf.set_font("Arial", "", 12)
        pdf.cell(200, 10, f"Author: {self.author}", ln=True, align="C")
        pdf.cell(200, 10, f"Version: {self.version}", ln=True, align="C")
        pdf.cell(200, 10, f"Date: {self.date}", ln=True, align="C")
        pdf.ln(20)
        
        # Content
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 10, content)
        
        file_path = os.path.join(OUTPUT_DIR, f"RLG_Whitepaper_{self.version}.pdf")
        pdf.output(file_path)
        print(f"Whitepaper successfully saved as {file_path}")

    def generate_whitepaper(self):
        """Generates and saves the whitepaper as a PDF."""
        content = self.generate_content()
        self.save_as_pdf(content)

if __name__ == "__main__":
    generator = WhitepaperGenerator(WHITEPAPER_TITLE, WHITEPAPER_AUTHOR, WHITEPAPER_VERSION)
    generator.generate_whitepaper()
