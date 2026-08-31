"""won_raw 환전 구간 및 달러 섹션 상세 확인"""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from convert_all import get_all_lines, split_toss_sections, filter_toss_section, filter_usd_lines, DATE_RE_TOSS

BASE = os.path.dirname(os.path.abspath(__file__))
PASSWORD = '840313'

# 파일1 won_raw 전체 (처음 환전 구간)
print('=== 토스거래1.pdf won_raw (인덱스 20~45) ===')
lines = get_all_lines(os.path.join(BASE, '토스거래1.pdf'), password=PASSWORD)
won_raw, dollar_raw = split_toss_sections(lines)
for i, l in enumerate(won_raw[20:45], 20):
    print(f'  {i:4d}: {repr(l)}')

# 달러 섹션 raw 처음 60줄
print('\n=== 토스거래1.pdf dollar_raw (처음 60줄) ===')
for i, l in enumerate(dollar_raw[:60]):
    print(f'  {i:4d}: {repr(l)}')

# 달러 섹션 filter 후
dollar_data_raw = filter_toss_section(dollar_raw)
print('\n=== 토스거래1.pdf dollar_data_raw (처음 60줄, USD 필터 전) ===')
for i, l in enumerate(dollar_data_raw[:60]):
    print(f'  {i:4d}: {repr(l)}')

dollar_data = filter_usd_lines(dollar_data_raw)
print('\n=== 토스거래1.pdf dollar_data (처음 60줄, USD 필터 후) ===')
for i, l in enumerate(dollar_data[:60]):
    print(f'  {i:4d}: {repr(l)}')

# 파일4 won_raw 환전 구간
print('\n\n=== 토스거래4.pdf won_raw (인덱스 10~35) ===')
lines4 = get_all_lines(os.path.join(BASE, '토스거래4.pdf'), password=PASSWORD)
won_raw4, dollar_raw4 = split_toss_sections(lines4)
for i, l in enumerate(won_raw4[10:35], 10):
    print(f'  {i:4d}: {repr(l)}')

# 파일4 달러 섹션 처음
print('\n=== 토스거래4.pdf dollar_raw (처음 50줄) ===')
for i, l in enumerate(dollar_raw4[:50]):
    print(f'  {i:4d}: {repr(l)}')

# 실제 생성된 엑셀의 문제 행 확인
print('\n\n=== 생성된 엑셀 문제 행 확인 ===')
import openpyxl
wb = openpyxl.load_workbook(os.path.join(BASE, '토스_통합거래내역.xlsx'))
ws = wb['원화 거래내역']
for row in ws.iter_rows(min_row=2, values_only=True):
    잔고 = row[12]
    잔액 = row[13]
    # 잔고나 잔액이 문자열인 경우
    if isinstance(잔고, str) or isinstance(잔액, str):
        print(f'  행: {row}')
