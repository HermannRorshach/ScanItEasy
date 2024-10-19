# ScanItEasy

**ScanItEasy** is a web application designed to streamline the routine scanning of multi-page documents, making the process easy and fast. This tool allows users to upload DOCX files, convert them into PDF format, add visual elements like stitches and signatures, and generate a "scanned" version of the document.

## Features

- Upload multi-page DOCX files for processing.
- Convert DOCX files directly into high-quality PDF documents.
- Automatically add decorative elements, such as stitches or ribbons, to the PDF.
- Choose from a selection of signature images to add to the document.
- Generate a final PDF that resembles a professionally printed and signed document.

## Technologies Used

- Django: A high-level Python web framework for building web applications.
- PyMuPDF: A library for working with PDF files, allowing for document rendering and image manipulation.
- Other relevant libraries for handling file uploads and processing.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/HermannRorschach/ScanItEasy.git
   ```
2. Navigate to the project directory:
   ```bash
   cd ScanItEasy
   ```
3. Install the required dependencies:
 ```bash
pip install -r requirements.txt
```
4. Run the Django development server:
 ```bash
 python manage.py runserver
 ```

Access the application in your web browser at http://127.0.0.1:8000/.

## Usage
Upload a DOCX file using the provided form.
Select a signature image from the dropdown menu.
Click the "Submit" button to process the document.
Download the generated scanned PDF document.


## Contributing
Contributions are welcome! If you'd like to contribute to ScanItEasy, please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them.
4. Push to your fork and submit a pull request.

## License
This project is licensed under the BSD 3-Clause License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments
Inspiration from various document processing tools and user feedback.
Thanks to the open-source community for providing valuable libraries and resources.
For any questions or support, please contact https://t.me/realpavelb

