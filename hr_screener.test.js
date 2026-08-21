/*
 * hr_screener.html 회귀 테스트
 *
 *   node hr_screener.test.js
 *
 * HTML 안의 순수 로직 함수를 원본 그대로 떼어내 실행한다.
 * 함수를 여기에 베껴 쓰지 않으므로, 본체가 바뀌면 테스트도 같이 바뀐다.
 */
'use strict';

const fs = require('fs');
const path = require('path');
const assert = require('assert');

const SRC = fs.readFileSync(path.join(__dirname, 'hr_screener.html'), 'utf8');

/** header로 시작하는 함수 선언을 중괄호 균형으로 잘라낸다 */
function grabBlock(header) {
  const i = SRC.indexOf(header);
  if (i < 0) throw new Error('찾지 못함: ' + header);
  const j = SRC.indexOf('{', i);
  let depth = 0;
  for (let k = j; k < SRC.length; k++) {
    if (SRC[k] === '{') depth++;
    else if (SRC[k] === '}' && --depth === 0) return SRC.slice(i, k + 1);
  }
  throw new Error('중괄호가 맞지 않음: ' + header);
}

/** 한 줄짜리 선언을 그대로 잘라낸다 */
function grabLine(header) {
  const i = SRC.indexOf(header);
  if (i < 0) throw new Error('찾지 못함: ' + header);
  const end = SRC.indexOf('\n', i);
  return SRC.slice(i, end);
}

const code = [
  grabBlock('function scoreOf('),
  grabBlock('function buildUserMsg('),
  grabBlock('function fmtSec('),
  grabLine('const norm = (s) =>'),
  grabBlock('function verifyEvidence('),
  grabBlock('function sortValue('),
  grabBlock('function visible('),
].join('\n\n');

// 모듈 스코프 변수(sortKey 등)를 흉내 낸 상자 안에서 실행한다
const M = new Function(`
  let sortKey = 'total', sortDir = 'desc', filterVerdict = 'all';
  ${code}
  return {
    scoreOf, buildUserMsg, fmtSec, verifyEvidence, sortValue, visible,
    setSort: (k) => { sortKey = k; },
    setFilter: (f) => { filterVerdict = f; }
  };
`)();

let n = 0;
const test = (name, fn) => { fn(); n++; console.log('  ok  ' + name); };

const job = {
  title: '공간운영 기획', cutoff: 70,
  criteria: [
    { kind: '필수', label: '공간운영 3년+', desc: '오피스/상업시설', weight: 40 },
    { kind: '필수', label: '입주사 응대', desc: '', weight: 30 },
    { kind: '우대', label: '커뮤니티 기획', desc: '', weight: 20 },
    { kind: '공통', label: '협업 커뮤니케이션', desc: '', weight: 10 },
  ],
};
const crit = (id, score, level, evidence) => ({ id, score, level, evidence: evidence ?? 'x' });

console.log('\n채점 로직');

test('가중 총점을 비중대로 계산한다', () => {
  const r = M.scoreOf(job, { criteria: [
    crit('c1', 90, '충족'), crit('c2', 80, '충족'),
    crit('c3', 50, '부분충족'), crit('c4', 70, '충족'),
  ]});
  // (90*40 + 80*30 + 50*20 + 70*10) / 100 = 77
  assert.strictEqual(r.total, 77);
  assert.strictEqual(r.verdict, '추천');
  assert.strictEqual(r.mustFail, false);
});

test('필수 항목이 미충족이면 점수와 무관하게 비추천으로 내린다', () => {
  const r = M.scoreOf(job, { criteria: [
    crit('c1', 95, '충족'), crit('c2', 95, '미충족'),
    crit('c3', 95, '충족'), crit('c4', 95, '충족'),
  ]});
  assert.strictEqual(r.total, 95);
  assert.strictEqual(r.mustFail, true);
  assert.strictEqual(r.verdict, '비추천');
});

test('합격선 아래 15점까지는 보류로 둔다', () => {
  const r = M.scoreOf(job, { criteria: [
    crit('c1', 60, '부분충족'), crit('c2', 60, '부분충족'),
    crit('c3', 60, '부분충족'), crit('c4', 60, '부분충족'),
  ]});
  assert.strictEqual(r.total, 60);
  assert.strictEqual(r.verdict, '보류');
});

test('추천·보류·비추천의 경계를 정확히 지킨다', () => {
  // 경계를 한 점씩 짚는다. 구간 한가운데만 확인하면 경계가 밀려도 통과해 버린다.
  const flat = { title: 't', cutoff: 70, criteria: [
    { kind: '공통', label: 'a', desc: '', weight: 50 },
    { kind: '공통', label: 'b', desc: '', weight: 50 },
  ]};
  const at = (score) => M.scoreOf(flat, {
    criteria: [crit('c1', score, '부분충족'), crit('c2', score, '부분충족')]
  });
  assert.strictEqual(at(70).verdict, '추천');     // 합격선 정확히
  assert.strictEqual(at(69).verdict, '보류');     // 합격선 바로 아래
  assert.strictEqual(at(55).verdict, '보류');     // 보류 하한 정확히 (70 - 15)
  assert.strictEqual(at(54).verdict, '비추천');   // 보류 하한 바로 아래
});

test('비중 합계가 100이 아니어도 환산한다', () => {
  const j = { title: 't', cutoff: 70, criteria: [
    { kind: '공통', label: 'a', desc: '', weight: 50 },
    { kind: '공통', label: 'b', desc: '', weight: 20 },
  ]};
  const r = M.scoreOf(j, { criteria: [crit('c1', 100, '충족'), crit('c2', 30, '부분충족')] });
  assert.strictEqual(r.total, 80);   // (100*50 + 30*20) / 70
  assert.strictEqual(r.wsum, 70);
});

test('AI가 항목을 빠뜨리면 0점 미충족으로 메운다', () => {
  const r = M.scoreOf(job, { criteria: [crit('c1', 100, '충족')] });
  assert.strictEqual(r.rows.length, 4);
  assert.strictEqual(r.rows[3].score, 0);
  assert.strictEqual(r.rows[3].level, '미충족');
  assert.strictEqual(r.total, 40);
  assert.strictEqual(r.verdict, '비추천');   // 필수(c2)가 미충족이 되므로
});

test('범위를 벗어난 점수와 알 수 없는 판정을 잘라낸다', () => {
  const j = { title: 't', cutoff: 70, criteria: [
    { kind: '공통', label: 'a', desc: '', weight: 50 },
    { kind: '공통', label: 'b', desc: '', weight: 50 },
  ]};
  const r = M.scoreOf(j, { criteria: [
    { id: 'c1', score: 150, level: '충족', evidence: 'x' },
    { id: 'c2', score: -20, level: '아주좋음', evidence: 'y' },
  ]});
  assert.strictEqual(r.rows[0].score, 100);
  assert.strictEqual(r.rows[1].score, 0);
  assert.strictEqual(r.rows[1].level, '미충족');
});

test('기여도의 합이 총점과 일치한다 (기여도 막대의 전제)', () => {
  const r = M.scoreOf(job, { criteria: [
    crit('c1', 90, '충족'), crit('c2', 80, '충족'),
    crit('c3', 50, '부분충족'), crit('c4', 70, '충족'),
  ]});
  const sum = r.rows.reduce((a, x) => a + x.score * x.weight / r.wsum, 0);
  assert.ok(Math.abs(sum - r.total) < 0.51, `기여도 합 ${sum} vs 총점 ${r.total}`);
});

console.log('\n프롬프트');

test('항목 id·구분·비중이 프롬프트에 들어간다', () => {
  const msg = M.buildUserMsg(job, { name: '김지연', doc: '경력 | 아모레퍼시픽' });
  assert.ok(msg.includes('c1 [필수, 비중 40%] 공간운영 3년+ — 오피스/상업시설'));
  assert.ok(msg.includes('c4 [공통, 비중 10%] 협업 커뮤니케이션'));
  assert.ok(msg.includes('[지원자] 김지연'));
  assert.ok(msg.includes('경력 | 아모레퍼시픽'));
});

test('지원서가 비면 빈칸이 아니라 표시를 넣는다', () => {
  assert.ok(M.buildUserMsg(job, { name: 'A', doc: '' }).includes('(내용 없음)'));
});

console.log('\n근거 대조');

const DOC = '경력\n직장 | (주)아모레퍼시픽 | 근무기간 | 2008.09 ~ 2025.12\n업무 | 오피스 레이아웃 계획 및 변경';

test('지원서에 있는 인용은 통과시킨다', () => {
  assert.strictEqual(M.verifyEvidence(DOC, '오피스 레이아웃 계획 및 변경'), 'ok');
});

test('공백·따옴표·구분자가 달라도 같은 문장으로 본다', () => {
  assert.strictEqual(M.verifyEvidence(DOC, '오피스  레이아웃\n계획 및 변경'), 'ok');
  assert.strictEqual(M.verifyEvidence(DOC, '직장 (주)아모레퍼시픽'), 'ok');   // ' | ' 가 빠져도 통과
});

test('지원서에 없는 문장은 미확인으로 잡아낸다', () => {
  assert.strictEqual(M.verifyEvidence(DOC, '스타트업 액셀러레이터 운영 총괄'), 'missing');
});

test('근거가 비었으면 none, 원문이 없으면 unknown', () => {
  assert.strictEqual(M.verifyEvidence(DOC, ''), 'none');
  assert.strictEqual(M.verifyEvidence('', '무엇이든'), 'unknown');
});

console.log('\n정렬 · 필터');

const A = { name: '김지연', total: 82, verdict: '추천', rows: [{ score: 90 }, { score: 70 }] };
const B = { name: '조성철', total: 77, verdict: '보류', rows: [{ score: 60 }, { score: 95 }] };
const C = { name: '박규연', total: 0, verdict: undefined, error: '오류' };

test('총점·이름·판정으로 정렬값을 낸다', () => {
  M.setSort('total');   assert.strictEqual(M.sortValue(A), 82);
  M.setSort('name');    assert.strictEqual(M.sortValue(A), '김지연');
  M.setSort('verdict'); assert.strictEqual(M.sortValue(A), 3);
  M.setSort('verdict'); assert.strictEqual(M.sortValue(B), 2);
  M.setSort('verdict'); assert.strictEqual(M.sortValue(C), 0);
});

test('항목별 점수로도 정렬한다', () => {
  M.setSort('crit:0'); assert.strictEqual(M.sortValue(A), 90);
  M.setSort('crit:1'); assert.strictEqual(M.sortValue(A), 70);
  M.setSort('crit:1'); assert.strictEqual(M.sortValue(B), 95);   // 총점은 A가 높지만 이 항목은 B가 높다
  M.setSort('crit:9'); assert.strictEqual(M.sortValue(A), -1);   // 없는 항목
});

test('판정 필터가 오류·중단 건을 섞지 않는다', () => {
  M.setFilter('all');    assert.ok(M.visible(A) && M.visible(B) && M.visible(C));
  M.setFilter('추천');   assert.ok(M.visible(A) && !M.visible(B) && !M.visible(C));
  M.setFilter('error');  assert.ok(!M.visible(A) && !M.visible(B) && M.visible(C));
});

test('오류 건은 판정이 남아 있어도 판정 필터에 걸리지 않는다', () => {
  const broken = { name: 'X', verdict: '추천', error: '타임아웃' };
  M.setFilter('추천');
  assert.strictEqual(M.visible(broken), false);
});

console.log('\n표기');

test('소요 시간을 분·초로 적는다', () => {
  assert.strictEqual(M.fmtSec(45), '45초');
  assert.strictEqual(M.fmtSec(88), '1분 28초');
  assert.strictEqual(M.fmtSec(120), '2분');
});

console.log('\n정적 검사');

const JS = SRC.match(/<script>\n([\s\S]*?)\n<\/script>/)[1];

test('인라인 스크립트가 문법 오류 없이 파싱된다', () => {
  new Function(JS);   // 파싱만 한다 — 실행하지 않는다
});

test('$(id)로 찾는 요소가 HTML에 모두 있다', () => {
  const inHtml = new Set([...SRC.matchAll(/id="([^"]+)"/g)].map(m => m[1]));
  const inJs = new Set([...JS.matchAll(/\$\('([a-zA-Z0-9_-]+)'\)/g)].map(m => m[1]));
  const missing = [...inJs].filter(id => !inHtml.has(id));
  assert.deepStrictEqual(missing, [], '없는 id: ' + missing.join(', '));
});

test('태그가 짝을 이룬다', () => {
  const VOID = new Set(['area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
    'link', 'meta', 'param', 'source', 'track', 'wbr']);
  const body = SRC.replace(/<script>[\s\S]*?<\/script>/g, '').replace(/<style>[\s\S]*?<\/style>/g, '')
                  .replace(/<!--[\s\S]*?-->/g, '');
  const stack = [];
  for (const m of body.matchAll(/<(\/?)([a-zA-Z][a-zA-Z0-9]*)\b[^>]*?(\/?)>/g)) {
    const [, close, tag, self] = m;
    if (VOID.has(tag.toLowerCase()) || self) continue;
    if (close) {
      assert.ok(stack.length, `</${tag}> 의 짝이 없습니다`);
      const top = stack.pop();
      assert.strictEqual(top, tag, `</${tag}> 인데 열려 있는 건 <${top}>`);
    } else stack.push(tag);
  }
  assert.deepStrictEqual(stack, [], '닫히지 않은 태그: ' + stack.join(', '));
});

// 마크업 전체(HTML + JS 템플릿 문자열)에서 <태그 ... class="..."> 를 모은다
function classUsage() {
  const use = new Map();   // class -> Set(tag)
  for (const m of SRC.matchAll(/<([a-zA-Z][a-zA-Z0-9]*)\b[^>]*?class="([^"]*)"/g)) {
    const tag = m[1].toLowerCase();
    for (const c of m[2].split(/\s+/)) {
      if (!c || c.includes('$') || c.includes('{')) continue;   // class="${...}" 조각은 건너뛴다
      if (!use.has(c)) use.set(c, new Set());
      use.get(c).add(tag);
    }
  }
  return use;
}

// CSS 규칙에서 각 클래스가 선언하는 속성을 모은다
function classDecls() {
  const css = SRC.match(/<style>([\s\S]*?)<\/style>/)[1];
  const decl = new Map();
  for (const rule of css.matchAll(/([^{}]+)\{([^{}]*)\}/g)) {
    const props = [...rule[2].matchAll(/([a-z-]+)\s*:/g)].map(x => x[1]);
    for (const c of [...rule[1].matchAll(/\.([\w가-힣-]+)/g)].map(x => x[1])) {
      if (!decl.has(c)) decl.set(c, new Set());
      props.forEach(p => decl.get(c).add(p));
    }
  }
  return decl;
}

test('한 클래스를 성격이 다른 요소에 겹쳐 쓰지 않는다', () => {
  // `.mark` 를 판정 배지와 카드 수식어 양쪽에 쓴 적이 있다.
  // 배지의 display:inline-flex 와 white-space:nowrap 이 카드에 먹어 레이아웃이 통째로 무너졌다.
  const KIND = (tag) =>
    /^(span|button|a|input|select|textarea|label|b|i|strong|em)$/.test(tag) ? '인라인'
    : /^(h1|h2|h3|h4|p)$/.test(tag) ? '텍스트'
    : '구조';
  const offenders = [];
  for (const [cls, tags] of classUsage()) {
    const kinds = new Set([...tags].map(KIND));
    if (kinds.size > 1) offenders.push(`${cls} → ${[...tags].sort().join(', ')}`);
  }
  assert.deepStrictEqual(offenders, [], '성격이 다른 요소에 겹쳐 쓴 클래스:\n  ' + offenders.join('\n  '));
});

test('한 요소에 display 를 정하는 클래스가 둘 이상 붙지 않는다', () => {
  const decl = classDecls();
  const offenders = [];
  for (const m of SRC.matchAll(/<([a-zA-Z][a-zA-Z0-9]*)\b[^>]*?class="([^"]*)"/g)) {
    const cs = m[2].split(/\s+/).filter(c => c && !c.includes('$') && !c.includes('{'));
    const hit = cs.filter(c => decl.get(c)?.has('display'));
    if (hit.length > 1) offenders.push(`<${m[1]} class="${cs.join(' ')}"> → ${hit.join(', ')}`);
  }
  assert.deepStrictEqual(offenders, [], '레이아웃이 서로 덮어쓰는 조합:\n  ' + offenders.join('\n  '));
});

test('flex 축약형으로 기준 폭을 0으로 만들지 않는다', () => {
  // `flex: 0` 은 grow:0 shrink:1 basis:0 이다. 기준 폭이 0인데 늘어나지도 않으니
  // min-width 바닥까지 없으면 요소가 패딩만 남게 눌리고, 한글은 한 글자씩 쪼개진다.
  // 버튼을 그렇게 눌러 "직무 저장"이 네 줄로 쪼개진 적이 있다. 쓰려면 `flex: 0 0 auto`.
  const hits = [...SRC.matchAll(/flex\s*:\s*0\s*(?=[;"}])/g)].map(m => {
    const line = SRC.slice(0, m.index).split('\n').length;
    return `${line}행: ${SRC.slice(m.index, m.index + 40).split('\n')[0]}`;
  });
  assert.deepStrictEqual(hits, [], 'flex: 0 0 auto 로 바꾸세요:\n  ' + hits.join('\n  '));
});

test('SheetJS를 취약점이 고쳐진 배포처·버전에서 받는다', () => {
  // 0.19.2 이하는 CVE-2023-30533(프로토타입 오염) 영향 범위이고,
  // 패치본은 npm·cdnjs가 아니라 cdn.sheetjs.com 에만 있다.
  const m = SRC.match(/https:\/\/cdn\.sheetjs\.com\/xlsx-(\d+)\.(\d+)\.(\d+)\//);
  assert.ok(m, 'SheetJS를 cdn.sheetjs.com 에서 받아야 합니다');
  const [, maj, min, pat] = m.map(Number);
  const ok = maj > 0 || min > 20 || (min === 20 && pat >= 2);
  assert.ok(ok, `0.20.2 이상이어야 합니다 (현재 ${maj}.${min}.${pat})`);
  assert.ok(!/cdnjs\.cloudflare\.com\/ajax\/libs\/xlsx/.test(SRC), 'cdnjs 경로가 남아 있습니다');
});

console.log(`\n${n}건 통과\n`);
