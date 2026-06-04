import markdown
from fpdf import FPDF

def create_resume_pdf(username: str, md_content: str) -> bytes:
    """
    Converts markdown content into a PDF document using fpdf2.
    """
    html = markdown.markdown(md_content)
    
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Helvetica", style="B", size=18)
    pdf.cell(0, 10, f"GitHub Portfolio Review: {username}", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    # Write HTML content
    pdf.set_font("Helvetica", size=12)
    pdf.write_html(html)
    
    return pdf.output()
