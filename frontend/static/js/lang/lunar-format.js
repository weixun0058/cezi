/**
 * 农历数字与日期格式化共享模块
 *
 * 用途：把 lunar.js 的阿拉伯数字月份/日期转成项目统一的汉字表示，
 *      并通过 i18n 字典支持简繁双语。两个 handler（黄历页与命盘页）
 *      共用同一套纯函数，避免重复定义与漂移。
 * 输入：阿拉伯数字（月份、日期，月份可为负数表示闰月）
 * 输出：window.LunarFormat 全局对象，暴露 tr / localizedDigit /
 *      numberToChinese / localizedLunarMonth / localizedLunarDay 等。
 *
 * 设计约束：
 *   - 不使用 ES Module 导出，沿用 i18n.js 的 IIFE + window 全局风格
 *   - 所有函数在 i18n 字典未加载时仍能返回当前语言的回退文案
 *   - 不修改任何 DOM，纯函数便于测试
 */

(function () {
    'use strict';

    /**
     * 返回当前生效语言；i18n 未加载时退回简体。
     */
    function currentLanguage() {
        return (typeof i18n !== 'undefined' && i18n.getLanguage) ? i18n.getLanguage() : 'zh-hans';
    }

    /**
     * 在简体/繁体回退文案间选择。
     */
    function localFallback(hans, hant) {
        return currentLanguage() === 'zh-hant' ? hant : hans;
    }

    /**
     * 用 params 替换 text 中的 {name} 占位符，与 i18n.t 的插值规则保持一致。
     */
    function applyParams(text, params) {
        if (!params || typeof text !== 'string') return text;
        return Object.keys(params).reduce(function (acc, name) {
            return acc.replace(new RegExp('\\{' + name + '\\}', 'g'), params[name]);
        }, text);
    }

    /**
     * 翻译 key；若 i18n 不可用或 key 不存在，返回当前语言的回退文案。
     * @param {string} key - i18n 字典 key
     * @param {string} hans - 简体回退
     * @param {string} hant - 繁体回退
     * @param {Object} [params] - 模板参数，与 i18n.t 的第二参数一致
     */
    function tr(key, hans, hant, params) {
        const fallback = applyParams(localFallback(hans, hant), params);
        if (typeof i18n === 'undefined' || !i18n.t || !i18n.getEntry || !i18n.getEntry(key)) {
            return fallback;
        }
        return params ? i18n.t(key, params) : i18n.t(key);
    }

    // 数字 0-10 的 i18n key 与简繁回退；索引即数字值
    const digitKeys = [
        ['calendar.digit.zero', '零', '零'],
        ['calendar.digit.one', '一', '一'],
        ['calendar.digit.two', '二', '二'],
        ['calendar.digit.three', '三', '三'],
        ['calendar.digit.four', '四', '四'],
        ['calendar.digit.five', '五', '五'],
        ['calendar.digit.six', '六', '六'],
        ['calendar.digit.seven', '七', '七'],
        ['calendar.digit.eight', '八', '八'],
        ['calendar.digit.nine', '九', '九'],
        ['calendar.digit.ten', '十', '十']
    ];

    /**
     * 把单个数字转成当前语言的汉字（0-10），超出范围返回阿拉伯数字字符串。
     */
    function localizedDigit(num) {
        const item = digitKeys[num];
        return item ? tr(item[0], item[1], item[2]) : String(num);
    }

    /**
     * 将阿拉伯数字转成传统汉字表示（≤99）。
     * @param {number} num - 阿拉伯数字
     * @return {string} 汉字表示
     */
    function numberToChinese(num) {
        if (num <= 10) {
            return localizedDigit(num);
        } else if (num < 20) {
            return tr('calendar.digit.ten', '十', '十') + (num > 10 ? localizedDigit(num - 10) : '');
        } else if (num < 100) {
            return localizedDigit(Math.floor(num / 10))
                + tr('calendar.digit.ten', '十', '十')
                + (num % 10 > 0 ? localizedDigit(num % 10) : '');
        }
        return num.toString();
    }

    /**
     * 将农历月份转成汉字表示（正月、腊月、闰二月等）。
     * @param {number} month - 月份，负数表示闰月
     * @return {string} 汉字表示
     */
    function localizedLunarMonth(month) {
        const isLeap = month < 0;
        const absMonth = Math.abs(month);
        let result = isLeap ? tr('calendar.month_prefix_leap', '闰', '閏') : '';
        if (absMonth === 1) {
            result += tr('calendar.month.zheng', '正月', '正月');
        } else if (absMonth === 12) {
            result += tr('calendar.month.la', '腊月', '臘月');
        } else if (absMonth === 11) {
            result += tr('calendar.month.dong', '冬月', '冬月');
        } else if (absMonth === 10) {
            result += tr('calendar.month.ten', '十月', '十月');
        } else {
            result += numberToChinese(absMonth) + tr('calendar.unit.month', '月', '月');
        }
        return result;
    }

    /**
     * 将农历日转成汉字表示（初一、十五、廿九等）。
     * @param {number} day - 日期数字（1-30）
     * @return {string} 汉字表示
     */
    function localizedLunarDay(day) {
        if (day <= 10) {
            return tr('calendar.day_prefix_chu', '初', '初') + localizedDigit(day);
        }
        if (day < 20) {
            return tr('calendar.digit.ten', '十', '十') + localizedDigit(day - 10);
        }
        if (day === 20) {
            return tr('calendar.digit.two', '二', '二') + tr('calendar.digit.ten', '十', '十');
        }
        if (day < 30) {
            return tr('calendar.day_prefix_nian', '廿', '廿') + localizedDigit(day - 20);
        }
        return tr('calendar.digit.three', '三', '三') + tr('calendar.digit.ten', '十', '十')
            + (day === 30 ? '' : localizedDigit(day - 30));
    }

    window.LunarFormat = {
        currentLanguage: currentLanguage,
        localFallback: localFallback,
        tr: tr,
        localizedDigit: localizedDigit,
        numberToChinese: numberToChinese,
        localizedLunarMonth: localizedLunarMonth,
        localizedLunarDay: localizedLunarDay
    };
})();
