/* ============================================================
   Wise Oracle — Ask the Oracle 页面逻辑（W7.4）
   职责：
   1. Three Words / Three Numbers 模式切换
   2. 客户端校验（词数/字母、数字范围/全零）
   3. POST /api/en/oracle/ask 调用
   4. Three Words 变换动画（LOVE→54→4，逐行淡入）
   5. 4 阶段分步揭示 + 打字机效果：
      阶段1 签号 → 阶段2 签文（打字机）→ 阶段3 解读（打字机）→ 阶段4 分项选择（打字机）
   6. responsible-use 文案展示
   7. "Draw Another Sign" 重启按钮
   8. 错误码 → 英文消息映射（经 WiseOracle 共享模块）

   依据：执行计划 W7.4、D13/D14（9 字段契约，无 fortune/gua_type）
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
        result: document.getElementById('oracle-result'),
        // 4 个阶段容器
        stageSignNumber: document.getElementById('stage-sign-number'),
        stageSignText: document.getElementById('stage-sign-text'),
        stageInterpretation: document.getElementById('stage-interpretation'),
        stageAreaSelect: document.getElementById('stage-area-select'),
        // 阶段内容元素
        resultSignNumber: document.getElementById('result-sign-number'),
        resultSignText: document.getElementById('result-sign-text'),
        resultInterpretation: document.getElementById('result-interpretation'),
        // 阶段切换按钮
        btnRevealSignText: document.getElementById('btn-reveal-sign-text'),
        btnRevealInterpretation: document.getElementById('btn-reveal-interpretation'),
        btnChooseArea: document.getElementById('btn-choose-area'),
        btnRestart: document.getElementById('btn-restart'),
        // 分项选择
        areaButtons: document.getElementById('area-buttons'),
        areaResult: document.getElementById('area-result'),
        areaTitle: document.getElementById('area-title'),
        areaText: document.getElementById('area-text'),
        responsibleUse: document.getElementById('responsible-use'),
        supportNote: document.getElementById('support-note')
    };

    let currentMode = 'words';
    let currentSignData = null;  // 保存当前签文数据，供分阶段揭示使用

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
    // 打字机效果
    // ============================================================

    /**
     * 分块逐字渲染文本（打字机效果）。
     * 输入：
     *   element — 目标 DOM 元素
     *   text    — 待渲染文本
     *   chunkSize — 每次渲染字符数（英文 4 字符/组）
     *   interval  — 每次渲染间隔毫秒（50ms）
     * 特性：
     *   - 尊重 prefers-reduced-motion：开启时立即显示全文
     *   - 自动滚动跟随：每 30 字符检查一次视口
     */
    async function typeWriter(element, text, chunkSize = 4, interval = 50) {
        const characters = Array.from(text || '');
        element.textContent = '';

        if (!characters.length) return;
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            element.textContent = characters.join('');
            return;
        }

        for (let end = chunkSize; end < characters.length; end += chunkSize) {
            element.textContent = characters.slice(0, end).join('');

            // 每 30 字符检查一次是否需要滚动
            if (end % (chunkSize * 6) === 0) {
                const elementRect = element.getBoundingClientRect();
                if (elementRect.bottom > window.innerHeight - 80) {
                    window.scrollBy({
                        top: Math.min(elementRect.bottom - window.innerHeight + 100, 240),
                        behavior: 'smooth'
                    });
                }
            }

            await new Promise(resolve => setTimeout(resolve, interval));
        }

        element.textContent = characters.join('');
    }

    /**
     * 平滑滚动元素进入视口。
     * 输入：element — 需要可见的 DOM 元素
     */
    function scrollIntoView(element) {
        const rect = element.getBoundingClientRect();
        if (rect.bottom > window.innerHeight) {
            window.scrollBy({
                top: rect.bottom - window.innerHeight + 50,
                behavior: 'smooth'
            });
        }
    }

    // ============================================================
    // 分阶段结果渲染
    // ============================================================

    const FIELD_LABELS = {
        career: 'Career',
        wealth: 'Wealth',
        love: 'Love & Relationships',
        health: 'Health',
        study: 'Study & Learning',
        general: 'General Outlook'
    };

    /**
     * 隐藏所有阶段容器。
     */
    function hideAllStages() {
        [els.stageSignNumber, els.stageSignText,
         els.stageInterpretation, els.stageAreaSelect].forEach(s => {
            s.hidden = true;
        });
    }

    /**
     * 启动分阶段结果渲染。
     * 保存签文数据，显示阶段 1（签号）。
     * 输入：data 对象 {mode, sign_number, transform?, sign}
     */
    function renderResult(data) {
        const sign = data.sign;
        els.result.classList.add('is-visible');

        if (!sign) {
            // 错误情况：直接在结果区显示提示
            hideAllStages();
            const note = WO.el('p', '', 'This sign could not be loaded. Please try again.');
            note.style.color = 'var(--wo-error)';
            els.result.append(note);
            return;
        }

        currentSignData = sign;
        hideAllStages();

        // 阶段 1：显示签号
        els.resultSignNumber.textContent = `Sign No. ${sign.sign_number}`;
        els.stageSignNumber.hidden = false;
        els.resultSignNumber.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    // ============================================================
    // 阶段切换事件
    // ============================================================

    // 阶段 1 → 2：点击"Reveal the Sign Text"
    els.btnRevealSignText.addEventListener('click', async () => {
        els.stageSignNumber.hidden = true;
        els.stageSignText.hidden = false;

        // 打字机渲染签文
        await typeWriter(els.resultSignText, currentSignData.sign_text);

        // 显示"下一步"按钮并滚动到可见位置
        els.btnRevealInterpretation.hidden = false;
        await new Promise(resolve => setTimeout(resolve, 100));
        scrollIntoView(els.btnRevealInterpretation);
    });

    // 阶段 2 → 3：点击"Reveal the Interpretation"
    els.btnRevealInterpretation.addEventListener('click', async () => {
        els.stageSignText.hidden = true;
        els.stageInterpretation.hidden = false;

        // 打字机渲染整体解读
        await typeWriter(els.resultInterpretation, currentSignData.interpretation1 || '');

        // 显示"下一步"按钮并滚动到可见位置
        els.btnChooseArea.hidden = false;
        await new Promise(resolve => setTimeout(resolve, 100));
        scrollIntoView(els.btnChooseArea);
    });

    // 阶段 3 → 4：点击"Choose an Area to Explore"
    els.btnChooseArea.addEventListener('click', () => {
        els.stageInterpretation.hidden = true;
        els.stageAreaSelect.hidden = false;

        // 显示 responsible_use 和赞助文案（如有）
        if (currentSignData.responsible_use) {
            els.responsibleUse.textContent = currentSignData.responsible_use;
            els.responsibleUse.hidden = false;
        }
        els.supportNote.hidden = false;

        // 重置分项选择状态
        els.areaResult.hidden = true;
        els.areaText.textContent = '';
        document.querySelectorAll('.en-area-btn').forEach(b => b.classList.remove('selected'));

        // 滚动到分项选择区域
        els.areaButtons.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });

    // 阶段 4：分项选择按钮点击
    document.querySelectorAll('.en-area-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            const area = btn.dataset.area;
            const text = currentSignData[area];

            // 切换选中状态
            document.querySelectorAll('.en-area-btn').forEach(b => b.classList.remove('selected'));
            btn.classList.add('selected');

            if (!text) return;

            // 显示分项结果
            els.areaResult.hidden = false;
            els.areaTitle.textContent = FIELD_LABELS[area] || area;

            // 打字机渲染分项内容
            await typeWriter(els.areaText, text);

            // 滚动到结果
            await new Promise(resolve => setTimeout(resolve, 100));
            scrollIntoView(els.areaResult);
        });
    });

    // 重启按钮
    els.btnRestart.addEventListener('click', resetForm);

    // ============================================================
    // 重启
    // ============================================================

    function resetForm() {
        els.form.reset();
        els.transform.hidden = true;
        els.transform.replaceChildren();

        // 隐藏所有阶段
        hideAllStages();
        els.result.classList.remove('is-visible');

        // 清空内容
        els.resultSignNumber.textContent = '';
        els.resultSignText.textContent = '';
        els.resultInterpretation.textContent = '';
        els.areaText.textContent = '';
        els.areaResult.hidden = true;
        els.responsibleUse.hidden = true;
        els.responsibleUse.textContent = '';
        els.supportNote.hidden = true;

        // 重置分项按钮选中状态
        document.querySelectorAll('.en-area-btn').forEach(b => b.classList.remove('selected'));

        // 重置阶段切换按钮为隐藏（打字机完成后才显示）
        els.btnRevealInterpretation.hidden = true;
        els.btnChooseArea.hidden = true;

        currentSignData = null;
        WO.setStatus(els.status, '');

        // 焦点回到第一个输入
        const firstInput = document.querySelector('.en-oracle-mode-panel.is-active input');
        if (firstInput) firstInput.focus();

        // 滚动回页面顶部
        window.scrollTo({ top: 0, behavior: 'smooth' });
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
        hideAllStages();
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
