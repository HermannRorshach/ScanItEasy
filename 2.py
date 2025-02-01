import pymupdf

class Converter:
    def __init__(self, docx_file=None, pdf_file=None):
        self.docx_file = docx_file
        self.pdf_file = pdf_file
        # self.image_file = image_file
        self.temp_images = []  # Для хранения путей к временным изображениям
        self.images_to_delete = []


    def add_image_to_pdf(
        self, output_path, first_page_image,
        other_pages_image, color="red", translator_sign=None):
        """Добавление изображений на страницы PDF."""
        doc = pymupdf.open(self.pdf_file)

        # Вставляем изображение на первую страницу
        first_img = pymupdf.open(first_page_image)
        first_page = doc.load_page(0)

        # Получаем реальные размеры изображения
        first_img_width = 83.3
        first_img_height = 44.88

        if color == "blue":
            first_img_width = first_img[0].rect.width
            first_img_height = first_img[0].rect.height
        # print('first_img_width =', first_img_width, 'first_img_height =', first_img_height)

        # Вставляем изображение в левый верхний угол первой страницы с его реальными размерами
        first_page.insert_image(pymupdf.Rect(0, 0, first_img_width, first_img_height), filename=first_page_image)

        # Вставляем изображение на последующие страницы
        for page_num in range(1, doc.page_count):
            page = doc.load_page(page_num)
            other_img = pymupdf.open(other_pages_image)

            # other_img_width = other_img[0].rect.width
            # other_img_height = other_img[0].rect.height
            other_img_width = 91.5
            other_img_height = 136.8

            if color == "blue":
                other_img_width = 110
                other_img_height = 110

            # Вставляем изображение в левый верхний угол с его реальными размерами
            page.insert_image(pymupdf.Rect(0, 0, other_img_width, other_img_height), filename=other_pages_image)

        # print('other_img_width =', other_img_width, 'other_img_height =', other_img_height)
        # Вставляем изображения на последнюю страницу
        if translator_sign:
            translator_sign_page = doc.load_page(doc.page_count - 1)
            translator_sign_img = pymupdf.open(translator_sign)

            translator_sign_img_width = translator_sign_img[0].rect.width
            translator_sign_img_height = translator_sign_img[0].rect.height
            translator_sign_img_width = 645
            translator_sign_img_height = 120

            # print('translator_sign_img_width =', translator_sign_img_width, 'translator_sign_img_height =', translator_sign_img_height)
            # print('translator_sign_page.rect.width =', translator_sign_page.rect.width, 'translator_sign_page.rect.height =', translator_sign_page.rect.height)

            # Вставляем изображение для последующих страниц в левый верхний угол
            translator_sign_page.insert_image(pymupdf.Rect(0, translator_sign_page.rect.height - translator_sign_img_height, translator_sign_img_width, translator_sign_page.rect.height), filename=translator_sign)

        doc.save(output_path, incremental=True, encryption=0)  # Сохраняем изменения
        doc.close()


converter = Converter(pdf_file="Кимия Захедиан Временный сертификат.pdf")
converter.add_image_to_pdf("Кимия Захедиан Временный сертификат.pdf", "doc_decorations/Красная лента. Первая страница.png",
                           "doc_decorations/Уголок с красной лентой.png")


# converter.add_image_to_pdf("output_path.pdf", "doc_decorations/Красная лента. Первая страница.png",
#                            "doc_decorations/Уголок с красной лентой.png")
