document.addEventListener('DOMContentLoaded', () => {
    const elements = {
        analyze: document.getElementById('analyze-btn'),
        reset: document.getElementById('reset-btn'),
        result: document.getElementById('result-container'),
        loading: document.getElementById('loading-container'),
        content: document.getElementById('analysis-content'),
        chart: document.getElementById('chart-summary'),
        status: document.getElementById('form-status'),
        trueSolar: document.getElementById('use-true-solar-time'),
        longitudeGroup: document.getElementById('longitude-group')
    };
    let activeController = null;
    let legacyReport = '';

    const setStatus = (message, type = '') => {
        elements.status.textContent = message;
        elements.status.dataset.type = type;
    };

    const createElement = (tag, className, text) => {
        const element = document.createElement(tag);
        if (className) element.className = className;
        if (text !== undefined) element.textContent = text;
        return element;
    };

    const getPayload = () => ({
        name: document.getElementById('name').value.trim(),
        gender: document.querySelector('input[name="gender"]:checked').value,
        birth_date: document.getElementById('birth-date').value,
        birth_time: document.getElementById('birth-time').value,
        birth_place: document.getElementById('birth-place').value.trim(),
        timezone: document.getElementById('timezone').value,
        use_true_solar_time: elements.trueSolar.checked,
        longitude: document.getElementById('longitude').value || null
    });

    const validate = (payload) => {
        if (!payload.name) return '请输入姓名';
        if (!payload.birth_date) return '请选择出生日期';
        if (!payload.birth_time) return '请选择出生时辰或“时辰未知”';
        if (payload.use_true_solar_time && payload.birth_time === '未知') return '时辰未知时不能启用真太阳时';
        if (payload.use_true_solar_time && payload.longitude === null) return '请输入出生地经度';
        return '';
    };

    const renderChart = (chart) => {
        elements.chart.replaceChildren();
        const heading = createElement('div', 'chart-heading');
        heading.append(
            createElement('span', 'report-kicker', '命盘纲要'),
            createElement('h2', 'chart-title', '四柱排盘')
        );
        elements.chart.append(heading);

        const pillarGrid = createElement('div', 'pillar-grid');
        const pillarLabels = { year: '年柱', month: '月柱', day: '日柱', time: '时柱' };
        Object.entries(pillarLabels).forEach(([key, label]) => {
            const item = createElement('div', `pillar-item pillar-${key}`);
            item.append(
                createElement('span', 'pillar-label', label),
                createElement('strong', 'pillar-value', chart.pillars[key] || '未知')
            );
            pillarGrid.append(item);
        });
        elements.chart.append(pillarGrid);

        const facts = createElement('div', 'chart-facts');
        const factData = [
            ['生肖', chart.zodiac],
            ['日主', chart.day_master],
            ['五行', Object.entries(chart.wu_xing_counts).map(([key, value]) => `${key}${value}`).join(' · ')]
        ];
        if (chart.calendar.true_solar_time) {
            factData.push(['真太阳时', `修正 ${chart.calendar.correction_minutes} 分钟`]);
        }
        factData.forEach(([label, value]) => {
            const fact = createElement('p', 'chart-fact');
            fact.append(createElement('span', '', label), createElement('strong', '', value));
            facts.append(fact);
        });
        elements.chart.append(facts);
        elements.chart.classList.remove('hidden');
    };

    const reveal = (element) => {
        elements.content.append(element);
        window.requestAnimationFrame(() => element.classList.add('is-visible'));
    };

    const renderReportStart = (event) => {
        const overview = createElement('section', 'report-overview report-reveal');
        overview.append(
            createElement('span', 'report-kicker', '命书总览'),
            createElement('p', 'report-summary', event.summary)
        );
        if (event.keywords?.length) {
            const keywords = createElement('div', 'report-keywords');
            event.keywords.forEach(keyword => keywords.append(createElement('span', 'report-keyword', keyword)));
            overview.append(keywords);
        }
        reveal(overview);
    };

    const renderReportSection = (section) => {
        const article = createElement('article', 'report-section report-reveal');
        article.dataset.section = section.id;
        article.append(createElement('h3', 'report-section-title', section.title));
        const points = createElement('div', 'report-points');
        section.points.forEach(point => {
            const item = createElement('div', 'report-point');
            item.append(
                createElement('h4', 'report-point-label', point.label),
                createElement('p', 'report-point-text', point.text)
            );
            points.append(item);
        });
        article.append(points);
        reveal(article);
    };

    const renderReportEnd = (event) => {
        if (event.actions?.length) {
            const actions = createElement('section', 'report-actions report-reveal');
            actions.append(
                createElement('span', 'report-kicker', '行事参考'),
                createElement('h3', 'report-section-title', '顺势而为，落在日常')
            );
            const list = createElement('div', 'action-list');
            event.actions.forEach(action => {
                const item = createElement('div', 'action-item');
                item.append(
                    createElement('strong', 'action-title', action.title),
                    createElement('p', 'action-text', action.text)
                );
                list.append(item);
            });
            actions.append(list);
            reveal(actions);
        }
        if (event.closing) reveal(createElement('p', 'report-closing report-reveal', event.closing));
    };

    const renderLegacyText = (text) => {
        legacyReport += text;
        let fallback = elements.content.querySelector('.legacy-report');
        if (!fallback) {
            fallback = createElement('div', 'legacy-report report-reveal');
            reveal(fallback);
        }
        fallback.textContent = legacyReport;
    };

    const parseEventBlock = (block) => {
        const data = block.split('\n')
            .filter(line => line.startsWith('data:'))
            .map(line => line.slice(5).trim())
            .join('\n');
        if (!data) return null;
        return JSON.parse(data);
    };

    const readStream = async (response) => {
        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let buffer = '';
        while (true) {
            const { value, done } = await reader.read();
            buffer += decoder.decode(value || new Uint8Array(), { stream: !done });
            const blocks = buffer.split(/\r?\n\r?\n/);
            buffer = blocks.pop() || '';
            for (const block of blocks) {
                const event = parseEventBlock(block);
                if (!event) continue;
                if (event.type === 'chart') renderChart(event.chart);
                if (event.type === 'report_start') renderReportStart(event);
                if (event.type === 'report_section') renderReportSection(event.section);
                if (event.type === 'report_end') renderReportEnd(event);
                if (event.type === 'text') renderLegacyText(event.text || '');
                if (event.type === 'error') throw new Error(event.error || '分析流中断');
                if (event.type?.startsWith('report_')) await new Promise(resolve => setTimeout(resolve, 90));
            }
            if (done) break;
        }
    };

    elements.trueSolar.addEventListener('change', () => {
        elements.longitudeGroup.classList.toggle('hidden', !elements.trueSolar.checked);
    });

    elements.analyze.addEventListener('click', async () => {
        const payload = getPayload();
        const validationError = validate(payload);
        if (validationError) {
            setStatus(validationError, 'error');
            return;
        }
        activeController?.abort();
        activeController = new AbortController();
        legacyReport = '';
        elements.content.replaceChildren();
        elements.chart.replaceChildren();
        elements.chart.classList.add('hidden');
        elements.result.classList.remove('hidden');
        elements.loading.classList.remove('hidden');
        elements.analyze.disabled = true;
        setStatus('正在建立分析连接…');
        try {
            const response = await fetch('/api/lunming/stream', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Accept': 'text/event-stream' },
                body: JSON.stringify(payload),
                signal: activeController.signal
            });
            if (!response.ok) {
                const body = await response.json().catch(() => ({}));
                throw new Error(body.error?.message || '分析请求失败');
            }
            elements.loading.classList.add('hidden');
            await readStream(response);
            setStatus('解读完成', 'success');
        } catch (error) {
            if (error.name !== 'AbortError') setStatus(error.message || '分析流中断，请重试', 'error');
        } finally {
            elements.loading.classList.add('hidden');
            elements.analyze.disabled = false;
            activeController = null;
        }
    });

    elements.reset.addEventListener('click', () => {
        activeController?.abort();
        document.getElementById('lunming-form').querySelectorAll('input[type="text"], input[type="number"], input[type="date"]').forEach(input => { input.value = ''; });
        document.querySelector('input[name="gender"][value="男"]').checked = true;
        elements.trueSolar.checked = false;
        elements.longitudeGroup.classList.add('hidden');
        elements.result.classList.add('hidden');
        elements.content.replaceChildren();
        setStatus('');
    });
});
