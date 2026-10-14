"""Owner-only JSON endpoints for Cloudflare and Search Console analytics."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from flask import Blueprint, abort, current_app, render_template, request, url_for

from ..analytics import AnalyticsNotConfigured, AnalyticsProviderError
from ..api_utils import failure, success
from .article_admin import _is_authorized


def _require_admin():
    # Do not expose whether analytics is configured to unauthenticated callers.
    if not current_app.config.get("ARTICLE_ADMIN_PASSWORD"):
        return failure(
            "ANALYTICS_ADMIN_AUTH_REQUIRED",
            "请先配置 ARTICLE_ADMIN_PASSWORD，再使用统计接口。",
            status=503,
        )
    if not _is_authorized():
        abort(404)
    return None


def _date_range() -> tuple[date, date] | tuple[None, tuple]:
    timezone_name = str(current_app.config.get("DEFAULT_TIMEZONE", "Asia/Shanghai"))
    try:
        today = datetime.now(ZoneInfo(timezone_name)).date()
    except Exception:
        today = date.today()
    # `to` is inclusive for callers; internally the end is exclusive.
    start_default = today - timedelta(days=29)
    start_raw = request.args.get("from", "").strip()
    end_raw = request.args.get("to", "").strip()
    try:
        start = date.fromisoformat(start_raw) if start_raw else start_default
        end_inclusive = date.fromisoformat(end_raw) if end_raw else today
    except ValueError:
        return None, failure(
            "INVALID_ANALYTICS_RANGE",
            "日期必须使用 YYYY-MM-DD 格式。",
            status=400,
        )
    end_exclusive = end_inclusive + timedelta(days=1)
    if start > end_inclusive:
        return None, failure(
            "INVALID_ANALYTICS_RANGE",
            "from 不能晚于 to。",
            status=400,
        )
    max_days = max(1, int(current_app.config.get("ANALYTICS_MAX_RANGE_DAYS", 31)))
    if (end_exclusive - start).days > max_days:
        return None, failure(
            "ANALYTICS_RANGE_TOO_LARGE",
            f"单次最多查询 {max_days} 天。",
            status=400,
        )
    return (start, end_exclusive), None


def _range_data(start: date, end_exclusive: date) -> dict[str, str]:
    return {
        "from": start.isoformat(),
        "to": (end_exclusive - timedelta(days=1)).isoformat(),
        "timezone": str(current_app.config.get("DEFAULT_TIMEZONE", "Asia/Shanghai")),
    }


def _dimensions() -> tuple[list[str] | None, tuple | None]:
    raw = request.args.get("dimensions", "date").strip()
    values = [item.strip() for item in raw.split(",") if item.strip()]
    allowed = current_app.extensions["search_console"].allowed_dimensions
    if not values or len(values) > 5 or len(set(values)) != len(values):
        return None, failure("INVALID_SEARCH_DIMENSIONS", "dimensions 参数无效。", status=400)
    invalid = [item for item in values if item not in allowed]
    if invalid:
        return None, failure(
            "INVALID_SEARCH_DIMENSIONS",
            "Search Console 维度无效。",
            status=400,
            details={"allowed": sorted(allowed)},
        )
    return values, None


def create_analytics_admin_blueprint() -> Blueprint:
    blueprint = Blueprint("analytics_admin", __name__)

    @blueprint.after_request
    def protect_analytics_response(response):
        response.headers["X-Robots-Tag"] = "noindex, nofollow, noarchive"
        response.headers["Cache-Control"] = "no-store"
        response.headers["Pragma"] = "no-cache"
        return response

    @blueprint.get("/status")
    def status():
        blocked = _require_admin()
        if blocked is not None:
            return blocked
        cloudflare = current_app.extensions["cloudflare_analytics"]
        search_console = current_app.extensions["search_console"]
        return success(
            {
                "cloudflare": {"configured": cloudflare.configured},
                "search_console": {
                    "configured": search_console.configured,
                    "site_url": search_console.site_url or None,
                },
            }
        )

    @blueprint.get("")
    def dashboard():
        blocked = _require_admin()
        if blocked is not None:
            return blocked
        return render_template(
            "admin/analytics.html",
            overview_url=url_for("analytics_admin.overview"),
            search_console_url=url_for("analytics_admin.search_console"),
            article_admin_url=url_for("article_admin.index"),
        )

    @blueprint.get("/overview")
    def overview():
        blocked = _require_admin()
        if blocked is not None:
            return blocked
        date_values, error = _date_range()
        if error is not None:
            return error
        start, end_exclusive = date_values
        provider = current_app.extensions["cloudflare_analytics"]
        try:
            data = provider.overview(start, end_exclusive)
        except AnalyticsNotConfigured as exc:
            return failure("ANALYTICS_NOT_CONFIGURED", str(exc), status=503)
        except AnalyticsProviderError as exc:
            return failure("ANALYTICS_PROVIDER_ERROR", str(exc), status=502)
        data["range"] = _range_data(start, end_exclusive)
        data["providers"] = {
            "cloudflare": True,
            "search_console": current_app.extensions["search_console"].configured,
        }
        return success(data)

    @blueprint.get("/search-console")
    def search_console():
        blocked = _require_admin()
        if blocked is not None:
            return blocked
        date_values, error = _date_range()
        if error is not None:
            return error
        dimensions, error = _dimensions()
        if error is not None:
            return error
        start, end_exclusive = date_values
        try:
            data = current_app.extensions["search_console"].query(
                start,
                end_exclusive,
                dimensions,
                row_limit=min(max(int(request.args.get("limit", "100")), 1), 25000),
            )
        except (TypeError, ValueError):
            return failure("INVALID_SEARCH_LIMIT", "limit 必须是数字。", status=400)
        except AnalyticsNotConfigured as exc:
            return failure("SEARCH_CONSOLE_NOT_CONFIGURED", str(exc), status=503)
        except AnalyticsProviderError as exc:
            return failure("SEARCH_CONSOLE_PROVIDER_ERROR", str(exc), status=502)
        data["range"] = _range_data(start, end_exclusive)
        return success(data)

    return blueprint
