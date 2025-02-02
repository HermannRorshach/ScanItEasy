
# Table of Contents
[[# Содержание]]

[[#Project Description]]
[[#Installation]]
[[#Running the Program]]
[[#Compiling the Program into an Executable]]
[[#Congratulations! The Program is Ready to Run]]
[[#PDF Compression]]
[[#Automatically Opening the Created PDF]]
[[#License]]
[[#Acknowledgements]]
[[#Feedback]]



## Project Description

This project provides a tool for automatic processing of DOCX documents, simulating the scanning process. The program converts the input file to PDF as if it were printed on a black-and-white printer, stapled with a ribbon, and scanned. This saves time on scanning multi-page documents.

In addition to two main scanning modes, the program also offers several additional features:

- **Convert DOCX to PDF**
- **Merge multiple PDFs into one**
- **Make a PDF black and white**
- **Compress PDF**
- **Convert PDF to PNG**

## Installation

### 1. Clone the repository

Clone the repository to your computer:

#### Windows/macOS/Linux:
```bash
git clone https://github.com/yourusername/yourproject.git
```

### 2. Set up a virtual environment with Python 3.12

The project requires Python version 3.12. Make sure you have this version installed, as it is necessary for proper operation with **pyinstaller**.

#### Windows:
```bash
py -3.12 -m venv venv
```
#### macOS/Linux:
```bash
`python3.12 -m venv venv`
```

### 3. Activate the virtual environment

#### Windows:

```python
source venv/Scripts/activate
```
#### macOS/Linux:
```bash
source venv/bin/activate
```

### ### 4. Install dependencies

Once the virtual environment is activated, install all the necessary dependencies using pip:
#### Windows/macOS/Linux:
```bash
pip install -r requirements.txt
```

## ## Running the Program

After all dependencies are installed and the virtual environment is activated, you can run the program with the following command from the console.
#### Windows:
```bash
python ScanItEasy_GUI.py
```
#### macOS/Linux:
```bash
python3 ScanItEasy_GUI.py
```

## Compiling the Program into an Executable

To compile the program into an executable file for your system, run the following command:
#### Windows
```bash
pyinstaller --onefile --noconsole \
--add-data "light.png;." \
--add-data "dark.png;." \
--add-data "doc_decorations/Красная лента. Первая страница.png;doc_decorations" \
--add-data "doc_decorations/Синяя лента. Первая страница.png;doc_decorations" \
--add-data "doc_decorations/Уголок с красной лентой.png;doc_decorations" \
--add-data "doc_decorations/Уголок с синей лентой.png;doc_decorations" \
ScanItEasy_GUI.py
```
#### macOS/Linux
```bash
pyinstaller --onefile --noconsole \
--add-data "light.png:." \
--add-data "dark.png:." \
--add-data "doc_decorations/Красная лента. Первая страница.png:doc_decorations" \
--add-data "doc_decorations/Синяя лента. Первая страница.png:doc_decorations" \
--add-data "doc_decorations/Уголок с красной лентой.png:doc_decorations" \
--add-data "doc_decorations/Уголок с синей лентой.png:doc_decorations" \
ScanItEasy_GUI.py
```
**The resulting executable file will be located in the `dist` folder**, which is in the root of the project. You can move it to any convenient location from there.

## Congratulations! The Program is Ready to Run

After completing these steps, the program is ready to run and will work, but there are a few more things you should know.

### PDF Compression

The program uses two methods for compressing PDFs:

1. **Compression with the [pdf_compressor](https://github.com/theeko74/pdfc) module**, which is based on **GhostScript**. However, this method requires **GhostScript** to be installed on your system.
2. **Compression with pikepdf**, if **GhostScript** is not installed. This method does not require any additional installation and works right out of the box. These two compression methods work differently, and you can test which one works better for your documents.

#### Installing GhostScript

If you want to use the first compression method with **pdf_compressor**, you need to:

##### 1. Install the Ghostscript dependency.
###### MacOSX:
```bash
brew install ghostscript
```
###### ###### Windows:
Download the file from the [official website](https://www.ghostscript.com/releases/gsdnld.html) or from [cloud](https://disk.yandex.ru/d/j0BH1f6yf8WsgA).

##### 2. Add to the PATH environment variable
###### MacOSX:
```bash
echo 'export PATH="/absolute/path/of/the/folder/script/:$PATH"' >> ~/.bash_profile
```
###### Windows:

1. **Press Win + R** to open the "Run" window.
2. Type `sysdm.cpl` and press **Enter**.
3. In the opened window, go to the **Advanced** tab.
4. Click the **Environment Variables** button at the bottom of the window.
5. In the **System variables** section, find the **Path** variable and select it.
6. Click **Edit**. In the opened window, you can view and edit the list of paths.
7. Add the path to the `GhostScript` executable file, for example, `C:\Program Files\gs\gs10.04.0\bin`, and click **OK** in all open windows.

**Now the program will be able to use `GhostScript` to compress PDF files. If you find that `pikepdf` performs better, remove the corresponding PATH from the environment variables and uninstall `GhostScript`.**

### Automatically Opening the Created PDF

The program automatically opens the created PDF. Depending on the operating system, it uses the appropriate application to open the file:

- **For Windows**, the program uses the `Acrobat.exe` file, which is usually located in `C:\Program Files\Adobe\Acrobat DC\Acrobat\`. If the file is not found in the specified folder, the program will show an error when trying to open the PDF automatically, but the PDF file will still be created.
- **For macOS** and **Linux**, the program uses standard system commands (`open` for macOS and `xdg-open` for Linux) that automatically open the PDF in the default application for handling such files.

If the path to **Acrobat.exe** on **Windows** differs from the one specified, you can:

1. Modify the first line of the `acrobat_path.txt` file, providing the correct path to **Acrobat.exe**. The `acrobat_path.txt` file should be located in the same folder as the compiled `ScanItEasy_GUI.exe` file.
2. If you don’t want to modify the contents of the `acrobat_path.txt` file and place it in the same folder with the compiled program file, you can change the path to **Acrobat.exe** directly in the code before compiling. The path is stored in the `acrobat_path` variable in the `work_process` function in the `ScanItEasy_backend.py` module. The second line of the `acrobat_path.txt` file specifies the page number the program will automatically open the PDF from.

## License

This project is licensed under the **BSD 3-Clause License**. Please refer to the full terms in the  [LICENSE](https://github.com/HermannRorshach/ScanItEasy/blob/gui/LICENSE)

## Acknowledgements

The project was inspired by various document processing tools, as well as valuable contributions and feedback from users. Thanks to everyone who supports and helps develop open-source software.

Special thanks to the community for providing useful libraries and resources, such as pymupdf, customtkinter, PyInstaller, pikepdf, and others.

## Feedback

If you have any questions, suggestions, or encounter any issues while using the program, feel free to reach out to me.
You can contact me via Telegram: [@realpavelb](https://t.me/realpavelb)

# Содержание

[[#Table of Contents]]

[[#Описание проекта]]
[[#Установка]]
[[#Запуск программы]]
[[#Компиляция программы в исполняемый файл]]
[[#Поздравляю! Программа готова к запуску]]
[[#Сжатие PDF]]
[[#Открытие созданного pdf в автоматическом режиме]]
[[#Лицензия]]
[[#Благодарности]]
[[#Обратная связь]]


## Описание проекта

Этот проект предоставляет инструмент для автоматической обработки документов в формате DOCX, имитируя процесс сканирования. Программа преобразует исходный файл в PDF, как если бы он был распечатан на чёрно-белом принтере, сшит лентой и отсканирован. Это позволяет сэкономить время на сканировании многостраничных документов.

Помимо двух основных режимов, имитирующих сканирование, программа также предлагает несколько дополнительных функций:
- **Конвертация DOCX в PDF**
- **Объединение нескольких PDF в один**
- **Сделать PDF чёрно-белым**
- **Сжатие PDF**
- **Конвертация PDF в PNG**

## Установка

### 1. Клонирование проекта

Клонируйте репозиторий на ваш компьютер:

#### Windows/macOS/Linux:
```bash
git clone https://github.com/yourusername/yourproject.git
```

### 2. Установка виртуального окружения с Python 3.12

Для работы проекта требуется версия Python 3.12. Убедитесь, что у вас установлена эта версия, так как она необходима для корректной работы с **pyinstaller**.

#### Windows:
```bash
py -3.12 -m venv venv
```
#### macOS/Linux:
```bash
`python3.12 -m venv venv`
```

### 3. Активировать виртуальное окружение

#### Windows:

```python
source venv/Scripts/activate
```
#### macOS/Linux:
```bash
source venv/bin/activate
```

### 4. Установка зависимостей

После активации виртуального окружения установите все необходимые зависимости с помощью pip:
#### Windows/macOS/Linux:
```bash
pip install -r requirements.txt
```

## Запуск программы

После того как все зависимости установлены и виртуальное окружение активировано, вы можете запустить программу командой прямо из консоли.
#### Windows:
```bash
python ScanItEasy_GUI.py
```
#### macOS/Linux:
```bash
python3 ScanItEasy_GUI.py
```

## Компиляция программы в исполняемый файл

Для того, чтобы скомпилировать программу в исполняемый файл для вашего компьютера, выполните следующую команду:
#### Windows
```bash
pyinstaller --onefile --noconsole \
--add-data "light.png;." \
--add-data "dark.png;." \
--add-data "doc_decorations/Красная лента. Первая страница.png;doc_decorations" \
--add-data "doc_decorations/Синяя лента. Первая страница.png;doc_decorations" \
--add-data "doc_decorations/Уголок с красной лентой.png;doc_decorations" \
--add-data "doc_decorations/Уголок с синей лентой.png;doc_decorations" \
ScanItEasy_GUI.py
```
#### macOS/Linux
```bash
pyinstaller --onefile --noconsole \
--add-data "light.png:." \
--add-data "dark.png:." \
--add-data "doc_decorations/Красная лента. Первая страница.png:doc_decorations" \
--add-data "doc_decorations/Синяя лента. Первая страница.png:doc_decorations" \
--add-data "doc_decorations/Уголок с красной лентой.png:doc_decorations" \
--add-data "doc_decorations/Уголок с синей лентой.png:doc_decorations" \
ScanItEasy_GUI.py
```
**Готовый исполняемый файл будет находиться в папке `dist`**, расположенной в корне проекта. Оттуда вы можете переместить его в любое удобное место.

## Поздравляю! Программа готова к запуску

После проделанных шагов программа готова к запуску и будет работать, однако есть ещё несколько вещей, о которых вам полезно знать.

### Сжатие PDF

Программа использует два варианта сжатия PDF:
1. **Сжатие с помощью модуля [pdf_compressor](https://github.com/theeko74/pdfc)**, который работает на основе **GhostScript**. Однако для этого способа необходимо установить **GhostScript** в вашу систему.
2. **Сжатие с помощью pikepdf**, если **GhostScript** не установлен. Этот метод не требует дополнительной установки в систему и работает прямо из коробки.
Эти два способа сжатия PDF работают по-разному, и вы можете протестировать, какой вариант работает лучше для ваших документов.

#### Установка GhostScript

Если вы хотите использовать первый способ сжатия с **pdf_compressor**, вам нужно:
##### 1. Установите зависимость Ghostscript.
###### MacOSX:
```bash
brew install ghostscript
```
###### Windows:
Скачайте файл с [официального сайта](https://www.ghostscript.com/releases/gsdnld.html) или с [облака](https://disk.yandex.ru/d/j0BH1f6yf8WsgA).

##### 2. Добавьте в переменную среды PATH
###### MacOSX:
```bash
echo 'export PATH="/absolute/path/of/the/folder/script/:$PATH"' >> ~/.bash_profile
```
###### Windows:
1. **Нажмите Win + R** для открытия окна "Выполнить".
2. Введите `sysdm.cpl` и нажмите **Enter**.
3. В открывшемся окне выберите вкладку **Дополнительно**.
4. Нажмите на кнопку **Переменные среды** внизу окна.
5. В разделе **Системные переменные** найдите переменную **Path** и выберите её.
6. Нажмите **Изменить**. В открывшемся окне вы сможете просматривать и редактировать список путей.
7. Добавьте путь к исполняемому файлу `GhostScript`, например `C:\Program Files\gs\gs10.04.0\bin`, нажмите `Ок` во всех открытых окнах.

**Теперь программа сможет использовать `GhostScript` для сжатия pdf-файлов. Если вы сочтёте, что `pikepdf` справляется лучше, удалите соответствующий PATH из переменных среды, а также сам `GhostScript'**

### Открытие созданного pdf в автоматическом режиме

Программа автоматически открывает созданный PDF. В зависимости от операционной системы она использует соответствующее приложение для открытия файлов:

- **Для Windows** программа использует файл `Acrobat.exe`, который обычно находится в папке `C:\Program Files\Adobe\Acrobat DC\Acrobat\`. Если файл не найден в указанной папке, программа выдаст ошибку при автоматическом открытии, но сам PDF-файл будет создан.
- **Для macOS** и **Linux** программа использует стандартные системные команды (`open` для macOS и `xdg-open` для Linux), которые автоматически открывают PDF в приложении, установленном по умолчанию для обработки таких файлов.

Если путь к **Acrobat.exe** на **Windows** отличается от указанного, вы можете:
1. Изменить первую строку файла `acrobat_path.txt`, указав правильный путь к **Acrobat.exe**. Файл `acrobat_path.txt` должен находиться в одной папке с скомпилированным файлом `ScanItEasy_GUI.exe`.
2. Если вы не хотите изменять содержимое файла `acrobat_path.txt` и размещать его одной папке со скомпилированным файлом программы, вы можете изменить путь к **Acrobat.exe** прямо в коде программы перед компиляцией. Путь хранится в переменной `acrobat_path` функции `work_process` в модуле `ScanItEasy_backend.py`.
Вторая строка файла `acrobat_path.txt` указывает номер страницы, с которой программа будет автоматически открывать PDF.

## Лицензия

Этот проект лицензируется под лицензией **BSD 3-Clause License**. Пожалуйста, ознакомьтесь с полными условиями в файле [LICENSE](https://github.com/HermannRorshach/ScanItEasy/blob/gui/LICENSE)

## Благодарности

Проект был вдохновлён различными инструментами для обработки документов, а также ценным вкладом и отзывами пользователей. Благодарим всех, кто поддерживает и помогает развивать открытое программное обеспечение.

Особая благодарность сообществу за предоставление полезных библиотек и ресурсов, таких как pymupdf, customtkinter, PyInstaller, pikepdf, и другие.

## Обратная связь

Если у вас есть вопросы, предложения или вы столкнулись с проблемами при использовании программы, не стесняйтесь связаться со мной.

Вы можете обратиться через Telegram: [@realpavelb](https://t.me/realpavelb)
