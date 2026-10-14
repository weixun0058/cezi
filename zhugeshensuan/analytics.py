"""Read-only analytics provider clients used by the owner dashboard.

The application deliberately keeps provider credentials server-side.  Cloudflare
is used for edge traffic and Web Analytics-style dimensions, while Search
Console is used for Google organic-search performance.  Both providers are
optional so an unconfigured production deployment continues to serve the site.
"""

from __future__ import annotations

import json
import logging
import threading
import time
from collections import defaultdict
from datetime import UTC, date, datetime, timedelta
from datetime import time as datetime_time
from typing import Any
from urllib.parse import quote
from zoneinfo import ZoneInfo

import requests

LOGGER = logging.getLogger(__name__)


class AnalyticsNotConfigured(RuntimeError):
    """Raised when an optional analytics provider has no credentials."""


class AnalyticsProviderError(RuntimeError):
    """Raised when an analytics provider cannot return a valid response."""


def _as_int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _as_float(value: Any) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _gql_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def _utc_bounds(start_date: date, end_date_exclusive: date, timezone_name: str) -> tuple[str, str]:
    local_timezone = ZoneInfo(timezone_name)
    start_local = datetime.combine(start_date, datetime_time.min, tzinfo=local_timezone)
    end_local = datetime.combine(end_date_exclusive, datetime_time.min, tzinfo=local_timezone)
    start_utc = start_local.astimezone(UTC).isoformat().replace("+00:00", "Z")
    end_utc = end_local.astimezone(UTC).isoformat().replace("+00:00", "Z")
    return start_utc, end_utc


def _local_date(value: Any, timezone_name: str) -> str | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(ZoneInfo(timezone_name)).date().isoformat()


def _sum_field(row: dict[str, Any], field: str) -> int:
    summary = row.get("sum") or {}
    return _as_int(summary.get(field))


def _is_page_path(path: Any) -> bool:
    if not isinstance(path, str) or not path.startswith("/"):
        return False
    if path in {"/healthz", "/readyz", "/robots.txt", "/sitemap.xml", "/favicon.ico"}:
        return False
    return not path.startswith(("/static/", "/api/", "/cdn-cgi/"))


class _TTLCache:
    def __init__(self, ttl_seconds: int):
        self.ttl_seconds = max(0, int(ttl_seconds))
        self._items: dict[str, tuple[float, Any]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Any | None:
        if self.ttl_seconds <= 0:
            return None
        now = time.monotonic()
        with self._lock:
            item = self._items.get(key)
            if item is None:
                return None
            expires_at, value = item
            if expires_at <= now:
                self._items.pop(key, None)
                return None
            return value

    def set(self, key: str, value: Any) -> None:
        if self.ttl_seconds <= 0:
            return
        with self._lock:
            self._items[key] = (time.monotonic() + self.ttl_seconds, value)


class CloudflareAnalyticsClient:
    """Client for Cloudflare's zone-scoped GraphQL Analytics API."""

    endpoint = "https://api.cloudflare.com/client/v4/graphql"

    def __init__(
        self,
        *,
        token: str,
        zone_id: str,
        hostname: str,
        timezone_name: str = "Asia/Shanghai",
        timeout_seconds: float = 10.0,
        cache_seconds: int = 300,
        max_lookback_days: int = 7,
        session: requests.Session | None = None,
    ):
        self.token = token.strip()
        self.zone_id = zone_id.strip()
        self.hostname = hostname.strip().lower()
        self.timezone_name = timezone_name
        self.timeout_seconds = timeout_seconds
        self.max_lookback_days = max(1, int(max_lookback_days))
        self.session = session or requests.Session()
        self.cache = _TTLCache(cache_seconds)

    @property
    def configured(self) -> bool:
        return bool(self.token and self.zone_id and self.hostname)

    def _filter(self, start_utc: str, end_utc: str) -> str:
        # Keep the result focused on navigational GET requests.  Static assets,
        # internal health checks, and API calls are not useful as page rows.
        return (
            "{"
            f"datetime_geq: {_gql_string(start_utc)}, "
            f"datetime_lt: {_gql_string(end_utc)}, "
            f"requestSource: {_gql_string('eyeball')}, "
            f"clientRequestHTTPHost: {_gql_string(self.hostname)}, "
            f"clientRequestHTTPMethodName: {_gql_string('GET')}, "
            "AND: ["
            f"{{clientRequestPath_notlike: {_gql_string('/static/%')}}}, "
            f"{{clientRequestPath_notlike: {_gql_string('/api/%')}}}, "
            f"{{clientRequestPath_notlike: {_gql_string('/cdn-cgi/%')}}}"
            "]"
            "}"
        )

    def _query(self, query: str, *, log_errors: bool = True) -> dict[str, Any]:
        if not self.configured:
            raise AnalyticsNotConfigured("Cloudflare Analytics 尚未配置。")
        try:
            response = self.session.post(
                self.endpoint,
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
                json={"query": query},
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError) as exc:
            LOGGER.exception("Cloudflare analytics request failed")
            raise AnalyticsProviderError("Cloudflare Analytics 请求失败。") from exc
        errors = payload.get("errors")
        if errors:
            log = LOGGER.error if log_errors else LOGGER.warning
            log("Cloudflare analytics GraphQL errors: %s", errors)
            raise AnalyticsProviderError(
                "Cloudflare Analytics 查询失败，请检查 Token 权限和 Zone ID。"
            )
        try:
            zones = payload["data"]["viewer"]["zones"]
            return zones[0]
        except (KeyError, IndexError, TypeError) as exc:
            raise AnalyticsProviderError("Cloudflare Analytics 返回了无法识别的数据。") from exc

    def _core_query(self, gql_filter: str) -> str:
        return f"""
        query AnalyticsOverview {{
          viewer {{
            zones(filter: {{zoneTag: {_gql_string(self.zone_id)}}}) {{
              daily: httpRequestsAdaptiveGroups(limit: 5000, filter: {gql_filter}) {{
                count
                sum {{ visits edgeResponseBytes }}
                dimensions {{ datetimeHour }}
              }}
              pages: httpRequestsAdaptiveGroups(limit: 5000, filter: {gql_filter}) {{
                count
                sum {{ visits edgeResponseBytes }}
                dimensions {{ clientRequestPath }}
              }}
              countries: httpRequestsAdaptiveGroups(limit: 5000, filter: {gql_filter}) {{
                count
                sum {{ visits }}
                dimensions {{ clientCountryName }}
              }}
            }}
          }}
        }}
        """

    def _referrer_query(self, gql_filter: str) -> str:
        return f"""
        query AnalyticsReferrers {{
          viewer {{
            zones(filter: {{zoneTag: {_gql_string(self.zone_id)}}}) {{
              referrers: httpRequestsAdaptiveGroups(limit: 5000, filter: {gql_filter}) {{
                count
                sum {{ visits }}
                dimensions {{ clientRefererHost }}
              }}
            }}
          }}
        }}
        """

    def overview(self, start_date: date, end_date_exclusive: date) -> dict[str, Any]:
        if not self.configured:
            raise AnalyticsNotConfigured("Cloudflare Analytics 尚未配置。")
        cache_key = f"{start_date.isoformat()}:{end_date_exclusive.isoformat()}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached
        result = self._empty_result()
        available_start = end_date_exclusive - timedelta(days=self.max_lookback_days)
        query_start = max(start_date, available_start)
        if query_start > start_date:
            result["notes"].append(
                f"Cloudflare 当前 Zone 仅保留最近约 {self.max_lookback_days} 天数据；"
                "更早日期已跳过。"
            )
        referrers_available = True
        cursor = query_start
        while cursor < end_date_exclusive:
            day_end = min(cursor + timedelta(days=1), end_date_exclusive)
            start_utc, end_utc = _utc_bounds(cursor, day_end, self.timezone_name)
            gql_filter = self._filter(start_utc, end_utc)

            # Cloudflare limits this zone's GraphQL time range to one day.
            zone = self._query(self._core_query(gql_filter))
            self._merge(result, self._normalise(zone, cursor, day_end))

            # Some zones/plans expose the core metrics but deny the referrer
            # dimension. Keep the rest of the report usable in that case.
            if referrers_available:
                try:
                    referrer_zone = self._query(self._referrer_query(gql_filter), log_errors=False)
                except AnalyticsProviderError:
                    referrers_available = False
                    LOGGER.warning(
                        "Cloudflare referrer analytics unavailable; continuing without referrers"
                    )
                else:
                    referrer_result = self._normalise(referrer_zone, cursor, day_end)
                    self._merge_group(result, "referrers", referrer_result["referrers"])
            cursor = day_end

        if not referrers_available:
            result["notes"].append(
                "当前 Cloudflare Zone 不提供来源网站字段，referrers 为空；"
                "可在 Cloudflare 控制台查看来源。"
            )
        self.cache.set(cache_key, result)
        return result

    @staticmethod
    def _empty_result() -> dict[str, Any]:
        return {
            "totals": {"requests": 0, "visits": 0, "bytes": 0},
            "daily": [],
            "pages": [],
            "referrers": [],
            "countries": [],
            "notes": [
                "requests 为 Cloudflare 边缘统计中符合筛选条件的 GET 请求，不等同于页面点击。",
                "visits 使用 Cloudflare 的访问定义；同一访问可能包含多个页面浏览。",
                "页面、来源和国家是聚合数据，不能识别个人。",
            ],
        }

    @staticmethod
    def _merge_group(result: dict[str, Any], field: str, items: list[dict[str, Any]]) -> None:
        grouped = {item["value"]: item for item in result[field]}
        for item in items:
            current = grouped.setdefault(
                item["value"], {"value": item["value"], "requests": 0, "visits": 0}
            )
            current["requests"] += item["requests"]
            current["visits"] += item["visits"]
        result[field] = sorted(
            grouped.values(),
            key=lambda item: (item["requests"], item["visits"]),
            reverse=True,
        )[:100]

    @classmethod
    def _merge(cls, result: dict[str, Any], chunk: dict[str, Any]) -> None:
        for field in result["totals"]:
            result["totals"][field] += chunk["totals"][field]
        daily = {item["date"]: item for item in result["daily"]}
        for item in chunk["daily"]:
            current = daily.setdefault(
                item["date"],
                {"date": item["date"], "requests": 0, "visits": 0, "bytes": 0},
            )
            current["requests"] += item["requests"]
            current["visits"] += item["visits"]
            current["bytes"] += item["bytes"]
        result["daily"] = [daily[key] for key in sorted(daily)]
        for field in ("pages", "referrers", "countries"):
            cls._merge_group(result, field, chunk[field])

    def _normalise(
        self, zone: dict[str, Any], start_date: date, end_date_exclusive: date
    ) -> dict[str, Any]:
        daily_map: dict[str, dict[str, int]] = defaultdict(
            lambda: {"requests": 0, "visits": 0, "bytes": 0}
        )
        for row in zone.get("daily", []):
            dimensions = row.get("dimensions") or {}
            day = _local_date(dimensions.get("datetimeHour"), self.timezone_name)
            if day is None:
                continue
            current = daily_map[day]
            current["requests"] += _as_int(row.get("count"))
            current["visits"] += _sum_field(row, "visits")
            current["bytes"] += _sum_field(row, "edgeResponseBytes")

        daily = [
            {"date": day, **values}
            for day, values in sorted(daily_map.items())
            if start_date.isoformat() <= day < end_date_exclusive.isoformat()
        ]

        def grouped(rows: list[dict[str, Any]], dimension: str, *, direct_label: str):
            output = []
            for row in rows:
                value = (row.get("dimensions") or {}).get(dimension) or direct_label
                if dimension == "clientRequestPath" and not _is_page_path(value):
                    continue
                output.append(
                    {
                        "value": value,
                        "requests": _as_int(row.get("count")),
                        "visits": _sum_field(row, "visits"),
                    }
                )
            output.sort(key=lambda item: (item["requests"], item["visits"]), reverse=True)
            return output[:100]

        totals = {
            "requests": sum(item["requests"] for item in daily),
            "visits": sum(item["visits"] for item in daily),
            "bytes": sum(item["bytes"] for item in daily),
        }
        return {
            "totals": totals,
            "daily": daily,
            "pages": grouped(zone.get("pages", []), "clientRequestPath", direct_label="(unknown)"),
            "referrers": grouped(
                zone.get("referrers", []),
                "clientRefererHost",
                direct_label="(direct or hidden)",
            ),
            "countries": grouped(
                zone.get("countries", []),
                "clientCountryName",
                direct_label="(unknown)",
            ),
            "notes": [
                "requests 为 Cloudflare 边缘统计中符合筛选条件的 GET 请求，不等同于页面点击。",
                "visits 使用 Cloudflare 的访问定义；同一访问可能包含多个页面浏览。",
                "页面、来源和国家是聚合数据，不能识别个人。",
            ],
        }


class SearchConsoleClient:
    """Google Search Console Search Analytics client using OAuth refresh tokens."""

    token_endpoint = "https://oauth2.googleapis.com/token"
    api_endpoint = "https://www.googleapis.com/webmasters/v3/sites/{site}/searchAnalytics/query"
    allowed_dimensions = {"date", "page", "query", "country", "device", "searchAppearance"}

    def __init__(
        self,
        *,
        site_url: str,
        client_id: str = "",
        client_secret: str = "",
        refresh_token: str = "",
        access_token: str = "",
        timeout_seconds: float = 10.0,
        cache_seconds: int = 300,
        session: requests.Session | None = None,
    ):
        self.site_url = site_url.strip()
        self.client_id = client_id.strip()
        self.client_secret = client_secret.strip()
        self.refresh_token = refresh_token.strip()
        self.access_token = access_token.strip()
        self.timeout_seconds = timeout_seconds
        self.session = session or requests.Session()
        self.cache = _TTLCache(cache_seconds)
        self._token_lock = threading.Lock()
        self._cached_access_token = ""
        self._token_expires_at = 0.0

    @property
    def configured(self) -> bool:
        direct_token = bool(self.site_url and self.access_token)
        refresh_flow = bool(
            self.site_url and self.client_id and self.client_secret and self.refresh_token
        )
        return direct_token or refresh_flow

    def _get_access_token(self) -> str:
        if self.access_token:
            return self.access_token
        if not self.configured:
            raise AnalyticsNotConfigured("Search Console 尚未配置。")
        now = time.monotonic()
        with self._token_lock:
            if self._cached_access_token and self._token_expires_at > now + 30:
                return self._cached_access_token
            try:
                response = self.session.post(
                    self.token_endpoint,
                    data={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "refresh_token": self.refresh_token,
                        "grant_type": "refresh_token",
                    },
                    timeout=self.timeout_seconds,
                )
                response.raise_for_status()
                payload = response.json()
                token = str(payload.get("access_token", ""))
                expires_in = _as_int(payload.get("expires_in"))
            except (requests.RequestException, ValueError) as exc:
                LOGGER.exception("Search Console token refresh failed")
                raise AnalyticsProviderError("Search Console 授权刷新失败。") from exc
            if not token:
                raise AnalyticsProviderError("Search Console 没有返回访问令牌。")
            self._cached_access_token = token
            self._token_expires_at = now + max(60, expires_in)
            return token

    def query(
        self,
        start_date: date,
        end_date_exclusive: date,
        dimensions: list[str],
        row_limit: int = 25000,
    ) -> dict[str, Any]:
        if not self.configured:
            raise AnalyticsNotConfigured("Search Console 尚未配置。")
        invalid = [item for item in dimensions if item not in self.allowed_dimensions]
        if invalid or not dimensions or len(set(dimensions)) != len(dimensions):
            raise AnalyticsProviderError("Search Console 维度参数无效。")
        end_date = end_date_exclusive - timedelta(days=1)
        cache_key = (
            f"{start_date.isoformat()}:{end_date.isoformat()}:"
            f"{','.join(dimensions)}:{row_limit}"
        )
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached
        site = quote(self.site_url, safe="")
        try:
            response = self.session.post(
                self.api_endpoint.format(site=site),
                headers={
                    "Authorization": f"Bearer {self._get_access_token()}",
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
                json={
                    "startDate": start_date.isoformat(),
                    "endDate": end_date.isoformat(),
                    "type": "web",
                    "dimensions": dimensions,
                    "rowLimit": max(1, min(int(row_limit), 25000)),
                },
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError) as exc:
            LOGGER.exception("Search Console query failed")
            raise AnalyticsProviderError("Search Console 查询失败，请检查授权和资源权限。") from exc
        if "error" in payload:
            LOGGER.error("Search Console API error: %s", payload.get("error"))
            raise AnalyticsProviderError("Search Console 返回了查询错误。")
        rows = []
        for row in payload.get("rows", []):
            keys = row.get("keys") or []
            item = {
                "clicks": _as_float(row.get("clicks")),
                "impressions": _as_float(row.get("impressions")),
                "ctr": _as_float(row.get("ctr")),
                "position": _as_float(row.get("position")),
                "keys": keys,
            }
            item.update(
                {dimension: value for dimension, value in zip(dimensions, keys, strict=False)}
            )
            rows.append(item)
        result = {
            "site_url": self.site_url,
            "dimensions": dimensions,
            "rows": rows,
            "notes": [
                "Search Console 只代表 Google 搜索流量，不代表全部网站访问。",
                "Google 数据通常会有延迟，最近日期可能尚未完整。",
            ],
        }
        self.cache.set(cache_key, result)
        return result
