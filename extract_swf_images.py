# -*- coding: utf-8 -*-
"""SWF 파일에서 이미지(JPEG, PNG) 추출"""
import os
import sys
import zlib
import struct
from pathlib import Path
from PIL import Image
import io

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

SWF_DIR = r'D:\OneDrive\photo-LG\외장하드사진\민준\한영'
OUT_DIR = r'D:\extracted_swf_images'

# SWF 이미지 태그 번호
TAG_JPEG_TABLE      = 8   # 전역 JPEG 헤더
TAG_DEFINE_BITS     = 6   # JPEG (헤더는 JPEG_TABLE 사용)
TAG_DEFINE_BITS2    = 21  # JPEG (독립 헤더 포함)
TAG_DEFINE_BITS3    = 35  # JPEG + 알파
TAG_DEFINE_BITS4    = 90  # JPEG4 + 알파
TAG_LOSSLESS        = 20  # DefineBitsLossless  (zlib, no alpha)
TAG_LOSSLESS2       = 36  # DefineBitsLossless2 (zlib, with alpha)


def read_swf_tags(data):
    """SWF 바이너리에서 모든 태그를 (tag_type, payload_bytes) 리스트로 반환"""
    # SWF 헤더
    sig = data[:3]
    if sig == b'CWS':
        body = zlib.decompress(data[8:])
        data = data[:8] + body
    elif sig == b'ZWS':
        import lzma
        body = lzma.decompress(data[12:])
        data = data[:8] + body
    elif sig != b'FWS':
        raise ValueError("SWF 시그니처 불명확")

    pos = 8  # 헤더 8바이트 건너뜀

    # RECT 구조 건너뛰기
    first_byte = data[pos]
    n_bits = (first_byte >> 3) & 0x1F
    rect_bits = 5 + 4 * n_bits
    pos += (rect_bits + 7) // 8

    pos += 4  # FrameRate(2) + FrameCount(2)

    tags = []
    while pos + 2 <= len(data):
        record_header = struct.unpack_from('<H', data, pos)[0]
        pos += 2
        tag_type = (record_header >> 6) & 0x3FF
        length   = record_header & 0x3F
        if length == 0x3F:
            if pos + 4 > len(data):
                break
            length = struct.unpack_from('<I', data, pos)[0]
            pos += 4
        payload = data[pos:pos + length]
        pos += length
        tags.append((tag_type, payload))
        if tag_type == 0:  # End tag
            break
    return tags


def extract_images(swf_path, out_dir, jpeg_table=None):
    """SWF 하나에서 이미지 파일들을 추출, 저장된 파일 경로 목록 반환"""
    stem = Path(swf_path).stem.replace('.asp', '')
    with open(swf_path, 'rb') as f:
        data = f.read()

    try:
        tags = read_swf_tags(data)
    except Exception as e:
        print(f"  [파싱 오류] {e}")
        return []

    saved = []
    img_idx = 0

    # 1) 전역 JPEG 테이블 수집
    for tag_type, payload in tags:
        if tag_type == TAG_JPEG_TABLE:
            jpeg_table = payload
            break

    for tag_type, payload in tags:
        out_name = f"{stem}_{img_idx:03d}"
        out_path = None

        # ── JPEG 계열 ──
        if tag_type == TAG_DEFINE_BITS and len(payload) > 2:
            char_id = struct.unpack_from('<H', payload)[0]
            jpeg_data = payload[2:]
            if jpeg_table:
                # 일부 SWF는 분리된 헤더를 붙여야 함
                # 헤더 끝(FFD9)과 데이터 시작(FFD8) 사이를 연결
                table = jpeg_table
                if table.endswith(b'\xff\xd9'):
                    table = table[:-2]
                if jpeg_data.startswith(b'\xff\xd8'):
                    jpeg_data = jpeg_data[2:]
                jpeg_data = table + jpeg_data
            out_path = os.path.join(out_dir, out_name + '.jpg')
            _save_bytes(jpeg_data, out_path)

        elif tag_type in (TAG_DEFINE_BITS2, TAG_DEFINE_BITS3, TAG_DEFINE_BITS4) and len(payload) > 2:
            char_id = struct.unpack_from('<H', payload)[0]
            offset = 2
            if tag_type in (TAG_DEFINE_BITS3, TAG_DEFINE_BITS4):
                if len(payload) < 6:
                    continue
                alpha_offset = struct.unpack_from('<I', payload, 2)[0]
                offset = 6
                # JPEG 데이터만 추출 (알파 분리)
                jpeg_data = payload[offset:offset + alpha_offset - (offset - 2)]
            else:
                jpeg_data = payload[offset:]

            # 잘못된 JPEG 헤더 보정 (FF D9 FF D8 로 시작하는 경우)
            if jpeg_data[:4] == b'\xff\xd9\xff\xd8':
                jpeg_data = jpeg_data[4:]
            if not jpeg_data.startswith(b'\xff\xd8'):
                jpeg_data = b'\xff\xd8' + jpeg_data

            out_path = os.path.join(out_dir, out_name + '.jpg')
            _save_bytes(jpeg_data, out_path)

        # ── Lossless (PNG 계열) ──
        elif tag_type in (TAG_LOSSLESS, TAG_LOSSLESS2) and len(payload) > 7:
            out_path = _decode_lossless(payload, tag_type, out_dir, out_name)

        if out_path and os.path.exists(out_path):
            size = os.path.getsize(out_path)
            if size < 100:          # 너무 작으면 깨진 파일
                os.remove(out_path)
            else:
                saved.append(out_path)
                img_idx += 1

    return saved


def _save_bytes(data, path):
    try:
        with open(path, 'wb') as f:
            f.write(data)
        # Pillow로 유효성 검사 + 재저장 (손상 방지)
        img = Image.open(path)
        img.verify()
    except Exception:
        try:
            os.remove(path)
        except OSError:
            pass


def _decode_lossless(payload, tag_type, out_dir, out_name):
    """DefineBitsLossless(2) 태그를 PNG로 변환"""
    try:
        # char_id(2) + format(1) + width(2) + height(2) [+ colorTableSize(1)]
        char_id, fmt, w, h = struct.unpack_from('<HBHH', payload)
        offset = 7
        if fmt == 3:  # 8-bit colormap
            color_table_size = payload[offset] + 1
            offset += 1
        else:
            color_table_size = 0

        compressed = payload[offset:]
        raw = zlib.decompress(compressed)

        if fmt == 3:  # 8-bit indexed
            if tag_type == TAG_LOSSLESS2:
                # RGBA palette (4 bytes each)
                palette = raw[:color_table_size * 4]
                pixel_data = raw[color_table_size * 4:]
                img = Image.frombytes('P', (w, h), pixel_data[:w * h])
                flat = list(palette)
                img.putpalette(flat, rawmode='RGBA')
                img = img.convert('RGBA')
            else:
                palette = raw[:color_table_size * 3]
                pixel_data = raw[color_table_size * 3:]
                img = Image.frombytes('P', (w, h), pixel_data[:w * h])
                img.putpalette(list(palette))
                img = img.convert('RGB')
        elif fmt == 4:  # 15-bit RGB
            img = Image.frombytes('RGB', (w, h), raw, 'raw', 'BGR;15')
        elif fmt == 5:  # 24/32-bit
            if tag_type == TAG_LOSSLESS2:
                img = Image.frombytes('RGBA', (w, h), raw[:w * h * 4], 'raw', 'ARGB')
            else:
                # XRGB -> RGB
                arr = bytearray(raw[:w * h * 4])
                rgb = bytes(arr[i] for i in range(len(arr)) if i % 4 != 0)
                img = Image.frombytes('RGB', (w, h), rgb)
        else:
            return None

        out_path = os.path.join(out_dir, out_name + '.png')
        img.save(out_path)
        return out_path
    except Exception as e:
        print(f"  [Lossless 변환 오류] {e}")
        return None


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    swf_files = sorted(Path(SWF_DIR).glob('*.swf'))
    print(f"SWF 파일 {len(swf_files)}개 발견 → 저장 위치: {OUT_DIR}\n")

    total_saved = 0
    for swf in swf_files:
        print(f"처리 중: {swf.name}")
        saved = extract_images(str(swf), OUT_DIR)
        if saved:
            for p in saved:
                print(f"  → {os.path.basename(p)}")
            total_saved += len(saved)
        else:
            print(f"  (이미지 없음 또는 추출 실패)")

    print(f"\n완료: 총 {total_saved}개 이미지 추출 → {OUT_DIR}")


if __name__ == '__main__':
    main()
