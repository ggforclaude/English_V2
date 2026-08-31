"""
번역 엔진 모듈
- DeepLTranslator  : DeepL API (기본값, 무료 월 50만 자)
- ClaudeTranslator : Anthropic Claude API
- create_translator(engine): 엔진 선택 팩토리 함수
"""

import json
import os
import re
import time
from abc import ABC, abstractmethod
from typing import List


class BaseTranslator(ABC):
    @abstractmethod
    def translate_batch(self, texts: List[str]) -> List[str]:
        ...


class DeepLTranslator(BaseTranslator):
    TARGET_LANG = "KO"
    BATCH_SIZE  = 50
    MAX_TEXT_LEN = 10_000

    def __init__(self, api_key: str = None):
        import deepl
        key = api_key or os.environ.get("DEEPL_API_KEY", "")
        if not key:
            raise ValueError(
                "DeepL API 키가 없습니다.\n"
                "  1. https://www.deepl.com/pro#developer 에서 Free 플랜 가입\n"
                "  2. 환경변수 DEEPL_API_KEY=your_key 설정"
            )
        self._translator = deepl.Translator(key)

    def translate_batch(self, texts: List[str]) -> List[str]:
        if not texts:
            return []
        # 길이 초과 텍스트 잘라내기
        texts = [t[:self.MAX_TEXT_LEN] for t in texts]
        results = []
        for i in range(0, len(texts), self.BATCH_SIZE):
            batch = texts[i : i + self.BATCH_SIZE]
            try:
                translated = self._translator.translate_text(batch, target_lang=self.TARGET_LANG)
                results.extend(t.text for t in translated)
            except Exception as e:
                print(f"  [DeepL 번역 오류] {e}")
                results.extend(batch)
            if i + self.BATCH_SIZE < len(texts):
                time.sleep(0.1)
        return results


class ClaudeTranslator(BaseTranslator):
    MODEL       = "claude-sonnet-4-6"
    BATCH_SIZE  = 20
    MAX_TEXT_LEN = 10_000

    def __init__(self, api_key: str = None):
        import anthropic
        self._client = anthropic.Anthropic(
            api_key=api_key or os.environ.get("ANTHROPIC_API_KEY")
        )

    def translate_batch(self, texts: List[str]) -> List[str]:
        if not texts:
            return []
        texts = [t[:self.MAX_TEXT_LEN] for t in texts]
        results = []
        for i in range(0, len(texts), self.BATCH_SIZE):
            batch = texts[i : i + self.BATCH_SIZE]
            results.extend(self._request(batch))
            if i + self.BATCH_SIZE < len(texts):
                time.sleep(0.3)
        return results

    def _request(self, texts: List[str]) -> List[str]:
        # JSON 인코딩으로 프롬프트 인젝션 방지
        texts_json = json.dumps(texts, ensure_ascii=False)
        prompt = (
            "아래 JSON 배열의 영어 텍스트를 한국어로 번역하세요.\n"
            "전문 용어는 통용되는 한국어 표현을 사용하고, 없으면 영어를 유지하세요.\n"
            "줄바꿈과 포맷을 최대한 그대로 유지하세요.\n"
            '반드시 JSON으로만 응답하세요: {"translations": ["번역1", "번역2", ...]}\n\n'
            f"번역할 텍스트: {texts_json}"
        )
        try:
            resp = self._client.messages.create(
                model=self.MODEL,
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}],
            )
            content = resp.content[0].text
            m = re.search(r'\{.*\}', content, re.DOTALL)
            if m:
                translated = json.loads(m.group()).get("translations", [])
                if not isinstance(translated, list):
                    raise ValueError("translations가 리스트가 아닙니다")
                while len(translated) < len(texts):
                    translated.append(texts[len(translated)])
                return translated[: len(texts)]
        except Exception as e:
            print(f"  [Claude 번역 오류] {e}")
        return list(texts)


def create_translator(engine: str = "deepl", api_key: str = None) -> BaseTranslator:
    """engine: 'deepl' (기본) | 'claude'"""
    engine = engine.lower()
    if engine == "deepl":
        return DeepLTranslator(api_key)
    elif engine in ("claude", "anthropic"):
        return ClaudeTranslator(api_key)
    else:
        raise ValueError(f"알 수 없는 엔진: {engine!r}. 'deepl' 또는 'claude' 사용")
