/**
 * 语言切换器
 *
 * 用途：在页面右上角渲染 中/EN 切换链接，并在中英文对应功能页之间跳转。
 * 依赖：无。中文页面仍由 i18n.js 根据 URL 前缀加载简体或繁体文案。
 *
 * 说明：
 *   - 仅展示"中"（繁体）和"EN"两个按钮。简体页面路由保留（/zh-hans/* 可直接访问），
 *     但不在切换器中显示入口。
 *   - "中"按钮固定指向繁体（zh-hant），不改变后端/API 的兼容默认语言。
 *
 * 使用方式：
 *   1. HTML 中放置容器：<div id="lang-switcher" class="lang-switcher"></div>
 *   2. 引入本脚本：<script src="/static/js/lang/lang_switcher.js"></script>
 *   3. 无需其他初始化代码，本脚本自动渲染
 */
(function() {
  'use strict';

  // 语言入口。只展示中文（繁体）和英文。简体页面路由保留但不显示按钮。
  var LANGS = [
    { code: 'zh-hant', label: '中' },
    { code: 'en', label: 'EN' }
  ];

  var ENGLISH_PAGE_TO_CHINESE_PAGE = {
    '/ask-oracle': 'divination',
    '/daily-almanac': 'almanac',
    '/birth-chart-reading': 'bazi'
  };

  var CHINESE_PAGE_TO_ENGLISH_PAGE = {
    'divination': '/ask-oracle',
    'almanac': '/daily-almanac',
    'bazi': '/birth-chart-reading'
  };

  function currentLanguage(path) {
    if (path === '/zh-hans' || path.indexOf('/zh-hans/') === 0) return 'zh-hans';
    if (path === '/zh-hant' || path.indexOf('/zh-hant/') === 0) return 'zh-hant';
    return 'en';
  }

  function chinesePageFromPath(path) {
    var match = path.match(/^\/(?:zh-hans|zh-hant)(?:\/([^/]+))?/);
    return match && match[1] ? match[1] : '';
  }

  function targetPath(language, currentPath) {
    var current = currentLanguage(currentPath);

    if (language === 'en') {
      if (current === 'en') return currentPath;
      return CHINESE_PAGE_TO_ENGLISH_PAGE[chinesePageFromPath(currentPath)] || '/';
    }

    if (current === 'en') {
      var chinesePage = ENGLISH_PAGE_TO_CHINESE_PAGE[currentPath];
      return '/' + language + (chinesePage ? '/' + chinesePage : '');
    }

    var page = chinesePageFromPath(currentPath);
    return '/' + language + (page ? '/' + page : '');
  }

  /**
   * 渲染切换按钮到 #lang-switcher 容器
   */
  function render() {
    var container = document.getElementById('lang-switcher');
    if (!container) return;

    var path = location.pathname;
    var current = currentLanguage(path);

    var html = '';
    for (var i = 0; i < LANGS.length; i++) {
      var lang = LANGS[i];
      var active = lang.code === current ? ' active' : '';
      var ariaCurrent = lang.code === current ? ' aria-current="page"' : '';
      html += '<a class="lang-btn' + active + '" href="' + targetPath(lang.code, path) + '"' +
        ariaCurrent + ' aria-label="Switch to ' + lang.label + '">' + lang.label + '</a>';
    }
    container.innerHTML = html;
  }

  // 注入切换器样式（避免改动 CSS 文件）
  // 样式同时适配中文 header（深棕底）和英文 header（白底）：
  //   - 未激活：按所在 header 设置文字色（中文米黄、英文深棕）
  //   - 激活态：米黄底 + 深棕字（两套页面统一，优先级最高）
  var style = document.createElement('style');
  style.textContent = [
    '.lang-switcher { display: inline-flex; gap: 6px; margin-left: 12px; vertical-align: middle; align-items: center; }',
    '.lang-btn {',
    '  display: inline-block;',
    '  padding: 3px 12px;',
    '  border: 1px solid currentColor;',
    '  background: transparent;',
    '  cursor: pointer;',
    '  font-size: 14px;',
    '  font-family: inherit;',
    '  line-height: 1.4;',
    '  border-radius: 3px;',
    '  text-decoration: none;',
    '  opacity: 0.75;',
    '  transition: opacity 0.2s, background 0.2s, color 0.2s;',
    '}',
    '.lang-btn:hover { opacity: 1; }',
    '.cn-header .lang-btn { color: #f4e4bc; }',
    '.en-header .lang-btn { color: var(--wo-text-soft, #6b5d52); }',
    '.lang-btn.active {',
    '  background: #f4e4bc;',
    '  color: #2c1810;',
    '  border-color: #f4e4bc;',
    '  opacity: 1;',
    '  font-weight: 600;',
    '}'
  ].join('\n');
  document.head.appendChild(style);

  // DOM 就绪后渲染
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', render);
  } else {
    render();
  }
})();
