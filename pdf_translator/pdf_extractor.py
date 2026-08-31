import fitz  # PyMuPDF
import io
from PIL import Image


class PDFExtractor:
    def __init__(self, pdf_path: str):
        self.doc = fitz.open(pdf_path)

    def extract(self) -> list:
        pages = []
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            pages.append({
                'page_num': page_num + 1,
                'width': page.rect.width,
                'height': page.rect.height,
                'text_blocks': self._extract_text_blocks(page),
                'images': self._extract_images(page),
            })
        return pages

    def _extract_text_blocks(self, page) -> list:
        blocks = []
        text_dict = page.get_text("dict")

        for block in text_dict["blocks"]:
            if block["type"] != 0:
                continue

            block_text = ""
            font_size = 11
            is_bold = False

            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    block_text += span["text"]
                    font_size = max(font_size, span["size"])
                    if "bold" in span.get("font", "").lower():
                        is_bold = True
                block_text += "\n"

            block_text = block_text.strip()
            if block_text:
                blocks.append({
                    'text': block_text,
                    'bbox': block["bbox"],
                    'font_size': font_size,
                    'is_bold': is_bold,
                    'translated': None,
                })

        return blocks

    def _extract_images(self, page) -> list:
        images = []
        for img_info in page.get_images(full=True):
            xref = img_info[0]
            try:
                base_image = self.doc.extract_image(xref)
                img_rects = page.get_image_rects(xref)
                bbox = img_rects[0] if img_rects else None

                # Convert to RGB PNG bytes regardless of original format
                pil_img = Image.open(io.BytesIO(base_image["image"]))
                if pil_img.mode not in ("RGB", "RGBA"):
                    pil_img = pil_img.convert("RGB")
                buf = io.BytesIO()
                pil_img.save(buf, format="PNG")

                images.append({
                    'xref': xref,
                    'bytes': buf.getvalue(),
                    'bbox': bbox,
                    'processed_bytes': None,
                })
            except Exception as e:
                print(f"Warning: skipping image xref={xref}: {e}")

        return images

    def __del__(self):
        if hasattr(self, 'doc'):
            self.doc.close()
