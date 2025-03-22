import io
import logging
from typing import Dict, Optional, Any
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

# Configure logging (if not already configured by your application)
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def generate_pdf_report(project_name: str, summary_data: Dict[str, int]) -> Optional[io.BytesIO]:
    """
    Generates a PDF report for the given project.
    
    This function creates a PDF containing a title, a subtitle, and a bar chart 
    that visualizes the summary data (e.g., mentions by platform).

    Args:
        project_name (str): The name of the project.
        summary_data (Dict[str, int]): A dictionary containing platform names as keys and 
                                       mention counts as values.

    Returns:
        Optional[io.BytesIO]: A BytesIO object containing the generated PDF, or None if an error occurs.
    
    Additional Recommendations:
        - Customize fonts, colors, and chart styles as needed.
        - Extend the report layout to include additional sections or graphs.
        - Integrate logging and error reporting for production monitoring.
    """
    try:
        # Create a byte stream to store the PDF output.
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)
        pdf.setTitle(f"{project_name} - Report")

        # Add title to the PDF.
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(100, 750, f"{project_name} - Social Media Report")

        # Add a subtitle.
        pdf.setFont("Helvetica", 12)
        pdf.drawString(100, 730, "Summary of mentions by platform:")

        # Generate a bar chart using Matplotlib.
        platforms = list(summary_data.keys())
        mentions = list(summary_data.values())
        plt.figure(figsize=(4, 3))
        plt.bar(platforms, mentions, color='blue')
        plt.title('Mentions by Platform')
        plt.xlabel('Platforms')
        plt.ylabel('Mentions')
        plt.tight_layout()

        # Save the chart to a bytes object.
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png')
        plt.close()  # Close the figure to free up memory
        img_buffer.seek(0)

        # Embed the chart into the PDF.
        image_reader = ImageReader(img_buffer)
        pdf.drawImage(image_reader, 100, 500, width=300, height=200)

        # Finalize the PDF.
        pdf.showPage()
        pdf.save()

        # Rewind the buffer to the beginning before returning.
        buffer.seek(0)
        logger.info("PDF report generated successfully for project: %s", project_name)
        return buffer

    except Exception as e:
        logger.error(f"Error generating PDF report: {e}")
        return None

# -------------------------------
# Example Usage (for testing purposes)
# -------------------------------
if __name__ == "__main__":
    # Example project name and summary data.
    project = "RLG Data"
    summary = {
        "Facebook": 120,
        "Twitter": 95,
        "Instagram": 150,
        "LinkedIn": 60,
        "YouTube": 80
    }

    pdf_buffer = generate_pdf_report(project, summary)
    if pdf_buffer:
        # Optionally, write the PDF to a file for testing purposes.
        with open("report.pdf", "wb") as f:
            f.write(pdf_buffer.getbuffer())
        print("PDF report generated and saved as 'report.pdf'.")
    else:
        print("Failed to generate PDF report.")
