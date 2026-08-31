"""상세 디버그: 문제 chunk 및 환전 chunk 분석"""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from convert_all import get_all_lines, split_toss_sections, filter_toss_section, filter_usd_lines, DATE_RE_TOSS

BASE = os.path.dirname(os.path.abspath(__file__))
PASSWORD = '840313'

# 모든 파일에서 원화 won_raw lines 확인
for fn in ['토스거래1.pdf', '토스거래2.pdf', '토스거래3.pdf', '토스거래4.pdf', '토스거래5.pdf']:
    fpath = os.path.join(BASE, fn)
    lines = get_all_lines(fpath, password=PASSWORD)
    won_raw, _ = split_toss_sections(lines)

    # filter 전 won_raw에서 특수 줄 패턴 찾기
    special = [l for l in won_raw if '잔고구분' in l or '금액단위' in l or '단위' in l or '달러' in l]
    if special:
        print(f'\n[{fn}] won_raw 특수줄:')
        for s in set(special):
            print(f'  repr: {repr(s)}')

# 토스거래1.pdf 상세 분석
print('\n\n=== 토스거래1.pdf 환전 chunk 분석 ===')
lines = get_all_lines(os.path.join(BASE, '토스거래1.pdf'), password=PASSWORD)
won_raw, _ = split_toss_sections(lines)
won_data = filter_toss_section(won_raw)

# 환전 포함 won_raw 전체 구간 출력 (첫 번째 환전 주변)
print('\n[won_raw 처음 50줄]:')
for i, l in enumerate(won_raw[:50]):
    print(f'  {i:3d}: {repr(l)}')

# filter 후 상태
print('\n[won_data 처음 60줄]:')
for i, l in enumerate(won_data[:60]):
    print(f'  {i:3d}: {repr(l)}')

# 문제 chunk (잔액이 숫자 아닌 것)
print('\n\n=== 전체 파일 문제 chunk 목록 ===')
total_won = 0
problem_rows = []
for fn in ['토스거래1.pdf', '토스거래2.pdf', '토스거래3.pdf', '토스거래4.pdf', '토스거래5.pdf']:
    fpath = os.path.join(BASE, fn)
    lines = get_all_lines(fpath, password=PASSWORD)
    won_raw, _ = split_toss_sections(lines)
    won_data = filter_toss_section(won_raw)
    won_dates = [i for i, l in enumerate(won_data) if DATE_RE_TOSS.match(l)]
    total_won += len(won_dates)

    for k, start in enumerate(won_dates):
        end = won_dates[k+1] if k+1 < len(won_dates) else len(won_data)
        chunk = won_data[start:end]
        last = chunk[-1]
        try:
            float(str(last).replace(',', ''))
        except ValueError:
            problem_rows.append((fn, k, chunk))
            print(f'  [{fn}] chunk[{k}] len={len(chunk)}: {chunk}')

print(f'\n총 won chunks: {total_won}')
print(f'문제 chunks: {len(problem_rows)}')
