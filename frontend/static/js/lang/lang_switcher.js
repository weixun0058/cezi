/**
 * 语言切换器
 *
 * 用途：在页面右上角渲染 EN/简/繁切换链接，并在中英文对应功能页之间跳转。
 * 依赖：无。中文页面仍由 i18n.js 根据 URL 前缀加载简体或繁体文案。
 *
 * 使用方式：
 *   1. HTML 中放置容器：<div id="lang-switcher" class="lang-switcher"></div>
 *   2. 引入本脚本：<script src="/static/js/lang/lang_switcher.js"></script>
 *   3. 无需其他初始化代码，本脚本自动渲染
 */
(function() {
  'use strict';

  // 三语入口。英文使用无前缀 URL，中文使用语言前缀 URL。
  var LANGS = [
    { code: 'zh-hans', label: '简' },
    { code: 'zh-hant', label: '繁' },
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
  var style = document.createElement('style');
  style.textContent = [
    '.lang-switcher { display: inline-flex; gap: 4px; margin-left: 12px; vertical-align: middle; }',
    '.lang-btn {',
    '  display: inline-block;',
    '  padding: 2px 10px;',
    '  border: 1px solid #8b7355;',
    '  background: transparent;',
    '  color: #8b7355;',
    '  cursor: pointer;',
    '  font-size: 13px;',
    '  line-height: 1.4;',
    '  border-radius: 3px;',
    '  text-decoration: none;',
    '  transition: all 0.2s;',
    '}',
    '.lang-btn.active { background: #8b7355; color: #f5e6d3; }',
    '.lang-btn:hover { opacity: 0.8; }'
  ].join('\n');
  document.head.appendChild(style);

  // DOM 就绪后渲染
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', render);
  } else {
    render();
  }
})();
