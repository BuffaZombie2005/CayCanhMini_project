"""Gọi LLM cục bộ qua API Ollama (mặc định http://127.0.0.1:11434/api/chat)."""
import json
import urllib.error
import urllib.request

from django.conf import settings


def chat_with_local_llm(messages):
    """
    messages: danh sách dict Ollama, ví dụ [{"role":"user","content":"..."}].
    Trả về (reply_text, error_message): một trong hai là None khi thành công/lỗi.
    """
    url = getattr(settings, 'LLM_CHAT_API_URL', 'http://127.0.0.1:11434/api/chat')
    model = getattr(settings, 'LLM_MODEL', 'llama3.2')
    timeout = getattr(settings, 'LLM_CHAT_TIMEOUT', 120)

    payload = {
        'model': model,
        'messages': messages,
        'stream': False,
    }
    body = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        url,
        data=body,
        headers={'Content-Type': 'application/json'},
        method='POST',
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        detail = ''
        try:
            detail = e.read().decode('utf-8', errors='replace')[:500]
        except Exception:
            pass
        return None, f'Máy chủ LLM trả về lỗi ({e.code}). {detail}'
    except urllib.error.URLError as e:
        return None, (
            'Không kết nối được tới máy chủ LLM cục bộ. '
            'Hãy chạy Ollama và tải model (ví dụ: `ollama run llama3.2`). '
            f'Chi tiết: {e.reason}'
        )
    except TimeoutError:
        return None, 'Hết thời gian chờ phản hồi từ model.'

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None, 'Phản hồi không phải JSON hợp lệ từ máy chủ LLM.'

    msg = data.get('message') or {}
    content = msg.get('content')
    if not content:
        return None, 'Model không trả về nội dung (kiểm tra tên model và log Ollama).'
    return str(content).strip(), None
