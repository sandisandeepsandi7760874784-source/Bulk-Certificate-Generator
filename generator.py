import os
from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor

# Create a directory to store generated certificates if it doesn't exist
CERTIFICATE_DIR = "certificates"
if not os.path.exists(CERTIFICATE_DIR):
    os.makedirs(CERTIFICATE_DIR)

def generate_certificate(name: str, course_title: str, output_path: str):
    """
    Generates a simple, elegant PDF certificate using ReportLab.
    """
    # Create the PDF canvas in Landscape mode
    c = canvas.Canvas(output_path, pagesize=landscape(letter))
    width, height = landscape(letter)

    # 1. Draw an outer border
    c.setStrokeColor(HexColor("#4F81BD")) # A nice blue color
    c.setLineWidth(10)
    c.rect(0.5 * inch, 0.5 * inch, width - 1 * inch, height - 1 * inch)

    # 2. Add the Main Title
    c.setFont("Helvetica-Bold", 36)
    c.setFillColor(HexColor("#000000"))
    c.drawCentredString(width / 2.0, height - 2.5 * inch, "Certificate of Completion")

    # 3. Add a subtitle
    c.setFont("Helvetica", 18)
    c.drawCentredString(width / 2.0, height - 3.5 * inch, "This is proudly presented to")

    # 4. Add the Recipient's Name (highlighted in red)
    c.setFont("Helvetica-Bold", 28)
    c.setFillColor(HexColor("#C0504D"))
    c.drawCentredString(width / 2.0, height - 4.5 * inch, name)

    # 5. Add the Course/Event Title
    c.setFillColor(HexColor("#000000"))
    c.setFont("Helvetica", 18)
    c.drawCentredString(width / 2.0, height - 5.5 * inch, f"For successfully completing: {course_title}")

    # 6. Add a fake Signature Line
    c.setLineWidth(1)
    c.setStrokeColor(HexColor("#000000"))
    c.line(width / 2.0 - 1.5 * inch, 2 * inch, width / 2.0 + 1.5 * inch, 2 * inch)
    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2.0, 1.7 * inch, "Authorized Signature")

    # Save the PDF document to disk
    c.save()
