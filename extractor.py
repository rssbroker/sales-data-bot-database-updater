from img2table.document import Image
from img2table.ocr import TesseractOCR
from PIL import Image as Grayscale
from PIL import ImageEnhance


def extract_price_list(img_path):
    img = Grayscale.open(img_path).convert("L")
    sharpness = ImageEnhance.Sharpness(img)
    img = sharpness.enhance(2.0)
    img.save('greyscale.png')
    g_img_path = "greyscale.png"
    img = Image(src=g_img_path)
    tesseract = TesseractOCR()
    tables = img.extract_tables(ocr=tesseract, implicit_rows=False, borderless_tables=False, min_confidence=0)
    table_work = tables[0].df
    table_work = table_work.iloc[:, 1]
    table_work = table_work.tolist()
    new_table_work = [input_string.replace(',', '').replace(
        '.', '').replace("USD", "").strip() for input_string in table_work]
    if len(new_table_work) > 10:
        new_table_work = new_table_work[-10:-1]
    return new_table_work
