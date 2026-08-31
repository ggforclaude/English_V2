"""
Improve_Eng v2 - 근거 기반 영어 학습 커리큘럼
매일 04:00 KST GitHub Actions에서 실행

구성:
  1. VOA Learning English (듣기)
  2. BBC/Perfect English Grammar (문법)
  3. Anki SRS (단어)
  4. 미니 에세이 (출력)
  5. 다독 권장 (Reading)
  6. 약점 분석 + Claude 보충 자료

웹 페이지:
  /today - 고정 URL 오늘의 학습 콘텐츠
  /report - 학습 리포트 및 약점 분석
"""
import asyncio
import logging
import sys
import os
from datetime import datetime
import pytz

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)
KST = pytz.timezone("Asia/Seoul")


async def main() -> None:
    """메인 실행 루프"""
    from voa_crawler import fetch_voa_daily_content
    from anki_connector import get_anki_stats
    from sheets_manager_v2 import get_sheets_manager
    from report_analyzer import analyze_weak_points
    from today_page_builder import build_today_page
    from level_tracker import LevelTracker
    from question_generator import generate_all_questions, generate_daily_learning
    from content_fetcher import fetch_daily_content

    today = datetime.now(KST).date()
    tracker = LevelTracker()
    day_number = tracker.get_day_number(today)
    sheets = await get_sheets_manager()

    log.info("=" * 60)
    log.info(f"Improve_Eng v2 시작: {today}  Day {day_number}")
    log.info("=" * 60)

    try:
        # 1. VOA Learning English 콘텐츠 수집
        log.info("[1] VOA Learning English 콘텐츠 수집...")
        voa_content = await fetch_voa_daily_content(today)
        log.info(f"  ✓ {voa_content.get('title', '')[:50]}...")

        # 2. 문법 콘텐츠 (기존 content_fetcher 사용)
        log.info("[2] 문법 콘텐츠 수집...")
        full_content = await fetch_daily_content(today)
        grammar_content = full_content.get("grammar", {})
        log.info(f"  ✓ {grammar_content.get('topic', 'Grammar')}")

        # 3. Anki 통계 조회
        log.info("[3] Anki 학습 상태 조회...")
        anki_stats = await get_anki_stats()
        log.info(f"  ✓ 오늘 복습: {anki_stats['today']['total_due']}개")

        # 4. 현재 레벨 계산
        log.info("[4] 현재 레벨 계산...")
        current_levels = tracker.calculate_current_levels()
        log.info(f"  ✓ {current_levels}")

        # 5. 일일 학습 콘텐츠 생성
        log.info("[5] 학습 콘텐츠 생성...")
        is_baseline = day_number <= 7
        daily_learning = await generate_daily_learning(
            grammar_info=grammar_content,
            listening_item=voa_content,
            listening_script={"script_en": voa_content.get("text", "")},
            etymology=full_content.get("etymology", {}),
            pronunciation=full_content.get("pronunciation", {}),
            current_levels=current_levels,
            day_number=day_number,
        )
        log.info("  ✓ 학습 콘텐츠 생성 완료")

        # 6. 퀴즈 문제 생성
        log.info("[6] 퀴즈 문제 생성...")
        questions = await generate_all_questions(
            content=full_content,
            current_levels=current_levels,
            is_baseline=is_baseline,
            day_number=day_number,
        )
        log.info(f"  ✓ {len(questions)} 영역 문제 생성")

        # 7. 지난 분석 및 약점 리포트 생성 (주 1회 또는 필요시)
        weak_points_report = None
        if day_number % 7 == 1:  # 주 1회 (매주 월요일)
            log.info("[7] 약점 분석 리포트 생성...")
            learning_history = await sheets.get_learning_history(days=30)
            prev_results = tracker.get_yesterday_results(today)
            wrong_items = prev_results.get("wrong_items", []) if prev_results else []

            weak_points_report = await analyze_weak_points(
                learning_history=learning_history,
                wrong_items=wrong_items,
                current_levels=current_levels,
                days_count=30,
            )
            log.info(f"  ✓ 약점 {len(weak_points_report.get('weak_areas', []))}개 분석")

            # 약점을 Sheets에 저장
            await sheets.save_weak_points(
                analysis_date=today,
                weak_areas=weak_points_report.get("weak_areas", []),
            )

        # 8. /today 페이지 생성
        log.info("[8] /today 페이지 생성...")
        page_path = build_today_page(
            today=today,
            day_number=day_number,
            anki_stats=anki_stats,
            voa_content=voa_content,
            grammar_content=grammar_content,
            daily_learning=daily_learning,
            current_levels=current_levels,
            report_available=(weak_points_report is not None),
        )
        log.info(f"  ✓ 저장: {page_path}")

        # 9. /report 페이지 생성 (주 1회)
        if weak_points_report and weak_points_report.get("html_report"):
            log.info("[9] /report 페이지 생성...")
            report_path = _save_report_html(weak_points_report["html_report"])
            log.info(f"  ✓ 저장: {report_path}")

        # 10. Google Sheets에 오늘 데이터 저장
        log.info("[10] Google Sheets에 학습 데이터 저장...")
        questions_correct = _estimate_questions_correct(tracker, today)
        questions_total = len(questions)

        await sheets.save_daily_learning(
            today=today,
            day_number=day_number,
            anki_stats=anki_stats,
            grammar_content=grammar_content,
            voa_content=voa_content,
            output_topic=daily_learning.get("topic", "일상 이야기"),
            reading_rec="Oxford Bookworms",
            questions_correct=questions_correct,
            questions_total=questions_total,
            levels=current_levels,
        )
        log.info("  ✓ Sheets 저장 완료")

        # 11. VOA 콘텐츠 캐시
        log.info("[11] VOA 콘텐츠 캐시...")
        await sheets.cache_voa_content(
            today=today,
            level=voa_content.get("level", ""),
            title=voa_content.get("title", ""),
            audio_url=voa_content.get("audio_url", ""),
            text_summary=voa_content.get("text", "")[:200],
            link=voa_content.get("link", ""),
        )
        log.info("  ✓ 캐시 완료")

        # 12. 오늘 문제를 Sheets에 저장 (내일 채점용)
        log.info("[12] 오늘 문제 저장...")
        tracker.save_today_questions(today, questions)
        log.info("  ✓ 문제 저장 완료")

        log.info("=" * 60)
        log.info("✓ 완료 - /today 페이지에서 오늘의 학습을 시작하세요!")
        log.info("=" * 60)

    except Exception as e:
        log.error(f"❌ 오류 발생: {e}", exc_info=True)
        raise


def _save_report_html(html_content: str) -> str:
    """리포트 HTML을 docs/report/index.html로 저장"""
    import pathlib
    base = pathlib.Path(__file__).parent.parent / "docs" / "report"
    base.mkdir(parents=True, exist_ok=True)
    out = base / "index.html"
    out.write_text(html_content, encoding="utf-8")
    return str(out)


def _estimate_questions_correct(tracker, today) -> int:
    """어제 문제의 정답 수 추정 (실제로는 Google Form 응답에서 가져와야 함)"""
    # 현재는 임시로 0을 반환 (나중에 responses 시트에서 읽도록 수정)
    return 0


if __name__ == "__main__":
    asyncio.run(main())
