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
            const group = document.createElement('div');
            group.className = 'en-spirit-group';
            const heading = document.createElement('h3');
            heading.textContent = title;
            group.appendChild(heading);
            if (!spirits.length) {
                const empty = document.createElement('p');
                empty.textContent = 'No reviewed spirit is listed.';
                group.appendChild(empty);
            } else {
                spirits.forEach((spirit) => {
                    const item = document.createElement('p');
                    item.className = 'en-spirit';
                    item.textContent = `${spirit.name} (${spirit.pinyin}) — ${spirit.explanation}`;
                    group.appendChild(item);
                });
            }
            container.appendChild(group);
        });
    };

    /**
     * 渲染干支（年月日时）。
     * 输入：data.gan_zhi = {year, month, day, hour}
     */
    const renderGanZhi = (data) => {
        const card = app.querySelector('[data-ganzhi-card]');
        const list = app.querySelector('[data-list="ganzhi"]');
        list.replaceChildren();
        const gz = data.gan_zhi || {};
        const entries = [
            ['Year', gz.year],
            ['Month', gz.month],
            ['Day', gz.day],
            ['Hour', gz.hour],
        ];
        const hasAny = entries.some(([, v]) => v);
        if (!hasAny) {
            card.hidden = true;
            return;
        }
        card.hidden = false;
        entries.forEach(([label, value]) => {
            if (value) addDefinition(list, label, value);
        });
    };

    /**
     * 渲染前后节气及天数。
     * 输入：data.solar_term = {current, previous:{name,days_ago}, next:{name,days_ahead}}
     */
    const renderSolarTerms = (data) => {
        const card = app.querySelector('[data-solar-terms-card]');
        const list = app.querySelector('[data-list="solar-terms"]');
        list.replaceChildren();
        const st = data.solar_term || {};
        const prev = st.previous;
        const next = st.next;
        if (!prev && !next) {
            card.hidden = true;
            return;
        }
        card.hidden = false;
        if (prev) {
            addDefinition(list, 'Previous term', `${prev.name} (${prev.days_ago} days ago)`);
        }
        if (st.current) {
            addDefinition(list, 'Current term', st.current.name);
        }
        if (next) {
            addDefinition(list, 'Next term', `${next.name} (in ${next.days_ahead} days)`);
        }
    };

    /**
     * 渲染节日列表。
     * 输入：data.festivals = [{name, type, pinyin, explanation}]
     */
    const renderFestivals = (data) => {
        const card = app.querySelector('[data-festivals-card]');
        const list = app.querySelector('[data-list="festivals"]');
        list.replaceChildren();
        const festivals = data.festivals || [];
        if (!festivals.length) {
            card.hidden = true;
            return;
        }
        card.hidden = false;
        festivals.forEach((f) => {
            const li = document.createElement('li');
            li.textContent = f.name;
            if (f.type) {
                const span = document.createElement('span');
                span.className = 'en-festival-type';
                span.textContent = ` (${f.type})`;
                li.appendChild(span);
            }
            list.appendChild(li);
        });
    };

    /**
     * 渲染特殊规则（馀事勿取等）。
     * 输入：data.special_indications = [{type, label, description}]
     */
    const renderSpecialIndications = (data) => {
        const card = app.querySelector('[data-special-card]');
        const list = app.querySelector(`[data-list="special"]`);
        list.replaceChildren();
        const specials = data.special_indications || [];
        if (!specials.length) {
            card.hidden = true;
            return;
        }
        card.hidden = false;
        specials.forEach((s) => {
            const li = document.createElement('li');
            const label = document.createElement('strong');
            label.textContent = s.label || s.type || '';
            li.appendChild(label);
            if (s.description) {
                const desc = document.createElement('span');
                desc.className = 'en-special-desc';
                desc.textContent = ` — ${s.description}`;
                li.appendChild(desc);
            }
            list.appendChild(li);
        });
    };

    const renderData = (data) => {
        setText('date', data.date);
        setText('lunar-date', data.lunar_date);
        setText('zodiac', data.zodiac);
        setText('solar-term', data.solar_term?.current?.name || 'Between solar terms');
        setText('responsible-use', data.responsible_use);
        setText('footer-disclaimer', data.footer_disclaimer);

        renderGanZhi(data);
        renderSolarTerms(data);
        renderFestivals(data);
        renderSpecialIndications(data);

        renderList('favorable', data.favorable_activities);
        renderList('unfavorable', data.unfavorable_activities);
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
        const scenarioTodayEl = app.querySelector('[data-field="scenario-today"]');
        const scenarioNextEl = app.querySelector('[data-field="scenario-next"]');
        if (data.scenario_assessment) {
            const sa = data.scenario_assessment;
            setText('scenario-label', sa.label);
            // 今日评估
            const todayText = sa.status_code === 'favored'
                ? `Today is traditionally favored for ${sa.label.toLowerCase()}.`
                : sa.status_code === 'avoided'
                    ? `Today is traditionally avoided for ${sa.label.toLowerCase()}.`
                    : `Today has no specific indication for ${sa.label.toLowerCase()}.`;
            scenarioTodayEl.textContent = todayText;
            // 下一个适合的日子
            const nf = data.next_favored_date;
            if (nf) {
                const daysWord = nf.days_ahead === 0 ? 'today'
                    : nf.days_ahead === 1 ? 'tomorrow'
                        : `in ${nf.days_ahead} days`;
                scenarioNextEl.textContent =
                    `Next favored day for ${sa.label.toLowerCase()}: ${nf.date} (${daysWord}).`;
                scenarioNextEl.hidden = false;
            } else {
                scenarioNextEl.hidden = true;
            }
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

    /**
     * 日期导航：前/今/后按钮。
     * 点击后更新日期选择器并重新加载黄历。
     */
    app.querySelectorAll('[data-nav]').forEach((btn) => {
        btn.addEventListener('click', () => {
            const action = btn.dataset.nav;
            if (action === 'today') {
                dateInput.value = new Date().toISOString().slice(0, 10);
            } else {
                const current = new Date(dateInput.value);
                const offset = action === 'prev' ? -1 : 1;
                current.setDate(current.getDate() + offset);
                dateInput.value = current.toISOString().slice(0, 10);
            }
            loadAlmanac();
        });
    });

    /**
     * 九天黄历网格。
     * 折叠展开时首次加载，场景按钮切换时重新加载。
     */
    let weekLoaded = false;
    const weekToggle = app.querySelector('[data-week-toggle]');
    const weekPanel = app.querySelector('[data-week-panel]');
    const weekGrid = app.querySelector('[data-week-grid]');
    const weekScenarios = app.querySelector('[data-week-scenarios]');

    const loadWeekAlmanac = async () => {
        weekGrid.replaceChildren();
        const loading = document.createElement('p');
        loading.className = 'en-week-loading';
        loading.textContent = 'Loading the ten-day almanac…';
        weekGrid.appendChild(loading);

        const activeBtn = weekScenarios.querySelector('.is-active');
        const scenario = activeBtn ? activeBtn.dataset.scenario : '';
        const focusEl = app.querySelector('[data-week-focus]');
        if (focusEl && activeBtn) {
            focusEl.textContent = `Current focus: ${activeBtn.textContent}`;
        }
        const params = new URLSearchParams();
        if (scenario) params.set('scenario', scenario);

        try {
            const response = await fetch(`/api/en/week-almanac?${params.toString()}`, {
                headers: { Accept: 'application/json' },
            });
            const payload = await response.json();
            if (!response.ok || !payload.success) {
                throw new Error(payload.error?.message || 'The ten-day almanac could not be loaded.');
            }
            renderWeekGrid(payload.data || []);
            weekLoaded = true;
        } catch (error) {
            weekGrid.replaceChildren();
            const err = document.createElement('p');
            err.className = 'en-week-error';
            err.textContent = `Error: ${error.message}`;
            weekGrid.appendChild(err);
        }
    };

    /**
     * 渲染九天网格。
     * 输入：days 数组，每项含 date/lunar_date/gan_zhi/favorable_activities/unfavorable_activities/conflict_clash/solar_term/scenario_assessment
     */
    const renderWeekGrid = (days) => {
        weekGrid.replaceChildren();
        if (!days.length) {
            const empty = document.createElement('p');
            empty.textContent = 'No data available.';
            weekGrid.appendChild(empty);
            return;
        }
        const todayStr = new Date().toISOString().slice(0, 10);
        days.forEach((day) => {
            const card = document.createElement('div');
            card.className = 'en-week-card';
            if (day.date === todayStr) card.classList.add('is-today');

            const dateLine = document.createElement('div');
            dateLine.className = 'en-week-date';
            dateLine.textContent = day.date;
            card.appendChild(dateLine);

            const lunar = document.createElement('div');
            lunar.className = 'en-week-lunar';
            lunar.textContent = day.lunar_date || '';
            card.appendChild(lunar);

            const gz = day.gan_zhi || {};
            if (gz.day) {
                const gzLine = document.createElement('div');
                gzLine.className = 'en-week-ganzhi';
                gzLine.textContent = gz.day;
                card.appendChild(gzLine);
            }

            const st = day.solar_term;
            if (st && st.current) {
                const stLine = document.createElement('div');
                stLine.className = 'en-week-term';
                stLine.textContent = st.current.name;
                card.appendChild(stLine);
            }

            const fav = (day.favorable_activities || []).map((a) => a.label).join(', ');
            if (fav) {
                const favLine = document.createElement('div');
                favLine.className = 'en-week-fav';
                favLine.textContent = `✓ ${fav}`;
                card.appendChild(favLine);
            }

            const unfav = (day.unfavorable_activities || []).map((a) => a.label).join(', ');
            if (unfav) {
                const unfavLine = document.createElement('div');
                unfavLine.className = 'en-week-unfav';
                unfavLine.textContent = `✕ ${unfav}`;
                card.appendChild(unfavLine);
            }

            const cc = day.conflict_clash;
            if (cc && cc.clashes_with) {
                const ccLine = document.createElement('div');
                ccLine.className = 'en-week-clash';
                ccLine.textContent = `Clash: ${cc.clashes_with}`;
                card.appendChild(ccLine);
            }

            const sa = day.scenario_assessment;
            const statusCode = sa && sa.status_code ? sa.status_code : '';
            // 仅在 Favored / Avoided 时显示 badge；Not Loaded 不显示
            if (sa && sa.status_label && (statusCode === 'favored' || statusCode === 'avoided')) {
                const saLine = document.createElement('div');
                saLine.className = 'en-week-scenario-status';
                saLine.textContent = sa.status_label;
                if (statusCode === 'favored') {
                    saLine.classList.add('is-favored');
                } else {
                    saLine.classList.add('is-avoided');
                }
                card.appendChild(saLine);
            }

            weekGrid.appendChild(card);
        });
    };

    // 折叠/展开
    weekToggle.addEventListener('click', () => {
        const expanded = weekToggle.getAttribute('aria-expanded') === 'true';
        weekToggle.setAttribute('aria-expanded', String(!expanded));
        weekPanel.hidden = expanded;
        if (!expanded && !weekLoaded) {
            // 首次展开若无选中场景，默认选第一个（已删除 General，必须有具体场景）
            if (!weekScenarios.querySelector('.is-active')) {
                const first = weekScenarios.querySelector('.en-week-scenario');
                if (first) first.classList.add('is-active');
            }
            loadWeekAlmanac();
        }
    });

    // 场景按钮切换
    weekScenarios.addEventListener('click', (event) => {
        const btn = event.target.closest('[data-scenario]');
        if (!btn || btn.classList.contains('is-active')) return;
        weekScenarios.querySelectorAll('.en-week-scenario').forEach((b) => {
            b.classList.toggle('is-active', b === btn);
        });
        loadWeekAlmanac();
    });

    dateInput.value = new Date().toISOString().slice(0, 10);
    form.addEventListener('submit', (event) => {
        event.preventDefault();
        loadAlmanac();
    });
    loadAlmanac();
});
