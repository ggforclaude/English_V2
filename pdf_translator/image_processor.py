"""
이미지 내 영어 텍스트를 OCR로 감지한 뒤 한국어로 교체합니다.
- OCR      : pytesseract (Tesseract 4+)
- 원본 제거 : OpenCV TELEA inpainting
- 한국어 렌더링 : Pillow + 맑은 고딕(윈도우) 또는 나눔고딕(리눅스)
"""

import io
import os
from typing import List, Tuple

import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageDraw, ImageFont

_TESS_PATHS = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
]
for _p in _TESS_PATHS:
    if os.path.exists(_p):
        pytesseract.pytesseract.tesseract_cmd = _p
        break

_KO_FONTS = [
    r"C:\Windows\Fonts\malgun.ttf",
    r"C:\Windows\Fonts\malgunbd.ttf",
    r"C:\Windows\Fonts\gulim.ttc",
    "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
    "/Library/Fonts/AppleGothic.ttf",
]


def _get_font(size: int) -> ImageFont.FreeTypeFont:
    for path in _KO_FONTS:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, max(8, size))
            except Exception:
                continue
    return ImageFont.load_default()


class ImageProcessor:
    MIN_CONF = 55
    INPAINT_R = 4
    MAX_PIXELS = 25_000_000   # 약 5000x5000 이상 이미지는 건너뜀

    def __init__(self, translator):
        self.translator = translator

    def process(self, img_data: dict) -> dict:
        try:
            pil_img = Image.open(io.BytesIO(img_data["bytes"])).convert("RGB")

            # 과도하게 큰 이미지 건너뜀 (메모리 보호)
            if pil_img.width * pil_img.height > self.MAX_PIXELS:
                print(f"  [이미지 건너뜀] 너무 큰 이미지: {pil_img.size}")
                return img_data

            regions, texts = self._ocr(pil_img)
            if not texts:
                return img_data

            translations = self.translator.translate_batch(texts)
            pil_out = self._replace_text(pil_img, regions, translations)

            buf = io.BytesIO()
            pil_out.save(buf, format="PNG")
            result = dict(img_data)
            result["processed_bytes"] = buf.getvalue()
            return result

        except Exception as e:
            print(f"  [이미지 처리 경고] {e}")
            return img_data

    def _ocr(self, pil_img: Image.Image) -> Tuple[List[dict], List[str]]:
        try:
            data = pytesseract.image_to_data(
                pil_img,
                lang="eng",
                config="--psm 11 --oem 3",
                output_type=pytesseract.Output.DICT,
            )
        except pytesseract.TesseractNotFoundError:
            print("  [경고] Tesseract를 찾을 수 없습니다. 이미지 번역이 생략됩니다.")
            return [], []
        except Exception as e:
            print(f"  [OCR 오류] {e}")
            return [], []

        lines: dict = {}
        for i in range(len(data["level"])):
            conf = int(data["conf"][i])
            word = data["text"][i].strip()
            if conf < self.MIN_CONF or not word:
                continue

            key = (data["block_num"][i], data["par_num"][i], data["line_num"][i])
            x, y, w, h = data["left"][i], data["top"][i], data["width"][i], data["height"][i]

            if key not in lines:
                lines[key] = {"words": [], "x0": x, "y0": y, "x1": x + w, "y1": y + h}
            else:
                lines[key]["x0"] = min(lines[key]["x0"], x)
                lines[key]["y0"] = min(lines[key]["y0"], y)
                lines[key]["x1"] = max(lines[key]["x1"], x + w)
                lines[key]["y1"] = max(lines[key]["y1"], y + h)
            lines[key]["words"].append(word)

        regions, texts = [], []
        for v in lines.values():
            text = " ".join(v["words"])
            regions.append({"bbox": (v["x0"], v["y0"], v["x1"], v["y1"]), "text": text})
            texts.append(text)

        return regions, texts

    def _replace_text(
        self,
        pil_img: Image.Image,
        regions: List[dict],
        translations: List[str],
    ) -> Image.Image:
        cv_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        h_img, w_img = cv_img.shape[:2]

        # Step 1: inpainting으로 원본 텍스트 제거
        mask = np.zeros((h_img, w_img), dtype=np.uint8)
        for region in regions:
            x0, y0, x1, y1 = region["bbox"]
            pad = 4
            mask[max(0, y0-pad):min(h_img, y1+pad), max(0, x0-pad):min(w_img, x1+pad)] = 255

        cv_img = cv2.inpaint(cv_img, mask, self.INPAINT_R, cv2.INPAINT_TELEA)

        # Step 2: 한국어 텍스트 렌더링
        pil_out = Image.fromarray(cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_out)

        for region, ko_text in zip(regions, translations):
            if not ko_text:
                continue

            x0, y0, x1, y1 = region["bbox"]
            box_w = x1 - x0
            box_h = y1 - y0

            font_size = max(8, int(box_h * 0.85))
            font = _get_font(font_size)

            while font_size > 6:
                font = _get_font(font_size)
                tw = draw.textlength(ko_text, font=font)
                if tw <= box_w * 1.3:
                    break
                font_size -= 1

            region_arr = np.array(pil_out)[y0:y1, x0:x1]
            color = (0, 0, 0) if (region_arr.mean() > 128 if region_arr.size else True) else (255, 255, 255)
            draw.text((x0, y0), ko_text, font=font, fill=color)

        return pil_out
