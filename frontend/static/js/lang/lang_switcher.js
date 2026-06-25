/**
 * 语言切换器
 *
 * 用途：在页面右上角渲染简/繁切换按钮，点击后切换语言并刷新页面。
 * 依赖：i18n.js（必须在本脚本之前引入）
 *
 * 使用方式：
 *   1. HTML 中放置容器：<div id="lang-switcher" class="lang-switcher"></div>
 *   2. 引入本脚本：<script src="/static/js/lang/lang_switcher.js"></script>
 *   3. 无需其他初始化代码，本脚本自动渲染
 */
(function() {
  'use strict';

  // 支持的语言列表（P1 阶段只做简繁）
  var LANGS = [
    { code: 'zh-hans', label: '简' },
    { code: 'zh-hant', label: '繁' }
  ];

  /**
   * 渲染切换按钮到 #lang-switcher 容器
   */
  function render() {
    var container = document.getElementById('lang-switcher');
    if (!container) return;

    var current = (typeof i18n !== 'undefined' && i18n.getLanguage) ? i18n.getLanguage() : 'zh-hans';

    var html = '';
    for (var i = 0; i < LANGS.length; i++) {
      var lang = LANGS[i];
      var active = lang.code === current ? ' active' : '';
      html += '<button type="button" class="lang-btn' + active + '" data-lang="' + lang.code + '">' + lang.label + '</button>';
    }
    container.innerHTML = html;

    // 绑定点击事件
    var buttons = container.querySelectorAll('.lang-btn');
    for (var j = 0; j < buttons.length; j++) {
      buttons[j].addEventListener('click', function() {
        var lang = this.getAttribute('data-lang');
        if (lang === current) return;

        // 持久化语言偏好到 localStorage
        try { localStorage.setItem('i18n_lang', lang); } catch (e) {}

        // 替换 URL 中的语言前缀（如 /zh-hans/almanac → /zh-hant/almanac）
        var path = location.pathname;
        var matched = false;
        for (var k = 0; k < LANGS.length; k++) {
          var prefix = '/' + LANGS[k].code;
          if (path === prefix || path.indexOf(prefix + '/') === 0) {
            location.href = '/' + lang + path.slice(prefix.length);
            matched = true;
            break;
          }
        }
        // 当前 URL 没有语言前缀（异常情况），回退到刷新
        if (!matched) location.reload();
      });
    }
  }

  // 注入切换器样式（避免改动 CSS 文件）
  var style = document.createElement('style');
  style.textContent = [
    '.lang-switcher { display: inline-flex; gap: 4px; margin-left: 12px; vertical-align: middle; }',
    '.lang-btn {',
    '  padding: 2px 10px;',
    '  border: 1px solid #8b7355;',
    '  background: transparent;',
    '  color: #8b7355;',
    '  cursor: pointer;',
    '  font-size: 13px;',
    '  line-height: 1.4;',
    '  border-radius: 3px;',
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
