import pymupdf

def merge_pdf(files, pages, output_path, remove=False):
    """Объединение нескольких PDF файлов с выбором страниц для каждого файла."""

    # Создаем новый PDF для записи
    pdf_writer = pymupdf.open()

    for i, pdf_file in enumerate(files):
        pdf_document = pymupdf.open(pdf_file)

        # Получаем страницы для текущего файла
        for page_num in pages[i]:
            # Загружаем страницу (нумерация с 0)
            page = pdf_document.load_page(page_num - 1)
            # Добавляем страницу в новый документ
            pdf_writer.insert_pdf(pdf_document, from_page=page_num - 1, to_page=page_num - 1)

        pdf_document.close()

    # Сохраняем результат в output_path
    pdf_writer.save(output_path)
    pdf_writer.close()

# Пример использования
merge_pdf(
    ["Мед карта ребенка Иран.pdf", "Scan7479.pdf", "Scan7478.pdf"],
    [[1], [2], [1]],  # Страницы для каждого файла (для первого файла 1-я страница, для второго 2-я, для третьего 1-я)
    "output.pdf"
)
