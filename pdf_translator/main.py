"""
PDF → 한국어 Word + PDF 번역기
사용법:
  python main.py                           # GUI 파일 선택창 (기본: DeepL)
  python main.py input.pdf                 # CLI
  python main.py input.pdf out.docx        # CLI + 출력 경로 지정
  python main.py input.pdf --engine claude # Claude API로 번역

번역 엔진 전환:
  ENGINE 변수를 "deepl" 또는 "claude" 로 변경하거나 --engine 옵션 사용
"""

import os
import sys
from pathlib import Path

ENGINE = "deepl"   # ← 여기서 기본 엔진 변경 가능: "deepl" | "claude"

VALID_ENGINES = ("deepl", "claude", "anthropic")


# ── 경로 검증 ──────────────────────────────────────────────────────────────────

def _validate_input_path(path_str: str) -> Path:
    path = Path(path_str).resolve()
    if not path.exists():
        raise FileNotFoundError(f"파일이 없습니다: {path}")
    if not path.is_file():
        raise ValueError(f"파일이 아닙니다: {path}")
    if path.suffix.lower() != ".pdf":
        raise ValueError(f"PDF 파일만 지원합니다 (현재: {path.suffix})")
    return path


def _validate_output_path(path_str: str) -> Path:
    path = Path(path_str).resolve()
    if path.suffix.lower() != ".docx":
        raise ValueError(f"출력 파일은 .docx 형식이어야 합니다 (현재: {path.suffix})")
    parent = path.parent
    if not parent.exists():
        parent.mkdir(parents=True, exist_ok=True)
    if not os.access(parent, os.W_OK):
        raise PermissionError(f"쓰기 권한이 없습니다: {parent}")
    return path


# ── CLI 인자 파싱 ──────────────────────────────────────────────────────────────

def _parse_args(args: list) -> tuple:
    engine = ENGINE

    if "--engine" in args:
        idx = args.index("--engine")
        if idx + 1 >= len(args):
            raise ValueError("--engine 다음에 엔진 이름이 필요합니다 (deepl 또는 claude)")
        engine = args[idx + 1].lower()
        if engine not in VALID_ENGINES:
            raise ValueError(f"지원하지 않는 엔진: {engine!r}. 지원: {VALID_ENGINES}")
        args = [a for i, a in enumerate(args) if i not in (idx, idx + 1)]

    pdf_path = args[0] if len(args) >= 1 else None
    out_path = args[1] if len(args) >= 2 else None
    return pdf_path, out_path, engine


# ── 파일 열기 ──────────────────────────────────────────────────────────────────

def _open_file(path: Path):
    try:
        if sys.platform == "win32":
            os.startfile(str(path))
        elif sys.platform == "darwin":
            import subprocess
            subprocess.run(["open", str(path)], check=False)
        else:
            import subprocess
            subprocess.run(["xdg-open", str(path)], check=False)
    except Exception as e:
        print(f"  (파일 자동 열기 실패 — 직접 열어주세요: {e})")


# ── PDF 변환 ──────────────────────────────────────────────────────────────────

def _convert_to_pdf(docx_path: Path) -> Path | None:
    """docx → PDF 변환. Microsoft Word 또는 LibreOffice 필요."""
    pdf_path = docx_path.with_suffix(".pdf")
    try:
        from docx2pdf import convert
        convert(str(docx_path), str(pdf_path))
        return pdf_path
    except ImportError:
        print("  [안내] docx2pdf 미설치로 PDF 변환 생략 (pip install docx2pdf)")
    except Exception as e:
        print(f"  [PDF 변환 경고] {e}")
    return None


# ── 메인 실행 ──────────────────────────────────────────────────────────────────

def run(pdf_path: str, output_path: str | None = None, engine: str = ENGINE) -> str:
    from pdf_extractor import PDFExtractor
    from translator import create_translator
    from image_processor import ImageProcessor
    from word_generator import WordGenerator

    # 경로 검증
    pdf = _validate_input_path(pdf_path)
    out = _validate_output_path(output_path) if output_path else \
          pdf.parent / (pdf.stem + "_korean.docx")

    # ── 1. PDF 분석 ────────────────────────────────────────────────────────────
    print(f"\n[1/4] PDF 분석 중: {pdf.name}")
    extractor = PDFExtractor(str(pdf))
    pages = extractor.extract()
    n_text = sum(len(p["text_blocks"]) for p in pages)
    n_img  = sum(len(p["images"])       for p in pages)
    print(f"      {len(pages)}페이지 | 텍스트 블록 {n_text}개 | 이미지 {n_img}개")

    # ── 2. 텍스트 번역 ─────────────────────────────────────────────────────────
    print(f"\n[2/4] 텍스트 번역 중 ({n_text}개 블록)… [엔진: {engine}]")
    translator = create_translator(engine)
    all_texts = [b["text"] for p in pages for b in p["text_blocks"]]
    translations = translator.translate_batch(all_texts)

    idx = 0
    for page in pages:
        for block in page["text_blocks"]:
            block["translated"] = translations[idx] if idx < len(translations) else block["text"]
            idx += 1

    # ── 3. 이미지 내 텍스트 처리 ───────────────────────────────────────────────
    print(f"\n[3/4] 이미지 OCR + 번역 중 ({n_img}개)…")
    img_proc = ImageProcessor(translator)
    for page in pages:
        processed = []
        for j, img in enumerate(page["images"]):
            print(f"      p{page['page_num']} 이미지 {j+1}/{len(page['images'])}", end="\r")
            processed.append(img_proc.process(img))
        page["processed_images"] = processed
    if n_img:
        print()

    # ── 4. Word 생성 ───────────────────────────────────────────────────────────
    print(f"\n[4/4] Word 문서 생성 중…")
    WordGenerator().create(pages, str(out))
    print(f"      Word 저장 완료 → {out.name}")

    # ── 5. PDF 변환 ────────────────────────────────────────────────────────────
    print(f"\n[5/5] PDF 변환 중…")
    pdf_out = _convert_to_pdf(out)
    if pdf_out:
        print(f"      PDF  저장 완료 → {pdf_out.name}")

    print(f"\n{'='*50}")
    print(f"완료!")
    print(f"  Word : {out}")
    if pdf_out:
        print(f"  PDF  : {pdf_out}")
    print(f"{'='*50}")

    _open_file(out)
    if pdf_out:
        _open_file(pdf_out)

    return str(out)


# ── GUI 파일 선택창 ────────────────────────────────────────────────────────────

def _pick_files_gui():
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    pdf = filedialog.askopenfilename(
        title="번역할 PDF 파일 선택",
        filetypes=[("PDF", "*.pdf"), ("모든 파일", "*.*")],
    )
    if not pdf:
        print("파일이 선택되지 않았습니다.")
        return None, None

    out = filedialog.asksaveasfilename(
        title="저장할 Word 파일 경로",
        defaultextension=".docx",
        filetypes=[("Word", "*.docx"), ("모든 파일", "*.*")],
        initialfile=Path(pdf).stem + "_korean.docx",
        initialdir=str(Path(pdf).parent),
    )
    root.destroy()
    return pdf, out or None


# ── 진입점 ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    try:
        pdf_path, out_path, engine = _parse_args(sys.argv[1:])
    except ValueError as e:
        print(f"[오류] {e}")
        sys.exit(1)

    if not pdf_path:
        pdf_path, out_path = _pick_files_gui()

    if pdf_path:
        try:
            run(pdf_path, out_path, engine=engine)
        except (FileNotFoundError, ValueError, PermissionError) as e:
            print(f"\n[오류] {e}")
            sys.exit(1)
