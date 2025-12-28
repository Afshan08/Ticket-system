try:
    import weasyprint
    print("weasyprint: INSTALLED")
except ImportError:
    print("weasyprint: NOT INSTALLED")

try:
    import xhtml2pdf
    print("xhtml2pdf: INSTALLED")
except ImportError:
    print("xhtml2pdf: NOT INSTALLED")

try:
    import reportlab
    print("reportlab: INSTALLED")
except ImportError:
    print("reportlab: NOT INSTALLED")
