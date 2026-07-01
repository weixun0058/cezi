document.addEventListener('DOMContentLoaded', () => {
    const app = document.querySelector('[data-almanac-app]');
    if (!app) return;

    const form = app.querySelector('[data-almanac-form]');
    const dateInput = app.querySelector('[data-almanac-date]');
    const scenarioInput = app.querySelector('[data-almanac-scenario]');
    const status = app.querySelector('[data-almanac-status]');
    const results = app.querySelector('[data-almanac-results]');

    const setText = (name, value) => {
        const element = app.querySelector(`[data-field="${name}"]`);
        if (element) element.textContent = value || 'Not listed';
    };

    const renderList = (name, items, labelKey = 'label') => {
        const list = app.querySelector(`[data-list="${name}"]`);
        list.replaceChildren();
        const values = items || [];
        if (!values.length) {
            const empty = document.createElement('li');
            empty.textContent = 'No reviewed indication is listed.';
            list.appendChild(empty);
            return;
        }
        values.forEach((item) => {
            const row = document.createElement('li');
            row.textContent = item[labelKey] || item.name || 'Reviewed indication';
            list.appendChild(row);
        });
    };

    const addDefinition = (list, term, value) => {
        const dt = document.createElement('dt');
        const dd = document.createElement('dd');
        dt.textContent = term;
        dd.textContent = value || 'Not listed';
        list.append(dt, dd);
    };

    const renderSpirits = (data) => {
        const container = app.querySelector('[data-list="spirits"]');
        container.replaceChildren();
        const groups = [
            ['Auspicious', data.auspicious_spirits || []],
            ['Inauspicious', data.inauspicious_spirits || []],
        ];
        groups.forEach(([title, spirits]) => {
            const heading = document.createElement('h3');
            heading.textContent = title;
            container.appendChild(heading);
            if (!spirits.length) {
                const empty = document.createElement('p');
                empty.textContent = 'No reviewed spirit is listed.';
                container.appendChild(empty);
                return;
            }
            spirits.forEach((spirit) => {
                const item = document.createElement('p');
                item.className = 'en-spirit';
                item.textContent = `${spirit.name} (${spirit.pinyin}) — ${spirit.explanation}`;
                container.appendChild(item);
            });
        });
    };

    const renderData = (data) => {
        setText('date', data.date);
        setText('lunar-date', data.lunar_date);
        setText('zodiac', data.zodiac);
        setText('solar-term', data.solar_term?.current || 'Between solar terms');
        setText('peng-zu', data.peng_zu_taboos?.summary);
        setText('responsible-use', data.responsible_use);
        setText('footer-disclaimer', data.footer_disclaimer);

        renderList('favorable', data.favorable_activities);
        renderList('unfavorable', data.unfavorable_activities);
        renderList('mixed', data.mixed_activities);
        renderSpirits(data);

        const directions = app.querySelector('[data-list="directions"]');
        directions.replaceChildren();
        Object.entries({
            Joy: data.directions?.joy,
            Fortune: data.directions?.fortune,
            Wealth: data.directions?.wealth,
        }).forEach(([name, value]) => {
            addDefinition(
                directions,
                name,
                value ? `${value.direction} (${value.trigram})` : null
            );
        });

        const clash = app.querySelector('[data-list="clash"]');
        clash.replaceChildren();
        addDefinition(clash, 'Clashes with', data.conflict_clash?.clashes_with);
        addDefinition(clash, 'Clash pillar', data.conflict_clash?.clash_pillar);
        addDefinition(
            clash,
            'Direction to approach with care',
            data.conflict_clash?.inauspicious_direction
        );

        const scenarioCard = app.querySelector('[data-scenario-card]');
        if (data.scenario_assessment) {
            setText('scenario-label', data.scenario_assessment.label);
            setText('scenario-status', data.scenario_assessment.status_label);
            scenarioCard.hidden = false;
        } else {
            scenarioCard.hidden = true;
        }
    };

    const loadAlmanac = async () => {
        status.textContent = 'Loading the almanac…';
        status.classList.remove('is-error');
        status.setAttribute('role', 'status');
        results.hidden = true;

        const params = new URLSearchParams({ date: dateInput.value });
        if (scenarioInput.value) params.set('scenario', scenarioInput.value);

        try {
            const response = await fetch(`/api/en/daily-almanac?${params.toString()}`, {
                headers: { Accept: 'application/json' },
            });
            const payload = await response.json();
            if (!response.ok || !payload.success) {
                throw new Error(payload.error?.message || 'The almanac could not be loaded.');
            }
            renderData(payload.data);
            status.textContent = '';
            results.hidden = false;
        } catch (error) {
            status.textContent = `Error: ${error.message || 'The almanac could not be loaded.'}`;
            status.classList.add('is-error');
            status.setAttribute('role', 'alert');
        }
    };

    dateInput.value = new Date().toISOString().slice(0, 10);
    form.addEventListener('submit', (event) => {
        event.preventDefault();
        loadAlmanac();
    });
    loadAlmanac();
});
