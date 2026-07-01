/* ============================================================
   Wise Oracle — Ask the Oracle 页面逻辑（W7.4）
   职责：
   1. Three Words / Three Numbers 模式切换
   2. 客户端校验（词数/字母、数字范围/全零）
   3. POST /api/en/oracle/ask 调用
   4. Three Words 变换动画（LOVE→54→4，逐行淡入）
   5. 9 字段渲染（sign_number/sign_text/interpretation1/career/wealth/love/health/study/general）
   6. responsible-use 文案展示
   7. "Draw Another Sign" 重启按钮
   8. 错误码 → 英文消息映射（经 WiseOracle 共享模块）

   依据：执行计划 W7.4、D13/D14（9 字段契约，无 fortune/gua_type）
   不复用中文 /calculate_sign 前端交互
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {
    const WO = window.WiseOracle;

    const els = {
        tabs: document.querySelectorAll('.en-mode-tab'),
        panels: document.querySelectorAll('.en-oracle-mode-panel'),
        form: document.getElementById('oracle-form'),
        submit: document.getElementById('oracle-submit'),
        status: document.getElementById('oracle-status'),
        transform: document.getElementById('oracle-transform'),
        result: document.getElementById('oracle-result')
    };

    let currentMode = 'words';

    // ============================================================
    // 模式切换
    // ============================================================

    function activateTab(tab, moveFocus = false) {
            const mode = tab.dataset.mode;
            currentMode = mode;
            els.tabs.forEach(t => {
                const active = t === tab;
                t.classList.toggle('is-active', active);
                t.setAttribute('aria-selected', active ? 'true' : 'false');
                t.tabIndex = active ? 0 : -1;
            });
            els.panels.forEach(p => {
                const active = p.dataset.panel === mode;
                p.classList.toggle('is-active', active);
                p.hidden = !active;
            });
            WO.setStatus(els.status, '');
            if (moveFocus) tab.focus();
    }

    els.tabs.forEach((tab, index) => {
        tab.addEventListener('click', () => activateTab(tab));
        tab.addEventListener('keydown', event => {
            const keys = ['ArrowLeft', 'ArrowRight', 'Home', 'End'];
            if (!keys.includes(event.key)) return;
            event.preventDefault();
            let nextIndex = index;
            if (event.key === 'ArrowLeft') nextIndex = (index - 1 + els.tabs.length) % els.tabs.length;
            if (event.key === 'ArrowRight') nextIndex = (index + 1) % els.tabs.length;
            if (event.key === 'Home') nextIndex = 0;
            if (event.key === 'End') nextIndex = els.tabs.length - 1;
            activateTab(els.tabs[nextIndex], true);
        });
    });

    // ============================================================
    // 校验
    // ============================================================

    /**
     * 校验三词输入。
     * 输出：{ok:true, words:[...]} 或 {ok:false, message}
     */
    function validateWords() {
        const words = [1, 2, 3].map(i => document.getElementById(`word-${i}`).value.trim());
        if (words.some(w => !w)) {
            return { ok: false, message: 'Please fill in all three words.' };
        }
        // 每个词必须至少含一个英文字母（与后端 word_to_letter_sum 一致）
        if (words.some(w => !/[A-Za-z]/.test(w))) {
            return { ok: false, message: 'Each word must contain at least one letter.' };
        }
        return { ok: true, words };
    }

    /**
     * 校验三数字输入。
     * 输出：{ok:true, numbers:[...]} 或 {ok:false, message}
     */
    function validateNumbers() {
        const raw = [1, 2, 3].map(i => document.getElementById(`num-${i}`).value);
        if (raw.some(v => v === '')) {
            return { ok: false, message: 'Please fill in all three numbers.' };
        }
        const numbers = raw.map(v => Number(v));
        if (numbers.some(n => !Number.isInteger(n))) {
            return { ok: false, message: 'Each number must be a whole number.' };
        }
        if (numbers.some(n => n < 0 || n > 999)) {
            return { ok: false, message: 'Each number must be between 0 and 999.' };
        }
        if (numbers.every(n => n === 0)) {
            return { ok: false, message: 'The three numbers cannot all be zero.' };
        }
        return { ok: true, numbers };
    }

    // ============================================================
    // 变换动画（仅 Three Words）
    // ============================================================

    /**
     * 渲染变换动画：word → letter_sum → digit，逐行淡入。
     * 输入：transform 数组 [{word, letter_sum, digit}, ...]
     * 输出：Promise<void>，动画完成后 resolve
     */
    function renderTransform(transform) {
        els.transform.hidden = false;
        els.transform.replaceChildren();
        const heading = WO.el('div', '', 'Each word becomes a digit:');
        heading.style.fontWeight = '600';
        heading.style.marginBottom = '0.5rem';
        heading.style.color = 'var(--wo-ink)';
        els.transform.append(heading);

        const steps = transform.map(item => {
            const step = WO.el('div', 'en-transform-step');
            step.append(
                WO.el('span', 'en-transform-word', item.word),
                WO.el('span', 'en-transform-arrow', '→'),
                WO.el('span', 'en-transform-sum', String(item.letter_sum)),
                WO.el('span', 'en-transform-arrow', '→'),
                WO.el('span', 'en-transform-digit', String(item.digit))
            );
            els.transform.append(step);
            return step;
        });

        // 逐行淡入
        return new Promise(resolve => {
            steps.forEach((step, idx) => {
                setTimeout(() => step.classList.add('is-visible'), idx * 350);
            });
            setTimeout(resolve, steps.length * 350 + 200);
        });
    }

    // ============================================================
    // 结果渲染
    // ============================================================

    const FIELD_LABELS = {
        interpretation1: 'Interpretation',
        career: 'Career',
        wealth: 'Wealth',
        love: 'Love & Relationships',
        health: 'Health',
        study: 'Study & Learning',
        general: 'General Outlook'
    };

    /**
     * 渲染签文结果（9 字段 + responsible_use）。
     * 输入：data 对象 {mode, sign_number, transform?, sign}
     */
    function renderResult(data) {
        const sign = data.sign;
        els.result.replaceChildren();
        if (!sign) {
            const note = WO.el('p', '', 'This sign could not be loaded. Please try again.');
            note.style.color = 'var(--wo-error)';
            els.result.append(note);
            els.result.classList.add('is-visible');
            return;
        }

        // 签号
        els.result.append(WO.el('p', 'en-sign-number', `Sign No. ${sign.sign_number}`));

        // 签文正文
        els.result.append(WO.el('div', 'en-sign-text', sign.sign_text));

        // 解签
        if (sign.interpretation1) {
            els.result.append(buildSection('Interpretation', sign.interpretation1));
        }

        // 六维字段
        ['career', 'wealth', 'love', 'health', 'study', 'general'].forEach(key => {
            if (sign[key]) {
                els.result.append(buildSection(FIELD_LABELS[key], sign[key]));
            }
        });

        // responsible_use（签文自带，可选）
        if (sign.responsible_use) {
            els.result.append(WO.el('div', 'en-responsible-use', sign.responsible_use));
        }

        // 克制赞助/付费墙占位（W7.4.4）
        const support = WO.el('div', 'en-responsible-use');
        support.style.marginTop = '1rem';
        support.style.textAlign = 'center';
        support.style.fontStyle = 'italic';
        support.textContent = 'This reading is free. If it resonated, consider supporting the project.';
        els.result.append(support);

        // Draw Another Sign 重启按钮
        const restart = WO.el('button', 'en-btn en-btn-secondary', 'Draw Another Sign');
        restart.style.marginTop = '1.5rem';
        restart.addEventListener('click', resetForm);
        els.result.append(restart);

        els.result.classList.add('is-visible');
    }

    function buildSection(label, text) {
        const section = WO.el('div', 'en-sign-section');
        section.append(WO.el('h3', '', label), WO.el('p', '', text));
        return section;
    }

    // ============================================================
    // 重启
    // ============================================================

    function resetForm() {
        els.form.reset();
        els.transform.hidden = true;
        els.transform.replaceChildren();
        els.result.replaceChildren();
        els.result.classList.remove('is-visible');
        WO.setStatus(els.status, '');
        // 焦点回到第一个输入
        const firstInput = document.querySelector('.en-oracle-mode-panel.is-active input');
        if (firstInput) firstInput.focus();
    }

    // ============================================================
    // 提交
    // ============================================================

    els.form.addEventListener('submit', async (event) => {
        event.preventDefault();
        WO.setStatus(els.status, '');

        // 校验
        const check = currentMode === 'words' ? validateWords() : validateNumbers();
        if (!check.ok) {
            WO.setStatus(els.status, check.message, 'error');
            return;
        }

        // 准备请求
        const payload = currentMode === 'words'
            ? { mode: 'words', words: check.words }
            : { mode: 'numbers', numbers: check.numbers };

        els.submit.disabled = true;
        els.transform.hidden = true;
        els.transform.replaceChildren();
        els.result.replaceChildren();
        els.result.classList.remove('is-visible');
        WO.setStatus(els.status, 'Drawing your sign…');

        try {
            const result = await WO.postJSON('/api/en/oracle/ask', payload);
            if (!result.ok) {
                WO.setStatus(els.status, result.message, 'error');
                return;
            }

            // Three Words 模式：先播变换动画，再渲染结果
            if (currentMode === 'words' && result.data.transform) {
                WO.setStatus(els.status, 'Forming your numbers…');
                await renderTransform(result.data.transform);
            }

            WO.setStatus(els.status, '', '');
            renderResult(result.data);
        } catch (err) {
            WO.setStatus(els.status, 'Something went wrong. Please try again.', 'error');
        } finally {
            els.submit.disabled = false;
        }
    });
});
