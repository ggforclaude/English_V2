import json
import os
import subprocess
import time
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
LAST_RUN_FILE = os.path.join(BASE_DIR, "last_run.json")


def load_config():
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_date_range():
    today = datetime.now()
    if os.path.exists(LAST_RUN_FILE):
        with open(LAST_RUN_FILE, 'r') as f:
            last_run = datetime.strptime(json.load(f)['last_run'], "%Y-%m-%d")
        start = last_run + timedelta(days=1)
    else:
        start = today - timedelta(days=1)
    # start가 end보다 크면 하루치로 보정
    if start > today:
        start = today
    return start, today


def save_last_run(date):
    with open(LAST_RUN_FILE, 'w') as f:
        json.dump({'last_run': date.strftime("%Y-%m-%d")}, f)


def safe_screenshot(page, path):
    try:
        page.screenshot(path=path)
        print(f"  스크린샷: {os.path.basename(path)}")
        return True
    except Exception:
        return False


def go_to_trading_history(page, frame):
    # 전체메뉴가 이미 열려있으면 먼저 닫기
    close_btn = frame.get_by_role("button", name="전체메뉴 닫기")
    try:
        if close_btn.is_visible(timeout=1000):
            close_btn.click()
            page.wait_for_timeout(500)
    except Exception:
        pass

    frame.get_by_role("button", name="전체메뉴", exact=True).click()
    page.wait_for_timeout(800)

    # 메뉴 내부의 링크만 선택 (헤더 링크와 중복 방지)
    frame.locator(".menuList").get_by_role("link", name="종합거래내역").click()
    page.wait_for_timeout(2000)


def set_date(frame, page, calendar_index, target_date):
    frame.get_by_role("button", name="달력").nth(calendar_index).click()
    page.wait_for_timeout(600)
    frame.get_by_role("button", name=str(target_date.day), exact=True).click()
    page.wait_for_timeout(400)


def download_account(page, frame, account_name, start_date, end_date, save_dir):
    frame.get_by_role("link", name=account_name).first.click()
    page.wait_for_timeout(600)
    frame.get_by_role("link", name=account_name).last.click()
    page.wait_for_timeout(1000)

    set_date(frame, page, 0, start_date)
    set_date(frame, page, 1, end_date)

    frame.get_by_text("RP매매내역포함").click()
    page.wait_for_timeout(400)

    frame.get_by_role("button", name="조회").click()
    page.wait_for_timeout(2500)

    account_id = account_name.split()[0].replace("-", "")
    filename = (
        f"신한투자_{account_id}"
        f"_{start_date.strftime('%Y%m%d')}"
        f"_{end_date.strftime('%Y%m%d')}.xlsx"
    )
    save_path = os.path.join(save_dir, filename)

    with page.expect_download() as dl:
        with page.expect_popup() as popup:
            frame.get_by_role("button", name="엑셀저장").click()
        popup.value.close()

    dl.value.save_as(save_path)
    print(f"  저장 완료: {filename}")


def run():
    cfg = load_config()
    start_date, end_date = get_date_range()
    save_dir = cfg['save_dir']
    os.makedirs(save_dir, exist_ok=True)

    print(f"조회 기간: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")

    # Edge 프로세스 전체 종료
    subprocess.run(["taskkill", "/f", "/im", "msedge.exe"], capture_output=True)
    time.sleep(3)

    with sync_playwright() as p:
        edge_data_dir = r"C:\Users\ggulb\AppData\Local\Microsoft\Edge\User Data"
        try:
            context = p.chromium.launch_persistent_context(
                user_data_dir=edge_data_dir,
                channel="msedge",
                headless=False,
                ignore_default_args=[
                    "--disable-extensions",
                    "--disable-component-extensions-with-background-pages",
                ],
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-background-mode",
                ],
                timeout=60000,
            )
        except Exception as e:
            err = str(e).encode("ascii", "replace").decode("ascii")
            print(f"Edge 실행 오류: {err[:300]}")
            return

        try:
            page = context.new_page()
            frame = page.locator("#mainFrame").content_frame

            # 홈 → 로그인 페이지
            page.goto("https://www.shinhansec.com/")
            page.wait_for_timeout(2000)

            frame.get_by_role("link", name="로그인").click()
            page.wait_for_timeout(2000)

            # ID 자동 입력 (암호화 불필요)
            id_field = frame.get_by_role("textbox", name="사용자 ID")
            id_field.click()
            page.wait_for_timeout(200)
            id_field.fill(cfg['id'])
            page.wait_for_timeout(200)

            # 비밀번호는 TouchEn 암호화 필요 → 사용자가 직접 입력
            pw_field = frame.get_by_role("textbox", name="접속 비밀번호")
            pw_field.click()

            print("\n" + "="*50)
            print("브라우저에서 비밀번호를 직접 입력하고 로그인 버튼을 누르세요.")
            print("로그인 완료 후 여기서 Enter를 누르세요...")
            print("="*50)
            input()

            page.wait_for_timeout(3000)
            print(f"로그인 후 URL: {page.url}")

            # 계좌별 반복
            for i, account in enumerate(cfg['accounts'], 1):
                print(f"\n[{i}/{len(cfg['accounts'])}] {account}")
                try:
                    go_to_trading_history(page, frame)
                    download_account(page, frame, account, start_date, end_date, save_dir)
                except Exception as e:
                    print(f"  오류 발생: {e}")
                    screenshot_path = os.path.join(save_dir, f"error_acct{i}.png")
                    if not safe_screenshot(page, screenshot_path):
                        print("  브라우저가 닫혔습니다. 루프 중단.")
                        break

        finally:
            try:
                context.close()
            except Exception:
                pass

    save_last_run(end_date)
    print("\n전체 완료!")


if __name__ == "__main__":
    run()
