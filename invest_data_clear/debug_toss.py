"""디버그: 토스 PDF 원시 데이터 확인"""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from convert_all import get_all_lines, split_toss_sections, filter_toss_section, filter_usd_lines, DATE_RE_TOSS

BASE = os.path.dirname(os.path.abspath(__file__))
PASSWORD = '840313'

for fn in ['토스거래1.pdf', '토스거래2.pdf', '토스거래3.pdf']:
    fpath = os.path.join(BASE, fn)
    print(f'\n{"="*60}')
    print(f'파일: {fn}')
    lines = get_all_lines(fpath, password=PASSWORD)
    won_raw, dollar_raw = split_toss_sections(lines)
    won_data = filter_toss_section(won_raw)

    won_dates = [i for i, l in enumerate(won_data) if DATE_RE_TOSS.match(l)]

    # 처음 5개 chunk 출력
    print(f'\n[원화 첫 5 chunk]')
    for k, start in enumerate(won_dates[:5]):
        end = won_dates[k+1] if k+1 < len(won_dates) else len(won_data)
        chunk = won_data[start:end]
        print(f'  chunk[{k}] len={len(chunk)}: {chunk}')

    # 문제가 될 수 있는 chunk 찾기 (마지막 2개가 숫자가 아닌 경우)
    print(f'\n[원화 - 잔고/잔액이 문자인 chunk]')
    problem_count = 0
    for k, start in enumerate(won_dates):
        end = won_dates[k+1] if k+1 < len(won_dates) else len(won_data)
        chunk = won_data[start:end]
        if len(chunk) >= 2:
            last = chunk[-1]
            second_last = chunk[-2]
            # 숫자가 아닌 경우
            try:
                float(str(last).replace(',', ''))
            except ValueError:
                print(f'  chunk[{k}] 잔액 문제: {chunk}')
                problem_count += 1
                if problem_count >= 3:
                    break

    # 환전 거래 chunk 출력
    print(f'\n[원화 - 환전 관련 chunk (환율 포함)]')
    fx_count = 0
    for k, start in enumerate(won_dates):
        end = won_dates[k+1] if k+1 < len(won_dates) else len(won_data)
        chunk = won_data[start:end]
        chunk_str = ' '.join(chunk)
        if '환전' in chunk_str or '환율' in chunk_str:
            print(f'  chunk[{k}]: {chunk}')
            fx_count += 1
            if fx_count >= 3:
                break
