/**
 * i18n 加载器
 *
 * 用途：从 dictionary.json 加载统一多语言字典，提供按 key 取值的接口。
 * 输入：language 代码（zh-hans / zh-hant / en / ja）
 * 输出：window.i18n 全局对象，含 t() 翻译函数、onReady() 就绪回调等
 *
 * 使用方式：
 *   // 1. HTML 中引入（无需 type="module"）
 *   <script src="/static/js/lang/i18n.js"></script>
 *
 *   // 2. 业务 JS 在初始化时等待字典就绪
 *   document.addEventListener('DOMContentLoaded', function() {
 *     i18n.onReady(function() {
 *       // 字典已就绪，可以安全调用 t()
 *       document.getElementById('btn').textContent = i18n.t('suanshi.calculate_btn');
 *     });
 *   });
 *
 *   // 3. 动态生成的字符串直接调用 t()
 *   setStatus(i18n.t('suanshi.status.querying_strokes'));
 *
 *   // 4. 模板插值
 *   i18n.t('lunming.correction_format', { minutes: 5 })  // "修正 5 分钟"
 *
 *   // 5. 切换语言（会重新触发所有 onReady 回调）
 *   i18n.setLanguage('zh-hant');  // 切换后需手动刷新或调用 applyTranslations
 *
 * 回退规则：
 *   1. 找不到 key → 控制台警告，返回 key 本身
 *   2. 当前语言的翻译为空字符串 → 回退到 source
 *   3. source 也缺失 → 返回 key
 *
 * 注意：
 *   - 本加载器不依赖任何第三方库，仅用 fetch + Promise
 *   - 不使用 ES Module 导出，避免非模块化 <script> 引入报错
 *   - 通过 window.i18n 全局对象暴露接口
 */

(function() {
  'use strict';

  let dictionary = null;
  let currentLang = 'zh-hans';
  const fallbackLang = 'zh-hans';
  const STORAGE_KEY = 'i18n_lang';
  const supportedLangs = ['zh-hans', 'zh-hant'];

  function normalizeLang(lang) {
    if (lang === 'zh-cn') return 'zh-hans';
    if (lang === 'zh-tw') return 'zh-hant';
    return supportedLangs.indexOf(lang) >= 0 ? lang : '';
  }

  function languageFromPath() {
    var path = location.pathname || '';
    for (var i = 0; i < supportedLangs.length; i++) {
      var prefix = '/' + supportedLangs[i];
      if (path === prefix || path.indexOf(prefix + '/') === 0) {
        return supportedLangs[i];
      }
    }
    return '';
  }

  // URL 语言前缀优先；无前缀时读取用户上次选择的语言。
  const pathLang = languageFromPath();
  if (pathLang) {
    currentLang = pathLang;
  }
  try {
    if (pathLang) {
      localStorage.setItem(STORAGE_KEY, pathLang);
    } else {
      const stored = normalizeLang(localStorage.getItem(STORAGE_KEY));
      if (stored) currentLang = stored;
    }
  } catch (e) {
    // localStorage 不可用，保持默认 zh-hans
  }

  // 字典加载 Promise（自动初始化）
  let readyPromise = null;

  /**
   * 加载 dictionary.json
   * @returns {Promise<Object>}
   */
  function loadDictionary() {
    if (readyPromise !== null) return readyPromise;

    readyPromise = fetch('/static/js/lang/dictionary.json')
      .then(function(response) {
        if (!response.ok) {
          throw new Error('i18n: 字典加载失败 (HTTP ' + response.status + ')');
        }
        return response.json();
      })
      .then(function(json) {
        dictionary = json;
        return dictionary;
      })
      .catch(function(error) {
        console.error('i18n: 字典加载异常', error);
        dictionary = {};
        return dictionary;
      });

    return readyPromise;
  }

  /**
   * 初始化 i18n（设置语言，触发字典加载）
   * 通常无需手动调用，本加载器会自动加载字典
   * @param {string} [lang] - 语言代码
   * @returns {Promise<void>}
   */
  function init(lang) {
    if (lang) currentLang = lang;
    return loadDictionary().then(function() {});
  }

  /**
   * 字典就绪回调
   * @param {Function} callback - 字典加载完成后执行
   * @returns {Promise<void>} 用于 async/await 场景
   */
  function onReady(callback) {
    return loadDictionary().then(function() {
      if (typeof callback === 'function') callback();
    });
  }

  /**
   * 设置当前语言（不重新加载字典，不持久化）
   * 仅用于运行时切换，刷新后失效
   * @param {string} lang
   */
  function setLanguage(lang) {
    currentLang = lang;
  }

  /**
   * 切换语言并持久化到 localStorage
   * 切换后刷新页面，确保所有静态/动态内容一致使用新语言
   * @param {string} lang - 语言代码（zh-hans / zh-hant / en / ja）
   */
  function switchLanguage(lang) {
    try {
      localStorage.setItem(STORAGE_KEY, lang);
    } catch (e) {
      // localStorage 不可用，忽略
    }
    currentLang = lang;
    // 刷新页面，确保动态生成的内容也使用新语言
    location.reload();
  }

  /**
   * 获取当前语言
   * @returns {string}
   */
  function getLanguage() {
    return currentLang;
  }

  /**
   * 在 API URL 上自动附加当前语言参数
   * 用于 fetch 调用，让后端 before_request 钩子能感知语言
   * @param {string} url - 原始 API URL（如 '/api/huangli?date=2026-01-01'）
   * @returns {string} 附加了 lang 参数的 URL
   */
  function apiUrl(url) {
    var sep = url.indexOf('?') >= 0 ? '&' : '?';
    return url + sep + 'lang=' + encodeURIComponent(currentLang);
  }

  /**
   * 翻译函数
   * @param {string} key - 字典中的语义 key（如 "suanshi.calculate_btn"）
   * @param {Object} [params] - 模板插值参数（如 { minutes: 5 }）
   * @returns {string} 翻译后的文本；找不到时返回 key
   */
  function t(key, params) {
    if (!dictionary) {
      console.warn('i18n: 字典尚未加载，调用 t("' + key + '") 返回 key 本身。请用 i18n.onReady() 包裹。');
      return key;
    }

    const entry = dictionary[key];
    if (!entry) {
      console.warn('i18n: 找不到 key "' + key + '"');
      return key;
    }

    // 优先取当前语言的翻译
    let text = '';
    if (entry.translations && entry.translations[currentLang]) {
      text = entry.translations[currentLang];
    }

    // 当前语言为空 → 回退到 source
    if (!text && entry.source) {
      text = entry.source;
    }

    // source 也空 → 返回 key
    if (!text) {
      return key;
    }

    // 模板插值
    if (params && typeof text === 'string') {
      Object.keys(params).forEach(function(name) {
        text = text.replace(new RegExp('\\{' + name + '\\}', 'g'), params[name]);
      });
    }

    return text;
  }

  /**
   * 获取字典中某个 key 的原始条目（含 source 和 translations）
   * 用于调试或特殊场景
   * @param {string} key
   * @returns {Object|null}
   */
  function getEntry(key) {
    if (!dictionary) return null;
    return dictionary[key] || null;
  }

  /**
   * 列出字典中所有 key（用于调试）
   * @returns {string[]}
   */
  function listKeys() {
    if (!dictionary) return [];
    return Object.keys(dictionary).filter(function(k) {
      return !k.startsWith('_');
    });
  }

  /**
   * 扫描 [data-i18n] 元素并替换 textContent
   * 用于 HTML 模板中的静态字符串翻译
   *
   * 支持的属性：
   *   data-i18n             - 翻译到 textContent
   *   data-i18n-placeholder - 翻译到 placeholder
   *   data-i18n-title       - 翻译到 title
   *   data-i18n-aria-label  - 翻译到 aria-label
   *
   * @param {Element} [root=document.body] - 扫描根节点
   */
  function applyTranslations(root) {
    const scope = root || document.body;

    function parseParams(el) {
      const params = {};
      const paramsAttr = el.getAttribute('data-i18n-params');
      if (paramsAttr) {
        paramsAttr.split(',').forEach(function(pair) {
          const idx = pair.indexOf(':');
          if (idx > 0) {
            params[pair.slice(0, idx).trim()] = pair.slice(idx + 1).trim();
          }
        });
      }
      return params;
    }

    // textContent
    scope.querySelectorAll('[data-i18n]').forEach(function(el) {
      el.textContent = t(el.getAttribute('data-i18n'), parseParams(el));
    });

    // placeholder
    scope.querySelectorAll('[data-i18n-placeholder]').forEach(function(el) {
      el.setAttribute('placeholder', t(el.getAttribute('data-i18n-placeholder'), parseParams(el)));
    });

    // title
    scope.querySelectorAll('[data-i18n-title]').forEach(function(el) {
      el.setAttribute('title', t(el.getAttribute('data-i18n-title'), parseParams(el)));
    });

    // aria-label
    scope.querySelectorAll('[data-i18n-aria-label]').forEach(function(el) {
      el.setAttribute('aria-label', t(el.getAttribute('data-i18n-aria-label'), parseParams(el)));
    });
  }

  // 暴露到 window
  window.i18n = {
    init: init,
    onReady: onReady,
    t: t,
    setLanguage: setLanguage,
    switchLanguage: switchLanguage,
    getLanguage: getLanguage,
    apiUrl: apiUrl,
    getEntry: getEntry,
    listKeys: listKeys,
    applyTranslations: applyTranslations,
    // 暴露 ready Promise 用于 await 场景
    ready: function() { return loadDictionary(); }
  };

  // 自动开始加载字典（不等 DOMContentLoaded，尽早加载）
  loadDictionary();
})();
