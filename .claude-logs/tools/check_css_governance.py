#!/usr/bin/env python3
"""check_css_governance.py — MadPro CSS 契約常駐檢查（THEME-DEDUP C4）

四類確定性檢查（規格源：design/docs/theme-guide.md 凍結規格 + css-architecture.md）：
  ① unlayered 鐵律：主檔系（static/css/ 除 print.css）頂層規則必在 @layer 內；
     print.css 與 static/themes/*.css 嚴禁 @layer。
  ② token 唯一定義：所有 --token 定義唯一落於 static/css/globals.css（主檔系其餘檔零定義、
     globals 內零重複）；主題 :root 覆寫不在此限。
  ③ 主題凍結骨架：static/themes/*.css + design/docs/theme-template.css 各須——
     26 必備 token 不多不少 / 16 必備選擇器全在（含 .ph::before 空槽）/
     進階 chrome 覆寫層 marker 在 / 16 必備選擇器之屬性 ⊆ 白名單 ∪ 例外表
     （例外表＝theme-guide §11.3 遺留登記 + §4 Q3 排版例外·本檔內嵌）/
     非必備選擇器（chrome 覆寫）必須出現在 marker 之後。
  ④ 死碼：主題與模板無 #demo-bar 系選擇器。

用法：
  python3 .claude-logs/tools/check_css_governance.py            # 全量（主檔系+9 主題+模板）
  python3 .claude-logs/tools/check_css_governance.py --file X   # 單檔主題模式（③④+@layer）
退出碼：0＝全綠；1＝有違規（stdout 列違規清單）。純標準庫（re/sys/pathlib/json）。
"""
import re
import sys
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]          # .claude-logs/tools/ → 專案根
CSS_DIR = ROOT / 'static' / 'css'
THEMES_DIR = ROOT / 'static' / 'themes'
TEMPLATE = ROOT / 'design' / 'docs' / 'theme-template.css'
MAIN_SHEETS = ['globals', 'layout', 'sidebar', 'content', 'chat', 'overlays']  # print 除外

REQ_TOKENS = {
    '--color-bg', '--color-bg-served', '--color-surface', '--color-surface-2',
    '--color-border', '--color-border-strong', '--color-divider', '--color-text',
    '--color-text-muted', '--color-text-subtle', '--color-accent', '--color-accent-hover',
    '--color-danger', '--divider-w', '--radius-sm', '--radius-md', '--content-max-w',
    '--pc-pad', '--figure-margin-y', '--byline-margin-b', '--byline-pad-b',
    '--byline-border-w', '--figcaption-margin-t', '--ph-border-w',
    '--font-display', '--font-body',
}  # 26

REQ_SELECTORS = [
    'body', '.display-font', '#content-area', '#content-toolbar h2',
    '#sidebar h1 .title, #chat-header > .h-title',
    '#paper-content', '#paper-content h1', '#paper-content h2', '#paper-content h3',
    '#paper-content p', '#paper-content em', '#paper-content .byline',
    '#paper-content .figure', '#paper-content .figure .ph',
    '#paper-content .figure figcaption',
    '#paper-content .figure .ph::before',
]  # 16

WHITELIST = {
    'color', 'background', 'background-color', 'background-image', 'border-color',
    'box-shadow', 'font-family', 'font-size', 'font-weight', 'font-style',
    'letter-spacing', 'text-transform', 'line-height', 'text-align', 'content',
}
PH_BEFORE_GEOM = {'position', 'top', 'left', 'right', 'bottom', 'width', 'height',
                  'transform', 'pointer-events'}  # 裝飾幾何層允許（theme-guide §5-A）
CHROME_MARKER = '進階 chrome 覆寫層'

# 例外表（theme-guide §4 Q3 排版例外 + §11.3 遺留登記·唯一登記源在該文件、此處為機器鏡像）
_RHYTHM = {('#paper-content h1', 'margin-bottom'), ('#paper-content h2', 'margin'),
           ('#paper-content h3', 'margin'), ('#paper-content p', 'margin-bottom')}
_FIGCAP = {('#paper-content .figure figcaption', 'max-width'),
           ('#paper-content .figure figcaption', 'margin-inline')}
EXCEPTIONS = {
    'kahn': _FIGCAP | {('#paper-content .figure .ph', 'position')},
    'kandinsky': set(),
    'mies': {('#paper-content .figure figcaption', 'max-width')},
    'nara': set(),
    'apple': _RHYTHM | {('#paper-content .figure .ph', 'border-radius')},
    'google': _RHYTHM | {('#paper-content .figure .ph', 'border-radius')},
    'corbusier': _RHYTHM | _FIGCAP,
    'fuller': _RHYTHM | _FIGCAP | {('#paper-content h2', 'border-bottom'),
                                   ('#paper-content .byline', 'border-bottom'),
                                   ('body', 'font-feature-settings')},
    'gropius': _RHYTHM | _FIGCAP,
    'theme-template': set(),
}

def strip_comments(txt):
    return re.sub(r'/\*.*?\*/', '', txt, flags=re.S)

def parse_rules(txt):
    """回傳 [(selector, {prop: value}, start_pos)]（頂層與巢內一併攤平；@ 規則跳過）。"""
    rules = []
    for m in re.finditer(r'([^{};]+)\{([^{}]*)\}', txt):
        sel = ' '.join(m.group(1).split())
        if not sel or sel.startswith('@'):
            continue
        props = {}
        for d in m.group(2).split(';'):
            if ':' in d:
                p, v = d.split(':', 1)
                props[p.strip()] = ' '.join(v.split())
        rules.append((sel, props, m.start()))
    return rules

def check_main_sheet_layered(path):
    """① 主檔系：頂層只允許 @layer 宣告/@layer 塊/@media 塊；其餘頂層規則＝unlayered 違規。"""
    v = []
    txt = strip_comments(path.read_text())
    txt = re.sub(r'^@import.*$', '', txt, flags=re.M)
    i, depth, n = 0, 0, len(txt)
    buf = ''
    while i < n:
        c = txt[i]
        if c == '{':
            head = ' '.join(buf.split())
            if depth == 0 and not head.startswith(('@layer', '@media', '@supports', '@font-face')):
                v.append(f'{path.name}: 頂層 unlayered 規則「{head[:60]}」')
            depth += 1
            buf = ''
        elif c == '}':
            depth -= 1
            buf = ''
        elif c == ';':
            buf = ''
        else:
            buf += c
        i += 1
    return v

def check_theme(path):
    """③④ + @layer：單一主題/模板之凍結骨架合規。"""
    v = []
    name = path.stem
    raw = path.read_text()
    txt = strip_comments(raw)
    if re.search(r'@layer', txt):
        v.append(f'{name}: 主題含 @layer（必 unlayered）')
    if '#demo-bar' in txt:
        v.append(f'{name}: #demo-bar 死碼殘留')
    rules = parse_rules(re.sub(r'^@import.*$', '', txt, flags=re.M))
    sel_map = {}
    for sel, props, pos in rules:
        sel_map.setdefault(sel, ({}, pos))[0].update(props)
    # 26 token 不多不少
    root = sel_map.get(':root', ({}, 0))[0]
    toks = {p for p in root if p.startswith('--')}
    if toks != REQ_TOKENS:
        miss, extra = REQ_TOKENS - toks, toks - REQ_TOKENS
        if miss:
            v.append(f'{name}: 缺必備 token {sorted(miss)}')
        if extra:
            v.append(f'{name}: 非規格 token {sorted(extra)}')
    # 16 選擇器
    for s in REQ_SELECTORS:
        if s not in sel_map:
            v.append(f'{name}: 缺必備選擇器「{s}」')
    # chrome marker
    mpos = raw.find(CHROME_MARKER)
    if mpos < 0:
        v.append(f'{name}: 缺進階 chrome 覆寫層 marker')
    # 屬性白名單（僅驗 16 必備選擇器；::before 加幾何集；例外表放行）
    exc = EXCEPTIONS.get(name, set())
    for s in REQ_SELECTORS:
        props = sel_map.get(s, ({}, 0))[0]
        allowed = WHITELIST | (PH_BEFORE_GEOM if s.endswith('::before') else set())
        for p in props:
            if p.startswith('--') or p in allowed or (s, p) in exc:
                continue
            v.append(f'{name}: {s} 用非白名單屬性「{p}」（未登記例外）')
    # 非必備選擇器（chrome 覆寫）必在 marker 後
    if mpos >= 0:
        m_stripped = strip_comments(raw[:mpos])
        cut = len(re.sub(r'^@import.*$', '', m_stripped, flags=re.M))
        for sel, (_, pos) in sel_map.items():
            if sel == ':root' or sel in REQ_SELECTORS:
                continue
            if pos < cut - 50:  # 容差：marker 前不得有 chrome 規則
                v.append(f'{name}: 非必備選擇器「{sel[:50]}」出現在 chrome marker 之前')
    return v

def main(argv):
    violations = []
    if len(argv) >= 2 and argv[0] == '--file':
        violations += check_theme(Path(argv[1]))
        scope = f'單檔 {argv[1]}'
    else:
        # ① 主檔系 layered + print/themes 無 @layer
        for f in MAIN_SHEETS:
            violations += check_main_sheet_layered(CSS_DIR / f'{f}.css')
        for p in [CSS_DIR / 'print.css'] + sorted(THEMES_DIR.glob('*.css')):
            if re.search(r'@layer', strip_comments(p.read_text())):
                violations.append(f'{p.name}: 含 @layer（print/themes 必 unlayered）')
        # ② token 唯一定義於 globals
        gdefs = re.findall(r'^\s*(--[\w-]+)\s*:', strip_comments((CSS_DIR / 'globals.css').read_text()), re.M)
        dup = {t for t in gdefs if gdefs.count(t) > 1}
        if dup:
            violations.append(f'globals.css: token 重複定義 {sorted(dup)}')
        for f in MAIN_SHEETS[1:] + ['print']:
            hits = re.findall(r'^\s*--[\w-]+\s*:', strip_comments((CSS_DIR / f'{f}.css').read_text()), re.M)
            if hits:
                violations.append(f'{f}.css: token 定義散落主檔（{len(hits)} 條·唯一定義處應為 globals）')
        # ③④ 9 主題 + 模板
        for p in sorted(THEMES_DIR.glob('*.css')) + [TEMPLATE]:
            violations += check_theme(p)
        scope = f'全量（主檔系 {len(MAIN_SHEETS)+1} + 主題 {len(list(THEMES_DIR.glob("*.css")))} + 模板 1）'

    if violations:
        print(f'❌ CSS 契約檢查未過（{scope}）——{len(violations)} 條違規：')
        for x in violations:
            print('  -', x)
        return 1
    print(f'✅ CSS 契約檢查全綠（{scope}）：unlayered 鐵律 / token 唯一定義 / 凍結骨架（26 token·16 選擇器·2 槽·白名單+例外表）/ 死碼=0')
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
