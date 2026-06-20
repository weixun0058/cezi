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
    let fullReport = '';
    let currentChart = null;
    let pendingText = '';
    let renderScheduled = false;

    const setStatus = (message, type = '') => {
        elements.status.textContent = message;
        elements.status.dataset.type = type;
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

    const renderText = () => {
        renderScheduled = false;
        if (pendingText) {
            fullReport += pendingText;
            pendingText = '';
        }
        elements.content.textContent = fullReport;
    };

    const queueText = (text) => {
        pendingText += text;
        if (!renderScheduled) {
            renderScheduled = true;
            window.requestAnimationFrame(renderText);
        }
    };

    const renderChart = (chart) => {
        currentChart = chart;
        const pillars = chart.pillars;
        const timePillar = pillars.time || '未知';
        elements.chart.textContent = [
            `四柱：${pillars.year}年 ${pillars.month}月 ${pillars.day}日 ${timePillar}时`,
            `生肖：${chart.zodiac}　日主：${chart.day_master}`,
            `五行：${Object.entries(chart.wu_xing_counts).map(([key, value]) => `${key}${value}`).join(' ')}`,
            chart.calendar.true_solar_time ? `真太阳时修正：${chart.calendar.correction_minutes} 分钟` : ''
        ].filter(Boolean).join('\n');
        elements.chart.classList.remove('hidden');
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
                if (event.type === 'text') queueText(event.text || '');
                if (event.type === 'error') throw new Error(event.error || '分析流中断');
            }
            if (done) break;
        }
        renderText();
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
        fullReport = '';
        currentChart = null;
        elements.content.textContent = '';
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
            setStatus('分析完成', 'success');
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
        setStatus('');
    });

});
