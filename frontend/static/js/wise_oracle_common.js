/* ============================================================
   Wise Oracle 英文站共享 JS（W7.2）
   职责：
   1. 错误码 → 英文用户消息映射（前端兜底，与后端 error_codes.py 对齐）
   2. JSON fetch 封装（统一解析 success/error 结构）
   3. DOM 辅助（createElement、setStatus）
   4. SSE 流读取辅助（与中文 lunming.js 的手动读取模式对齐，支持 POST）

   设计原则：单一职责、纯函数、不依赖中文 i18n.js
   暴露：window.WiseOracle 命名空间
   ============================================================ */

(function () {
    'use strict';

    /**
     * 错误码 → 英文用户消息映射。
     * 与后端 error_codes.py MESSAGES_EN 对齐；前端兜底用，
     * 优先使用后端返回的 error.message，仅在后端缺失时回退到此映射。
     */
    const ERROR_MESSAGES = {
        INVALID_JSON: 'The request could not be understood. Please try again.',
        INVALID_INPUT: 'Some fields were missing or invalid. Please check and try again.',
        INVALID_ORACLE_MODE: 'Invalid input mode. Please choose three words or three numbers.',
        ORACLE_WORDS_INSUFFICIENT: 'Please enter exactly three words, each containing at least one letter.',
        INVALID_ORACLE_NUMBER: 'Each number must be a whole number between 0 and 999.',
        ORACLE_NUMBERS_ALL_ZERO: 'The three numbers cannot all be zero. Please enter at least one non-zero number.',
        CONTENT_NOT_FOUND: 'This oracle sign could not be loaded. Please try again later.',
        INVALID_BIRTH_DATA: 'The birth data provided was invalid. Please check and try again.',
        MODEL_NOT_CONFIGURED: 'The analysis service is not configured. Please contact support.',
        ANALYSIS_FAILED: 'The analysis service is temporarily unavailable. Please try again later.',
        AI_DAILY_QUOTA_EXHAUSTED: 'Your daily free analysis quota has been used up. Please try again tomorrow.',
        AI_GLOBAL_QUOTA_EXHAUSTED: 'The analysis service quota has been exhausted today. Please try again tomorrow.',
        AI_RATE_LIMITED: 'Too many requests. Please slow down and try again shortly.',
        AI_CONCURRENCY_LIMITED: 'The analysis service is busy. Please try again shortly.',
        NOT_READY: 'The service is not ready yet. Please try again later.',
        NOT_FOUND: 'The requested resource does not exist.',
        PAYLOAD_TOO_LARGE: 'The request was too large. Please simplify your input.'
    };

    /**
     * 按错误码取英文消息。
     * 输入：code（错误码字符串）
     * 输出：英文消息；未知 code 返回通用兜底。
     */
    function messageForCode(code) {
        return ERROR_MESSAGES[code] || 'Something went wrong. Please try again.';
    }

    /**
     * 从后端响应中提取错误消息。
     * 优先用后端 error.message，否则按 error.code 查映射，最后通用兜底。
     * 输入：parsed JSON 对象（{success:false, error:{code, message}}）
     * 输出：英文消息字符串
     */
    function extractErrorMessage(body) {
        if (!body || !body.error) return 'Something went wrong. Please try again.';
        if (body.error.message) return body.error.message;
        return messageForCode(body.error.code);
    }

    /**
     * POST JSON 请求封装。
     * 输入：url, payload（对象）, options（{signal} 可选）
     * 输出：{ok: true, data} 或 {ok: false, message, code, status}
     */
    async function postJSON(url, payload, options) {
        const opts = options || {};
        let response;
        try {
            response = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
                body: JSON.stringify(payload),
                signal: opts.signal
            });
        } catch (err) {
            if (err.name === 'AbortError') return { ok: false, aborted: true };
            return { ok: false, message: 'Network error. Please check your connection and try again.' };
        }

        const body = await response.json().catch(() => ({}));
        if (response.ok && body && body.success) {
            return { ok: true, data: body.data };
        }
        return {
            ok: false,
            status: response.status,
            code: body && body.error ? body.error.code : null,
            message: extractErrorMessage(body)
        };
    }

    /**
     * 创建 DOM 元素并可选设置类名与文本。
     * 输入：tag, className（可选）, text（可选）
     * 输出：HTMLElement
     */
    function el(tag, className, text) {
        const node = document.createElement(tag);
        if (className) node.className = className;
        if (text !== undefined) node.textContent = text;
        return node;
    }

    /**
     * 设置表单状态文本。
     * 输入：statusEl（HTMLElement）, message（字符串）, type（'' | 'error' | 'success'）
     */
    function setStatus(statusEl, message, type) {
        if (!statusEl) return;
        const statusType = type || '';
        const statusMessage = message || '';
        statusEl.textContent = statusType === 'error' && statusMessage
            ? `Error: ${statusMessage}`
            : statusMessage;
        statusEl.dataset.type = type || '';
        statusEl.setAttribute('role', statusType === 'error' ? 'alert' : 'status');
    }

    /**
     * SSE 流读取器（支持 POST body，EventSource 不支持 POST 故手动读取）。
     * 与中文 lunming.js readStream 模式对齐。
     * 输入：response（fetch 返回的 Response）, onEvent（event 对象回调）
     * 输出：Promise<void>，正常结束 resolve，异常 reject
     */
    async function readSSE(response, onEvent) {
        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let buffer = '';
        while (true) {
            const { value, done } = await reader.read();
            buffer += decoder.decode(value || new Uint8Array(), { stream: !done });
            const blocks = buffer.split(/\r?\n\r?\n/);
            buffer = blocks.pop() || '';
            for (const block of blocks) {
                const data = block.split('\n')
                    .filter(line => line.startsWith('data:'))
                    .map(line => line.slice(5).trim())
                    .join('\n');
                if (!data) continue;
                let event;
                try {
                    event = JSON.parse(data);
                } catch {
                    continue;
                }
                onEvent(event);
            }
            if (done) break;
        }
    }

    // 暴露命名空间
    window.WiseOracle = {
        messageForCode,
        extractErrorMessage,
        postJSON,
        readSSE,
        el,
        setStatus
    };
})();
