import json

from utils.text_utils import strip_json_fence


def fix_heading_levels(text: str, llm_client, prompt: str, model: str = None) -> str:
    """用 LLM 修正 Markdown 標題層級。

    text: 原始 Markdown 全文
    llm_client: 具備 chat(messages, stream=False) 介面的 LLM client
    prompt: 由呼叫端依文件類型 / 規則建好的完整提示詞
    model: 指定模型；None 時由 llm_client.chat 套用預設（向後相容）

    回傳套用修正後的 Markdown 全文。LLM 呼叫或 JSON 解析失敗時拋出例外，
    由呼叫端自行處理（與合併前各自的 try/except 行為一致）。
    """
    lines = text.split('\n')

    result_text = llm_client.chat(
        [{"role": "user", "content": prompt}], stream=False, model=model
    ).strip()
    result_text = strip_json_fence(result_text)
    heading_map = json.loads(result_text)

    new_lines = lines.copy()
    for line_num_str, hash_count in heading_map.items():
        line_num = int(line_num_str)
        if line_num < len(lines) and lines[line_num].startswith('#'):
            title_text = lines[line_num].lstrip('#').strip()
            new_lines[line_num] = '#' * int(hash_count) + ' ' + title_text

    return '\n'.join(new_lines)
