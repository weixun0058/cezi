/**
 * 诸葛神算V2 - 公农历日期转换器
 * 日历交互逻辑
 */

// DOM 元素
const gregorianDateInput = document.getElementById('gregorian-date');
const lunarYearInput = document.getElementById('lunar-year');
const lunarMonthSelect = document.getElementById('lunar-month');
const lunarDaySelect = document.getElementById('lunar-day');
const todayGregorianSpan = document.getElementById('today-gregorian');
const todayLunarSpan = document.getElementById('today-lunar');

// 农历月份和日期的中文表示
const lunarMonthStr = ["正", "二", "三", "四", "五", "六", "七", "八", "九", "十", "冬", "腊"];
const lunarDayStr = [
    "初一", "初二", "初三", "初四", "初五", "初六", "初七", "初八", "初九", "初十",
    "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九", "二十",
    "廿一", "廿二", "廿三", "廿四", "廿五", "廿六", "廿七", "廿八", "廿九", "三十"
];

// 标记是否正在更新，防止循环触发
let isUpdating = false;

/**
 * 获取农历月份的中文表示
 */
function getLunarMonthText(month, isLeap) {
    return (isLeap ? "闰" : "") + lunarMonthStr[month - 1] + "月";
}

/**
 * 获取农历日期的中文表示
 */
function getLunarDayText(day) {
    return lunarDayStr[day - 1];
}

/**
 * 初始化日期选择器
 */
function initDatePickers() {
    console.log('初始化日期选择器');
    
    // 设置公历日期范围
    gregorianDateInput.min = '1900-01-01';
    gregorianDateInput.max = '2100-12-31';
    
    // 设置农历年份范围
    lunarYearInput.min = 1900;
    lunarYearInput.max = 2100;
    
    // 初始化为当前日期
    const today = new Date();
    
    // 格式化公历日期为YYYY-MM-DD格式
    const year = today.getFullYear();
    const month = (today.getMonth() + 1).toString().padStart(2, '0');
    const day = today.getDate().toString().padStart(2, '0');
    const formattedDate = `${year}-${month}-${day}`;
    
    // 设置公历日期输入框的值
    gregorianDateInput.value = formattedDate;
    
    // 更新农历日期
    updateLunarFromGregorian();
    
    // 显示今天的日期信息
    updateTodayInfo();
}

/**
 * 更新今天的日期信息
 */
function updateTodayInfo() {
    const today = new Date();
    const year = today.getFullYear();
    const month = (today.getMonth() + 1).toString().padStart(2, '0');
    const day = today.getDate().toString().padStart(2, '0');
    
    // 公历日期
    todayGregorianSpan.textContent = `${year}年${month}月${day}日`;
    
    try {
        // 农历日期
        const solar = Solar.fromDate(today);
        const lunar = solar.getLunar();
        todayLunarSpan.textContent = lunar.toString();
    } catch (error) {
        console.error('更新今日信息出错:', error);
        todayLunarSpan.textContent = '获取农历信息失败';
    }
}

/**
 * 根据公历日期更新农历日期
 */
function updateLunarFromGregorian() {
    if (isUpdating) return;
    isUpdating = true;
    
    try {
        const dateValue = gregorianDateInput.value;
        if (!dateValue) {
            isUpdating = false;
            return;
        }
        
        const [year, month, day] = dateValue.split('-').map(Number);
        
        console.log(`公历日期变更为: ${year}-${month}-${day}`);
        
        // 使用lunar-javascript库转换
        const solar = Solar.fromYmd(year, month, day);
        const lunar = solar.getLunar();
        
        console.log(`转换结果: 农历 ${lunar.getYear()}年${lunar.getMonth()}月${lunar.getDay()}日 ${lunar.isLeap() ? '闰' : ''}`);
        
        // 更新农历年份
        lunarYearInput.value = lunar.getYear();
        
        // 更新农历月份选项
        updateLunarMonthOptions(lunar.getYear());
        
        // 选择当前农历月份
        const monthValue = lunar.isLeap() ? `leap-${lunar.getMonth()}` : lunar.getMonth().toString();
        lunarMonthSelect.value = monthValue;
        
        // 更新农历日期选项
        updateLunarDayOptions(lunar.getYear(), lunar.getMonth(), lunar.isLeap());
        
        // 选择当前农历日期
        lunarDaySelect.value = lunar.getDay().toString();
    } catch (error) {
        console.error('更新农历日期出错:', error);
    } finally {
        isUpdating = false;
    }
}

/**
 * 根据农历日期更新公历日期
 */
function updateGregorianFromLunar() {
    if (isUpdating) return;
    isUpdating = true;
    
    try {
        const year = parseInt(lunarYearInput.value, 10);
        if (isNaN(year) || year < 1900 || year > 2100) {
            isUpdating = false;
            return;
        }
        
        const monthValue = lunarMonthSelect.value;
        if (!monthValue) {
            isUpdating = false;
            return;
        }
        
        let month, isLeap;
        if (monthValue.startsWith('leap-')) {
            isLeap = true;
            month = parseInt(monthValue.substring(5), 10);
        } else {
            isLeap = false;
            month = parseInt(monthValue, 10);
        }
        
        const day = parseInt(lunarDaySelect.value, 10);
        if (isNaN(day)) {
            isUpdating = false;
            return;
        }
        
        console.log(`农历日期变更为: ${year}年${month}月${day}日 ${isLeap ? '闰' : ''}`);
        
        // 使用lunar-javascript库转换
        const lunar = Lunar.fromYmd(year, month, day, isLeap);
        const solar = lunar.getSolar();
        
        console.log(`转换结果: 公历 ${solar.getYear()}-${solar.getMonth()}-${solar.getDay()}`);
        
        // 格式化公历日期
        const solarYear = solar.getYear();
        const solarMonth = solar.getMonth().toString().padStart(2, '0');
        const solarDay = solar.getDay().toString().padStart(2, '0');
        
        // 更新公历日期输入框
        gregorianDateInput.value = `${solarYear}-${solarMonth}-${solarDay}`;
    } catch (error) {
        console.error('更新公历日期出错:', error);
    } finally {
        isUpdating = false;
    }
}

/**
 * 更新农历月份选项
 */
function updateLunarMonthOptions(year) {
    // 清空现有选项
    lunarMonthSelect.innerHTML = '';
    
    try {
        // 获取该年的闰月
        const lunar = Lunar.fromYmd(year, 1, 1);
        const leapMonth = lunar.getLeapMonth();
        console.log(`${year}年的闰月是: ${leapMonth || '无'}`);
        
        // 添加月份选项
        for (let i = 1; i <= 12; i++) {
            const option = document.createElement('option');
            option.value = i.toString();
            option.textContent = getLunarMonthText(i, false);
            lunarMonthSelect.appendChild(option);
            
            // 如果有闰月，添加闰月选项
            if (i === leapMonth) {
                const leapOption = document.createElement('option');
                leapOption.value = `leap-${i}`;
                leapOption.textContent = getLunarMonthText(i, true);
                lunarMonthSelect.appendChild(leapOption);
            }
        }
    } catch (error) {
        console.error('更新农历月份选项出错:', error);
    }
}

/**
 * 更新农历日期选项
 */
function updateLunarDayOptions(year, month, isLeap) {
    // 清空现有选项
    lunarDaySelect.innerHTML = '';
    
    try {
        // 获取该月的天数
        const lunar = Lunar.fromYmd(year, month, 1, isLeap);
        const daysInMonth = lunar.getDaysOfMonth();
        console.log(`${year}年${isLeap ? '闰' : ''}${month}月的天数: ${daysInMonth}`);
        
        // 添加日期选项
        for (let i = 1; i <= daysInMonth; i++) {
            const option = document.createElement('option');
            option.value = i.toString();
            option.textContent = getLunarDayText(i);
            lunarDaySelect.appendChild(option);
        }
    } catch (error) {
        console.error('更新农历日期选项出错:', error);
    }
}

/**
 * 处理农历年份变化
 */
function handleLunarYearChange() {
    try {
        const year = parseInt(lunarYearInput.value, 10);
        if (isNaN(year) || year < 1900 || year > 2100) {
            return;
        }
        
        console.log(`农历年份变更为: ${year}`);
        
        // 更新农历月份选项
        updateLunarMonthOptions(year);
        
        // 选择默认月份（正月）
        lunarMonthSelect.value = '1';
        
        // 更新农历日期选项
        updateLunarDayOptions(year, 1, false);
        
        // 选择默认日期（初一）
        lunarDaySelect.value = '1';
        
        // 更新公历日期
        updateGregorianFromLunar();
    } catch (error) {
        console.error('处理农历年份变化出错:', error);
    }
}

/**
 * 处理农历月份变化
 */
function handleLunarMonthChange() {
    try {
        const year = parseInt(lunarYearInput.value, 10);
        if (isNaN(year) || year < 1900 || year > 2100) {
            return;
        }
        
        const monthValue = lunarMonthSelect.value;
        if (!monthValue) {
            return;
        }
        
        let month, isLeap;
        if (monthValue.startsWith('leap-')) {
            isLeap = true;
            month = parseInt(monthValue.substring(5), 10);
        } else {
            isLeap = false;
            month = parseInt(monthValue, 10);
        }
        
        console.log(`农历月份变更为: ${isLeap ? '闰' : ''}${month}月`);
        
        // 更新农历日期选项
        updateLunarDayOptions(year, month, isLeap);
        
        // 选择默认日期（初一）
        lunarDaySelect.value = '1';
        
        // 更新公历日期
        updateGregorianFromLunar();
    } catch (error) {
        console.error('处理农历月份变化出错:', error);
    }
}

/**
 * 处理农历日期变化
 */
function handleLunarDayChange() {
    try {
        const day = parseInt(lunarDaySelect.value, 10);
        console.log(`农历日期变更为: ${day}日`);
        
        // 更新公历日期
        updateGregorianFromLunar();
    } catch (error) {
        console.error('处理农历日期变化出错:', error);
    }
}

// 添加事件监听器
gregorianDateInput.addEventListener('change', updateLunarFromGregorian);
lunarYearInput.addEventListener('change', handleLunarYearChange);
lunarYearInput.addEventListener('input', handleLunarYearChange);
lunarMonthSelect.addEventListener('change', handleLunarMonthChange);
lunarDaySelect.addEventListener('change', handleLunarDayChange);

// 检查lunar-javascript库是否加载
function checkLunarLibrary() {
    if (typeof Solar !== 'undefined' && typeof Lunar !== 'undefined') {
        console.log('lunar-javascript库已加载，开始初始化日期选择器');
        initDatePickers();
        return true;
    }
    return false;
}

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('页面加载完成，尝试初始化');
    
    // 尝试立即初始化
    if (checkLunarLibrary()) {
        return;
    }
    
    // 如果库未加载，等待一段时间后再次尝试
    console.log('lunar-javascript库尚未加载，等待500ms后重试');
    setTimeout(function() {
        if (checkLunarLibrary()) {
            return;
        }
        
        // 如果仍未加载，显示错误信息
        console.error('lunar-javascript库加载失败，请检查路径是否正确');
        alert('日历转换库加载失败，请检查lunar.js文件路径是否正确');
    }, 500);
}); 