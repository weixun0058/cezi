"""Central SEO metadata and trusted public URL generation."""

from __future__ import annotations

from dataclasses import dataclass, replace
from urllib.parse import urlsplit

from .content import SLUG_PATTERN, Article

SITE_NAME = "Wise Oracle"

OG_LOCALES = {
    "en": "en_US",
    "zh-Hans": "zh_CN",
    "zh-Hant": "zh_TW",
}

CORE_ALTERNATES = {
    "home": {
        "en": "/",
        "zh-Hans": "/zh-hans",
        "zh-Hant": "/zh-hant",
        "x-default": "/",
    },
    "oracle": {
        "en": "/ask-oracle",
        "zh-Hans": "/zh-hans/divination",
        "zh-Hant": "/zh-hant/divination",
        "x-default": "/ask-oracle",
    },
    "almanac": {
        "en": "/daily-almanac",
        "zh-Hans": "/zh-hans/almanac",
        "zh-Hant": "/zh-hant/almanac",
        "x-default": "/daily-almanac",
    },
    "bazi": {
        "en": "/birth-chart-reading",
        "zh-Hans": "/zh-hans/bazi",
        "zh-Hant": "/zh-hant/bazi",
        "x-default": "/birth-chart-reading",
    },
}


@dataclass(frozen=True)
class SEOPage:
    title: str
    description: str
    canonical_path: str
    language: str
    alternate_group: str | None = None
    indexable: bool = True
    og_type: str = "website"


PAGE_SPECS = {
    "en.home": SEOPage(
        "Wise Oracle — Chinese Cultural Divination & Almanac",
        "Draw an oracle sign, read the daily Chinese almanac, and reflect on your "
        "birth chart through traditional Chinese cultural wisdom.",
        "/",
        "en",
        "home",
    ),
    "en.oracle": SEOPage(
        "Ask the Oracle — Free Chinese Oracle Sign Reading",
        "Hold a question in mind and draw a Zhuge Oracle sign for cultural "
        "reflection. Not fortune telling — a mirror for self-examination.",
        "/ask-oracle",
        "en",
        "oracle",
    ),
    "en.almanac": SEOPage(
        "Daily Chinese Almanac — Favorable Activities & Solar Terms",
        "Explore the daily Chinese almanac: traditional activity indications, "
        "lunar date, solar terms, zodiac, directions, and cultural context.",
        "/daily-almanac",
        "en",
        "almanac",
    ),
    "en.bazi": SEOPage(
        "Birth Chart Reading — BaZi Cultural Self-Reflection",
        "Explore your BaZi birth chart as a cultural framework for self-reflection. "
        "Not destiny prediction.",
        "/birth-chart-reading",
        "en",
        "bazi",
    ),
    "en.articles": SEOPage(
        "Articles — Chinese Divination Culture & Almanac Traditions",
        "Essays on Chinese oracle signs, almanac traditions, and cultural "
        "self-reflection practices.",
        "/articles",
        "en",
        indexable=False,
    ),
    "en.privacy": SEOPage(
        "Privacy Policy — Wise Oracle",
        "How Wise Oracle handles your data: oracle queries, birth chart input, AI "
        "processing, cookies, and your rights.",
        "/privacy",
        "en",
    ),
    "en.terms": SEOPage(
        "Terms of Service — Wise Oracle",
        "Terms of service for Wise Oracle: acceptable use, no warranty, limitation "
        "of liability, and AI content disclaimer.",
        "/terms",
        "en",
    ),
    "en.disclaimer": SEOPage(
        "Disclaimer — Wise Oracle",
        "Wise Oracle disclaimer: all readings are for entertainment, cultural "
        "exploration, and self-reflection only. Not professional advice.",
        "/disclaimer",
        "en",
    ),
    "en.about": SEOPage(
        "About — Wise Oracle",
        "Wise Oracle offers traditional Chinese oracle signs, almanac references, "
        "and BaZi birth chart reflections for cultural self-examination.",
        "/about",
        "en",
    ),
    "en.contact": SEOPage(
        "Contact — Wise Oracle",
        "Contact Wise Oracle for questions, feedback, privacy inquiries, or support.",
        "/contact",
        "en",
    ),
    "zh-hans.home": SEOPage(
        "诸葛神算",
        "体验诸葛神算求签、每日黄历与八字文化解读，用于传统文化探索和自我反思。",
        "/zh-hans",
        "zh-Hans",
        "home",
    ),
    "zh-hans.huangli": SEOPage(
        "诸葛神算 - 传统黄历",
        "查看每日黄历、农历日期、节气与传统宜忌，作为中国传统文化参考。",
        "/zh-hans/almanac",
        "zh-Hans",
        "almanac",
    ),
    "zh-hans.suanshi": SEOPage(
        "诸葛神算 - 算事",
        "通过三字起签体验诸葛神算文化解读，用于自我反思，不代替现实决策。",
        "/zh-hans/divination",
        "zh-Hans",
        "oracle",
    ),
    "zh-hans.lunming": SEOPage(
        "诸葛神算 - 论命",
        "从传统八字文化视角阅读出生信息，用于文化探索和自我反思。",
        "/zh-hans/bazi",
        "zh-Hans",
        "bazi",
    ),
    "zh-hant.home": SEOPage(
        "諸葛神算",
        "體驗諸葛神算求籤、每日黃曆與八字文化解讀，用於傳統文化探索和自我反思。",
        "/zh-hant",
        "zh-Hant",
        "home",
    ),
    "zh-hant.huangli": SEOPage(
        "諸葛神算 - 傳統黃曆",
        "查看每日黃曆、農曆日期、節氣與傳統宜忌，作為中國傳統文化參考。",
        "/zh-hant/almanac",
        "zh-Hant",
        "almanac",
    ),
    "zh-hant.suanshi": SEOPage(
        "諸葛神算 - 算事",
        "透過三字起籤體驗諸葛神算文化解讀，用於自我反思，不代替現實決策。",
        "/zh-hant/divination",
        "zh-Hant",
        "oracle",
    ),
    "zh-hant.lunming": SEOPage(
        "諸葛神算 - 論命",
        "從傳統八字文化視角閱讀出生資訊，用於文化探索和自我反思。",
        "/zh-hant/bazi",
        "zh-Hant",
        "bazi",
    ),
}

SITEMAP_PATHS = (
    "/",
    "/ask-oracle",
    "/daily-almanac",
    "/birth-chart-reading",
    "/about",
    "/zh-hant",
    "/zh-hant/divination",
    "/zh-hant/almanac",
    "/zh-hant/bazi",
)


def absolute_public_url(base_url: str, path: str) -> str:
    """Join a validated site origin to one trusted, query-free public path."""
    if not isinstance(path, str) or not path.startswith("/") or "\\" in path:
        raise ValueError("public URL path must be an absolute path")
    parsed = urlsplit(path)
    if parsed.scheme or parsed.netloc or parsed.query or parsed.fragment or path.startswith("//"):
        raise ValueError("public URL path must not contain an origin, query, or fragment")
    return f"{base_url.rstrip('/')}{path}"


def _build_page_seo(base_url: str, page_key: str, spec: SEOPage) -> dict:
    alternates = {}
    if spec.alternate_group:
        alternates = {
            language: absolute_public_url(base_url, path)
            for language, path in CORE_ALTERNATES[spec.alternate_group].items()
        }

    canonical_url = absolute_public_url(base_url, spec.canonical_path)
    site_url = absolute_public_url(base_url, "/")
    json_ld = []
    if spec.indexable:
        if page_key == "en.home":
            json_ld.append(
                {
                    "@context": "https://schema.org",
                    "@type": "WebSite",
                    "name": SITE_NAME,
                    "url": site_url,
                    "inLanguage": "en",
                }
            )
        json_ld.append(
            {
                "@context": "https://schema.org",
                "@type": "WebPage",
                "name": spec.title,
                "description": spec.description,
                "url": canonical_url,
                "inLanguage": spec.language,
                "isPartOf": {
                    "@type": "WebSite",
                    "name": SITE_NAME,
                    "url": site_url,
                },
            }
        )

    return {
        "title": spec.title,
        "description": spec.description,
        "robots": "index,follow" if spec.indexable else "noindex,follow",
        "canonical_url": canonical_url,
        "alternates": alternates,
        "og_type": spec.og_type,
        "og_locale": OG_LOCALES[spec.language],
        "language": spec.language,
        "site_name": SITE_NAME,
        "json_ld": json_ld,
    }


def build_page_seo(base_url: str, page_key: str) -> dict:
    """Build request-independent SEO values for one registered HTML page."""
    try:
        spec = PAGE_SPECS[page_key]
    except KeyError as exc:
        raise KeyError(f"Unknown SEO page key: {page_key}") from exc
    return _build_page_seo(base_url, page_key, spec)


def build_articles_index_seo(base_url: str, *, has_articles: bool) -> dict:
    """Index the article hub only after it contains a public article."""
    spec = PAGE_SPECS["en.articles"]
    if has_articles:
        spec = replace(spec, indexable=True)
    return _build_page_seo(base_url, "en.articles", spec)


def build_article_seo(base_url: str, article: Article) -> dict:
    """Build canonical metadata and conservative structured data for an article."""
    canonical_path = f"/articles/{article.slug}"
    canonical_url = absolute_public_url(base_url, canonical_path)
    site_url = absolute_public_url(base_url, "/")
    title = f"{article.title} — {SITE_NAME}"
    web_page = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": title,
        "description": article.description,
        "url": canonical_url,
        "inLanguage": "en",
        "isPartOf": {
            "@type": "WebSite",
            "name": SITE_NAME,
            "url": site_url,
        },
    }
    article_graph = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": article.title,
        "description": article.description,
        "url": canonical_url,
        "mainEntityOfPage": canonical_url,
        "datePublished": article.published_at.isoformat(),
        "dateModified": (article.updated_at or article.published_at).isoformat(),
        "inLanguage": "en",
        "isPartOf": {
            "@type": "WebSite",
            "name": SITE_NAME,
            "url": site_url,
        },
    }
    return {
        "title": title,
        "description": article.description,
        "robots": "index,follow",
        "canonical_url": canonical_url,
        "alternates": {},
        "og_type": "article",
        "og_locale": OG_LOCALES["en"],
        "language": "en",
        "site_name": SITE_NAME,
        "json_ld": [web_page, article_graph],
    }


def build_sitemap_urls(base_url: str, *, article_slugs: tuple[str, ...] = ()) -> tuple[str, ...]:
    """Return the deliberately small, approved public sitemap URL set."""
    paths = list(SITEMAP_PATHS)
    if article_slugs:
        paths.append("/articles")
        for slug in article_slugs:
            if not SLUG_PATTERN.fullmatch(slug):
                raise ValueError("sitemap article slug is invalid")
            paths.append(f"/articles/{slug}")
    return tuple(absolute_public_url(base_url, path) for path in paths)
