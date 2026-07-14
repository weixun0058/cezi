/* ============================================================
   Wise Oracle — Birth Chart Reading 页面逻辑（W7.6）
   职责：
   1. 表单交互（birth_time_unknown checkbox 联动 birth_time）
   2. 客户端校验
   3. POST /api/en/birth-chart/stream SSE 流消费
      事件序列：chart → report → responsible_use → done（异常时 error）
   4. 渲染：四柱 + 基础事实 + 五行分布 → AI 报告 → responsible-use
   5. 错误码 → 英文消息映射（经 WiseOracle 共享模块）

   依据：执行计划 W7.6、W0.3 AI prompt 边界、变更日志 0.12（stream 用 POST）
   不出现 fate guarantee / accurate prediction / pay to change your destiny
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {
    const WO = window.WiseOracle;

    const els = {
        form: document.getElementById('birth-chart-form'),
        submit: document.getElementById('bc-submit'),
        status: document.getElementById('bc-status'),
        loading: document.getElementById('bc-loading'),
        result: document.getElementById('bc-result'),
        timeUnknown: document.getElementById('bc-time-unknown'),
        timeInput: document.getElementById('bc-time')
    };

    let activeController = null;

    // ============================================================
    // birth_time_unknown 联动
    // ============================================================

    function syncTimeUnknown() {
        const unknown = els.timeUnknown.checked;
        els.timeInput.disabled = unknown;
        if (unknown) els.timeInput.value = '';
        syncFilled(els.timeInput);
    }

    // ============================================================
    // date/time 原生控件中文占位覆盖：有值时切 is-filled 显示值
    // ============================================================
    const dateInput = document.getElementById('bc-date');
    function syncFilled(input) {
        if (input.value) {
            input.classList.add('is-filled');
        } else {
            input.classList.remove('is-filled');
        }
    }
    [dateInput, els.timeInput].forEach(input => {
        input.addEventListener('input', () => syncFilled(input));
        input.addEventListener('change', () => syncFilled(input));
    });

    els.timeUnknown.addEventListener('change', syncTimeUnknown);
    syncTimeUnknown();
    syncFilled(dateInput);

    // ============================================================
    // 校验与 payload
    // ============================================================

    function getPayload() {
        const payload = {
            name: document.getElementById('bc-name').value.trim(),
            gender: document.querySelector('input[name="bc-gender"]:checked').value,
            birth_date: document.getElementById('bc-date').value,
            birth_time: els.timeInput.value || null,
            birth_time_unknown: els.timeUnknown.checked
        };
        const tz = document.getElementById('bc-timezone').value.trim();
        if (tz) payload.timezone = tz;
        return payload;
    }

    function validate(payload) {
        if (!payload.name) return 'Please enter a name or nickname.';
        if (payload.name.length > 30) return 'Name must be 30 characters or fewer.';
        if (!payload.birth_date) return 'Please enter your birth date.';
        if (!payload.birth_time_unknown && !payload.birth_time) {
            return 'Please enter your birth time, or check "I don\'t know my birth time".';
        }
        return '';
    }

    // ============================================================
    // 渲染：基础盘（chart 事件）
    // ============================================================

    function renderChart(event) {
        const cs = event.chart_summary || {};
        // 四柱
        const pillars = [
            ['Year', cs.year_pillar],
            ['Month', cs.month_pillar],
            ['Day', cs.day_pillar],
            ['Time', cs.time_pillar]
        ];

        const pillarsGrid = WO.el('div', 'en-bc-pillars');
        pillars.forEach(([label, value]) => {
            const item = WO.el('div', 'en-bc-pillar');
            item.append(
                WO.el('div', 'en-bc-pillar-label', label),
                WO.el('div', 'en-bc-pillar-value', value || '—')
            );
            pillarsGrid.append(item);
        });
        els.result.append(WO.el('h3', '', 'Your Four Pillars'), pillarsGrid);

        // 基础事实
        const facts = WO.el('div', 'en-bc-facts');
        const factData = [
            ['Day Master', cs.day_master],
            ['Zodiac', cs.zodiac],
            ['Lunar Date', cs.lunar_date]
        ].filter(([, v]) => v);
        factData.forEach(([label, value]) => {
            const fact = WO.el('div', 'en-bc-fact');
            fact.append(
                WO.el('div', 'en-bc-fact-label', label),
                WO.el('div', 'en-bc-fact-value', value)
            );
            facts.append(fact);
        });
        if (factData.length) els.result.append(facts);

        // 五行分布
        const balance = event.element_balance || {};
        const balanceItems = Object.entries(balance).filter(([, count]) => count);
        if (balanceItems.length) {
            const balanceText = balanceItems.map(([elem, count]) => `${elem}: ${count}`).join(' · ');
            const balanceFact = WO.el('div', 'en-bc-fact');
            balanceFact.append(
                WO.el('div', 'en-bc-fact-label', 'Element Balance'),
                WO.el('div', 'en-bc-fact-value', balanceText)
            );
            // 五行平衡小英文说明
            const balanceHint = WO.el('p', 'en-bc-balance-hint',
                'A balanced spread of the five elements is considered ideal. ' +
                'When one element is excessive or lacking, traditional practice suggests ' +
                'balancing it through lifestyle, environment, or wearing complementary accessories.'
            );
            const wrap = WO.el('div', 'en-bc-facts');
            wrap.append(balanceFact);
            els.result.append(wrap);
            els.result.append(balanceHint);
        }

        // 局限说明
        const limitations = event.limitations || [];
        if (limitations.length) {
            const note = WO.el('p', 'en-responsible-use');
            note.style.marginTop = '0.5rem';
            note.textContent = limitations.join(' ');
            els.result.append(note);
        }
    }

    // ============================================================
    // 渲染：AI 报告（report 事件）
    // ============================================================

    function renderReport(event) {
        // AI 概览
        if (event.chart_summary) {
            const section = WO.el('div', 'en-bc-section');
            section.append(WO.el('h3', '', 'Chart Overview'), WO.el('p', '', event.chart_summary));
            els.result.append(section);
        }

        // 元素说明（AI 返回的字符串，非空才显示）
        if (event.element_balance) {
            const section = WO.el('div', 'en-bc-section');
            section.append(WO.el('h3', '', 'Element Pattern'), WO.el('p', '', event.element_balance));
            els.result.append(section);
        }

        // 反思点
        const points = event.reflection_points || [];
        if (points.length) {
            const section = WO.el('div', 'en-bc-section');
            section.append(WO.el('h3', '', 'Reflection Points'));
            points.forEach(point => {
                const card = WO.el('div', 'en-bc-reflection');
                card.append(
                    WO.el('div', 'en-bc-reflection-label', point.label || 'Reflection'),
                    WO.el('p', '', point.text || '')
                );
                section.append(card);
            });
            els.result.append(section);
        }

        // 文化提醒（非预测）
        const cautions = event.cautions || [];
        if (cautions.length) {
            const section = WO.el('div', 'en-bc-section');
            section.append(WO.el('h3', '', 'Reflections to Sit With'));
            const list = WO.el('ul', 'en-bc-cautions');
            cautions.forEach(c => list.append(WO.el('li', '', c)));
            section.append(list);
            els.result.append(section);
        }
    }

    // ============================================================
    // 渲染：responsible-use
    // ============================================================

    function renderResponsibleUse(event) {
        if (event.responsible_use) {
            els.result.append(WO.el('div', 'en-responsible-use', event.responsible_use));
        }
    }

    // ============================================================
    // 重启
    // ============================================================

    function finalizeResult() {
        // Begin Again 重启按钮
        const restart = WO.el('button', 'en-btn en-btn-secondary', 'Begin Again');
        restart.style.marginTop = '1.5rem';
        restart.addEventListener('click', resetForm);
        els.result.append(restart);
        els.result.classList.add('is-visible');
    }

    function resetForm() {
        activeController?.abort();
        activeController = null;
        els.form.reset();
        syncTimeUnknown();
        els.result.replaceChildren();
        els.result.classList.remove('is-visible');
        WO.setStatus(els.status, '');
        document.getElementById('bc-name').focus();
    }

    // ============================================================
    // 提交（SSE 流）
    // ============================================================

    els.form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const payload = getPayload();
        const error = validate(payload);
        if (error) {
            WO.setStatus(els.status, error, 'error');
            return;
        }

        activeController?.abort();
        activeController = new AbortController();
        els.result.replaceChildren();
        els.result.classList.remove('is-visible');
        els.loading.classList.add('is-visible');
        els.submit.disabled = true;
        WO.setStatus(els.status, 'Generating your chart…');

        try {
            const response = await fetch('/api/en/birth-chart/stream', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Accept': 'text/event-stream' },
                body: JSON.stringify(payload),
                signal: activeController.signal
            });

            if (!response.ok) {
                const body = await response.json().catch(() => ({}));
                WO.setStatus(els.status, WO.extractErrorMessage(body), 'error');
                return;
            }

            // 注意：loading 在此不立即移除，要等首个 chart 事件到达后再隐藏。
            // 服务器收到请求 → 计算基础盘 → 发送 chart 事件，这段时间才是真正的等待。
            els.result.classList.add('is-visible');
            WO.setStatus(els.status, 'Reflecting on your chart…');

            let sawError = false;
            await WO.readSSE(response, (event) => {
                if (!event || !event.type) return;
                if (event.type === 'chart') {
                    // 首个 chart 事件到达，AI 已开始响应，隐藏 loading
                    els.loading.classList.remove('is-visible');
                    renderChart(event);
                    WO.setStatus(els.status, 'Composing reflections…');
                } else if (event.type === 'report') {
                    renderReport(event);
                } else if (event.type === 'responsible_use') {
                    renderResponsibleUse(event);
                } else if (event.type === 'error') {
                    sawError = true;
                    WO.setStatus(els.status, WO.messageForCode(event.error_code), 'error');
                } else if (event.type === 'done') {
                    // 流结束
                }
            });

            if (!sawError) {
                WO.setStatus(els.status, '', 'success');
                finalizeResult();
            } else {
                finalizeResult();
            }
        } catch (err) {
            if (err.name !== 'AbortError') {
                WO.setStatus(els.status, 'The connection was interrupted. Please try again.', 'error');
            }
        } finally {
            els.loading.classList.remove('is-visible');
            els.submit.disabled = false;
            activeController = null;
        }
    });
});
