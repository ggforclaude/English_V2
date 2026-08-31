# -*- coding: utf-8 -*-
import os
import sys
import hashlib
from collections import defaultdict
from datetime import datetime

# Windows 터미널 한글 출력 설정
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

PHOTO_EXTS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.heic', '.heif',
              '.tiff', '.tif', '.webp', '.raw', '.cr2', '.nef', '.arw',
              '.mp4', '.mov', '.avi', '.3gp', '.mkv'}

SCAN_ROOT = 'D:/OneDrive'
LOG_PATH = 'D:/OneDrive/1. NA/cluade/deleted_log.txt'


def md5_hash(filepath, chunk_size=65536):
    h = hashlib.md5()
    try:
        with open(filepath, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                h.update(chunk)
        return h.hexdigest()
    except (PermissionError, OSError):
        return None


def format_size(size_bytes):
    if size_bytes >= 1024 * 1024:
        return f"{size_bytes / (1024*1024):.1f} MB"
    return f"{size_bytes / 1024:.1f} KB"


def get_mtime(path):
    try:
        ts = os.path.getmtime(path)
        return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')
    except OSError:
        return '알 수 없음'


def scan_duplicates():
    print("파일 목록 수집 중... (잠시 기다려 주세요)")
    size_map = defaultdict(list)
    total = 0
    for root, dirs, files in os.walk(SCAN_ROOT):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for fname in files:
            ext = os.path.splitext(fname.lower())[1]
            if ext in PHOTO_EXTS:
                fpath = os.path.join(root, fname)
                try:
                    size = os.path.getsize(fpath)
                    size_map[size].append(fpath)
                    total += 1
                except OSError:
                    pass

    print(f"총 {total:,}개 파일 수집 완료")
    print("해시 비교 중... (수분 소요)")

    candidates = {sz: paths for sz, paths in size_map.items() if len(paths) > 1}
    candidate_count = sum(len(v) for v in candidates.values())

    hash_map = defaultdict(list)
    processed = 0
    for size, paths in candidates.items():
        for fpath in paths:
            h = md5_hash(fpath)
            if h:
                hash_map[(size, h)].append(fpath)
            processed += 1
            if processed % 1000 == 0:
                pct = processed * 100 // candidate_count
                print(f"  {processed:,}/{candidate_count:,} ({pct}%)...")

    duplicates = [(size, paths) for (size, _), paths in hash_map.items() if len(paths) > 1]
    duplicates.sort(key=lambda x: -x[0])  # 큰 파일부터
    print(f"\n중복 그룹 {len(duplicates)}개 발견\n")
    return duplicates


def print_separator():
    print("=" * 70)


def interactive_delete(duplicates):
    deleted_count = 0
    deleted_size = 0
    skipped = 0
    log_lines = []

    print_separator()
    print(f"  총 {len(duplicates)}개 그룹 처리 시작")
    print("  입력 방법:")
    print("    삭제할 파일 번호 입력 (예: 2  또는  1,3  또는  1 3)")
    print("    s 또는 Enter  = 건너뛰기")
    print("    q             = 종료")
    print_separator()

    for idx, (size, paths) in enumerate(duplicates, 1):
        print(f"\n[{idx}/{len(duplicates)}] 그룹 - 파일 크기: {format_size(size)}")
        print("-" * 70)

        for i, fpath in enumerate(paths, 1):
            mtime = get_mtime(fpath)
            fname = os.path.basename(fpath)
            folder = os.path.dirname(fpath)
            print(f"  [{i}] {fname}")
            print(f"       경로: {folder}")
            print(f"       수정일: {mtime}  /  크기: {format_size(size)}")

        print()
        while True:
            try:
                ans = input("  삭제할 번호 (Enter=건너뛰기, q=종료): ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\n종료합니다.")
                break

            if ans in ('', 's'):
                skipped += 1
                break
            elif ans == 'q':
                print("\n종료합니다.")
                _print_summary(deleted_count, deleted_size, skipped, log_lines)
                return

            # 번호 파싱 (쉼표 또는 공백 구분)
            tokens = ans.replace(',', ' ').split()
            try:
                nums = [int(t) for t in tokens]
            except ValueError:
                print("  올바른 번호를 입력하세요.")
                continue

            invalid = [n for n in nums if n < 1 or n > len(paths)]
            if invalid:
                print(f"  범위를 벗어난 번호: {invalid}")
                continue

            # 전체 삭제 방지: 그룹 내 파일 모두 삭제하려는 경우 경고
            if len(set(nums)) == len(paths):
                confirm = input(f"  경고: 그룹 내 모든 파일을 삭제합니다. 정말 삭제할까요? (y/n): ").strip().lower()
                if confirm != 'y':
                    continue

            # 삭제 확인
            to_delete = [paths[n - 1] for n in set(nums)]
            print(f"\n  삭제 대상 ({len(to_delete)}개):")
            for p in to_delete:
                print(f"    - {p}")
            confirm = input("  삭제하시겠습니까? (y/n): ").strip().lower()
            if confirm != 'y':
                print("  취소했습니다.")
                continue

            for p in to_delete:
                try:
                    os.remove(p)
                    deleted_count += 1
                    deleted_size += size
                    log_lines.append(f"[삭제] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  {p}")
                    print(f"  [삭제됨] {os.path.basename(p)}")
                except OSError as e:
                    print(f"  [오류] {p}: {e}")
                    log_lines.append(f"[오류] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  {p}  ({e})")
            break

    _print_summary(deleted_count, deleted_size, skipped, log_lines)


def _print_summary(deleted_count, deleted_size, skipped, log_lines):
    print()
    print_separator()
    print(f"  완료!")
    print(f"  삭제된 파일: {deleted_count}개  ({format_size(deleted_size)} 확보)")
    print(f"  건너뛴 그룹: {skipped}개")
    print_separator()

    if log_lines:
        with open(LOG_PATH, 'a', encoding='utf-8') as f:
            f.write(f"\n=== 실행: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
            f.write('\n'.join(log_lines) + '\n')
        print(f"  삭제 로그: {LOG_PATH}")


if __name__ == '__main__':
    duplicates = scan_duplicates()
    if not duplicates:
        print("중복 파일이 없습니다.")
    else:
        interactive_delete(duplicates)
