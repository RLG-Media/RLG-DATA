import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from typing import List, Dict, Optional

class ReportGenerator:
    """
    A system for generating detailed reports in various formats including PDF, Excel, HTML, and sharing to external platforms.
    """

    def __init__(self, output_dir: str = "reports"):
        """
        Initialize the ReportGenerator.

        Args:
            output_dir: Directory to save the generated reports.
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_summary_statistics(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate summary statistics for the given data.

        Args:
            data: Input pandas DataFrame.

        Returns:
            A DataFrame with summary statistics.
        """
        return data.describe(include='all').transpose()

    def generate_charts(self, data: pd.DataFrame, chart_dir: str = "charts") -> str:
        """
        Generate visualizations for the given data.

        Args:
            data: Input pandas DataFrame.
            chart_dir: Directory to save the generated charts.

        Returns:
            Path to the directory containing generated charts.
        """
        chart_dir = os.path.join(self.output_dir, chart_dir)
        os.makedirs(chart_dir, exist_ok=True)

        # Example visualizations
        for column in data.select_dtypes(include=['number']).columns:
            plt.figure(figsize=(10, 6))
            sns.histplot(data[column], kde=True, bins=30, color='blue')
            plt.title(f"Distribution of {column}")
            plt.xlabel(column)
            plt.ylabel("Frequency")
            plt.tight_layout()
            chart_path = os.path.join(chart_dir, f"{column}_distribution.png")
            plt.savefig(chart_path)
            plt.close()

        return chart_dir

    def generate_pdf_report(self, title: str, data: pd.DataFrame, template_file: str = "report_template.html", include_footer: bool = True) -> str:
        """
        Generate a PDF report.

        Args:
            title: Title of the report.
            data: Input pandas DataFrame.
            template_file: HTML template file for the report.
            include_footer: Boolean to include a standard footer.

        Returns:
            Path to the generated PDF report.
        """
        env = Environment(loader=FileSystemLoader(searchpath="templates"))
        template = env.get_template(template_file)

        # Generate charts
        chart_dir = self.generate_charts(data)

        # Render the template
        rendered_html = template.render(
            title=title,
            summary=self.generate_summary_statistics(data).to_html(classes="table table-striped"),
            chart_dir=chart_dir,
            include_footer=include_footer
        )

        # Generate PDF
        pdf_path = os.path.join(self.output_dir, f"{title.replace(' ', '_').lower()}.pdf")
        HTML(string=rendered_html).write_pdf(pdf_path)

        return pdf_path

    def generate_excel_report(self, title: str, data: pd.DataFrame, include_summary: bool = True, include_charts: bool = True) -> str:
        """
        Generate an Excel report.

        Args:
            title: Title of the report.
            data: Input pandas DataFrame.
            include_summary: Boolean to include summary statistics.
            include_charts: Boolean to include charts.

        Returns:
            Path to the generated Excel report.
        """
        excel_path = os.path.join(self.output_dir, f"{title.replace(' ', '_').lower()}.xlsx")
        writer = pd.ExcelWriter(excel_path, engine='xlsxwriter')

        # Write data and summary statistics to Excel
        data.to_excel(writer, sheet_name="Raw Data", index=False)

        if include_summary:
            summary = self.generate_summary_statistics(data)
            summary.to_excel(writer, sheet_name="Summary Statistics")

        if include_charts:
            workbook = writer.book
            worksheet = workbook.add_worksheet("Charts")
            workbook.add_worksheet(worksheet)
            worksheet.insert_image('B2', os.path.join(self.output_dir, "charts", f"{data.columns[0]}_distribution.png"))

        writer.save()
        return excel_path

    def generate_html_report(self, title: str, data: pd.DataFrame, include_summary: bool = True) -> str:
        """
        Generate an HTML report.

        Args:
            title: Title of the report.
            data: Input pandas DataFrame.
            include_summary: Boolean to include summary statistics.

        Returns:
            Path to the generated HTML report.
        """
        html_path = os.path.join(self.output_dir, f"{title.replace(' ', '_').lower()}.html")
        with open(html_path, 'w') as f:
            if include_summary:
                f.write(data.to_html(classes="table table-striped"))
            else:
                f.write(data.to_html(classes="table"))

        return html_path

    def generate_complete_report(self, title: str, data: pd.DataFrame, include_summary: bool = True, include_charts: bool = True) -> Dict[str, str]:
        """
        Generate reports in all formats (PDF, Excel, HTML).

        Args:
            title: Title of the report.
            data: Input pandas DataFrame.
            include_summary: Boolean to include summary statistics.
            include_charts: Boolean to include charts.

        Returns:
            A dictionary containing paths to all generated reports.
        """
        return {
            "pdf": self.generate_pdf_report(title, data, include_footer=True),
            "excel": self.generate_excel_report(title, data, include_summary, include_charts),
            "html": self.generate_html_report(title, data, include_summary),
        }


# Example Usage
if __name__ == "__main__":
    # Sample DataFrame
    data = pd.DataFrame({
        "Name": ["Alice", "Bob", "Charlie"],
        "Age": [25, 30, 35],
        "Score": [85, 90, 95]
    })

    report_gen = ReportGenerator()
    reports = report_gen.generate_complete_report(title="Sample Report", data=data)

    for report_type, path in reports.items():
        print(f"{report_type.upper()} Report: {path}")
