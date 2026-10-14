(function () {
    "use strict";

    const app = document.getElementById("analytics-app");
    const config = {
        overviewUrl: app?.dataset.overviewUrl || "",
        searchConsoleUrl: app?.dataset.searchConsoleUrl || "",
    };
    const rangeSelect = document.getElementById("range-select");
    const refreshButton = document.getElementById("refresh-button");
    const loading = document.getElementById("dashboard-loading");
    const content = document.getElementById("dashboard-content");
    const errorBox = document.getElementById("dashboard-error");
    const noteBox = document.getElementById("coverage-note");
    const number = new Intl.NumberFormat("zh-CN");

    function formatNumber(value) { return number.format(Number(value || 0)); }
    function formatBytes(value) {
        const bytes = Number(value || 0);
        if (bytes < 1024) return `${formatNumber(bytes)} B`;
        if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
        return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
    }
    function dateString(date) { return date.toISOString().slice(0, 10); }
    function rangeParams(days) {
        const end = new Date();
        const start = new Date(end.getTime() - (Number(days) - 1) * 86400000);
        return new URLSearchParams({ from: dateString(start), to: dateString(end) });
    }
    function showError(message) {
        errorBox.textContent = message;
        errorBox.hidden = false;
        loading.hidden = true;
        content.hidden = true;
    }
    function rowValue(value, requests, visits) {
        const tr = document.createElement("tr");
        [value, formatNumber(requests), formatNumber(visits)].forEach((text) => {
            const td = document.createElement("td");
            td.textContent = text;
            tr.appendChild(td);
        });
        return tr;
    }
    function fillTable(id, items) {
        const body = document.getElementById(id);
        body.replaceChildren();
        (items || []).slice(0, 10).forEach((item) => body.appendChild(rowValue(item.value, item.requests, item.visits)));
        if (!items || !items.length) {
            const tr = document.createElement("tr");
            const td = document.createElement("td");
            td.colSpan = 3;
            td.className = "analytics-muted";
            td.textContent = "暂无数据";
            tr.appendChild(td);
            body.appendChild(tr);
        }
    }
    function drawDaily(items) {
        const chart = document.getElementById("daily-chart");
        const empty = document.getElementById("daily-empty");
        chart.replaceChildren();
        if (!items || !items.length) { chart.hidden = true; empty.hidden = false; return; }
        chart.hidden = false; empty.hidden = true;
        const max = Math.max(...items.map((item) => Number(item.requests || 0)), 1);
        items.forEach((item) => {
            const column = document.createElement("div");
            column.className = "day-column";
            column.title = `${item.date}：${formatNumber(item.requests)} 个请求，${formatNumber(item.visits)} 次访问`;
            const track = document.createElement("div"); track.className = "bar-track";
            const fill = document.createElement("div"); fill.className = "bar-fill";
            fill.style.height = `${Math.max(3, (Number(item.requests || 0) / max) * 100)}%`;
            track.appendChild(fill);
            const label = document.createElement("span"); label.className = "day-label"; label.textContent = item.date.slice(5);
            column.append(track, label); chart.appendChild(column);
        });
    }
    function drawOverview(data) {
        const totals = data.totals || {};
        document.getElementById("metric-requests").textContent = formatNumber(totals.requests);
        document.getElementById("metric-visits").textContent = formatNumber(totals.visits);
        document.getElementById("metric-bytes").textContent = formatBytes(totals.bytes);
        const topPage = (data.pages || [])[0];
        document.getElementById("metric-top-page").textContent = topPage ? topPage.value : "—";
        document.getElementById("metric-top-page-count").textContent = topPage ? `${formatNumber(topPage.requests)} 个请求` : "暂无数据";
        drawDaily(data.daily || []);
        fillTable("pages-table", data.pages);
        fillTable("countries-table", data.countries);
        fillTable("referrers-table", data.referrers);
        const referrerSummary = document.getElementById("referrers-summary");
        referrerSummary.textContent = (data.referrers && data.referrers.length) ? "按来源网站汇总" : "当前 Cloudflare Zone 未提供来源网站字段；可在 Cloudflare 控制台查看。";
        const notes = (data.notes || []).filter((note) => note.includes("仅保留") || note.includes("来源网站"));
        noteBox.textContent = notes.join(" "); noteBox.hidden = !notes.length;
    }
    async function loadSearchConsole(params) {
        const response = await fetch(`${config.searchConsoleUrl}?${params.toString()}&dimensions=date`, { credentials: "same-origin" });
        const payload = await response.json();
        if (!response.ok || !payload.success) throw new Error(payload.error?.message || "Search Console 数据暂时无法读取。");
        const rows = payload.data?.rows || [];
        const clicks = rows.reduce((sum, row) => sum + Number(row.clicks || 0), 0);
        const impressions = rows.reduce((sum, row) => sum + Number(row.impressions || 0), 0);
        const positionWeight = rows.reduce((sum, row) => sum + Number(row.position || 0) * Number(row.impressions || 0), 0);
        document.getElementById("search-clicks").textContent = formatNumber(clicks);
        document.getElementById("search-impressions").textContent = formatNumber(impressions);
        document.getElementById("search-ctr").textContent = impressions ? `${(clicks / impressions * 100).toFixed(2)}%` : "0%";
        document.getElementById("search-position").textContent = impressions ? (positionWeight / impressions).toFixed(1) : "—";
        document.getElementById("search-summary").textContent = rows.length ? "Google Search Console 按日汇总。" : "这段时间没有搜索数据。";
    }
    async function load() {
        loading.hidden = false; content.hidden = true; errorBox.hidden = true; refreshButton.disabled = true;
        const params = rangeParams(rangeSelect.value);
        try {
            const response = await fetch(`${config.overviewUrl}?${params.toString()}`, { credentials: "same-origin" });
            const payload = await response.json();
            if (!response.ok || !payload.success) throw new Error(payload.error?.message || "Cloudflare 数据暂时无法读取。");
            drawOverview(payload.data || {});
            try { await loadSearchConsole(params); } catch (searchError) {
                document.getElementById("search-summary").textContent = searchError.message;
            }
            loading.hidden = true; content.hidden = false;
            document.getElementById("last-updated").textContent = `更新于 ${new Date().toLocaleTimeString("zh-CN", { hour: "2-digit", minute: "2-digit" })}`;
        } catch (error) { showError(error.message); }
        finally { refreshButton.disabled = false; }
    }
    refreshButton.addEventListener("click", load);
    rangeSelect.addEventListener("change", load);
    load();
})();
