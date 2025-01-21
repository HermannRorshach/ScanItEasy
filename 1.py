
import pymupdf

def merge_pdf(files, output_path, remove=False):
        """Объединение нескольких PDF файлов."""
        pdf_writer = pymupdf.open()
        for pdf in files:
            pdf_document = pymupdf.open(pdf)
            pdf_writer.insert_pdf(pdf_document)
            pdf_document.close()
        pdf_writer.save(output_path)
        pdf_writer.close()

merge_pdf(
      ["Мед карта ребенка Иран.pdf", "Scan7479.pdf", "Scan7478.pdf"], "output.pdf"
)
