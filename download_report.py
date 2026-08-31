import sys
import os
import re
from urllib.parse import urlparse, parse_qs, unquote
import urllib.request

SAVE_DIR = os.path.dirname(os.path.abspath(__file__))

def extract_pdf_url(input_url):
    """네이버 증권 래퍼 URL에서 실제 PDF URL 추출"""
    parsed = urlparse(input_url)
    if "m.stock.naver.com" in parsed.netloc and "/pdf" in parsed.path:
        qs = parse_qs(parsed.query)
        if "url" in qs:
            return unquote(qs["url"][0])
    return input_url

def make_filename(pdf_url):
    """URL에서 파일명 생성"""
    name = os.path.basename(urlparse(pdf_url).path)
    if not name.endswith(".pdf"):
        name += ".pdf"
    return name

def download(input_url):
    pdf_url = extract_pdf_url(input_url)
    filename = make_filename(pdf_url)
    save_path = os.path.join(SAVE_DIR, filename)

    print(f"다운로드 중: {pdf_url}")
    req = urllib.request.Request(
        pdf_url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    )
    with urllib.request.urlopen(req) as resp, open(save_path, "wb") as f:
        f.write(resp.read())

    size_kb = os.path.getsize(save_path) // 1024
    print(f"완료: {save_path} ({size_kb:,} KB)")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        url = input("URL을 붙여넣으세요: ").strip()
    else:
        url = sys.argv[1].strip()

    download(url)
