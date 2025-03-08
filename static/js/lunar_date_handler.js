/**
 * 阴阳历日期处理工具
 * 严格按照lunar.js文档实现阴阳历日期的联动转换
 */

document.addEventListener('DOMContentLoaded', () => {
    // 获取DOM元素
    const birthDateInput = document.getElementById('birth-date');
    const lunarYearInput = document.getElementById('lunar-year');
    const lunarMonthSelect = document.getElementById('lunar-month');
    const lunarDaySelect = document.getElementById('lunar-day');
    
    console.log("初始化阴阳历联动");
    
    // 初始化阳历日期为今天
    const today = new Date();
    birthDateInput.valueAsDate = today;
    
    // 初始化阴历日期（从阳历）
    initLunar();
    
    // 阳历日期变更事件
    birthDateInput.addEventListener('change', initLunar);
    
    // 阴历年份变更事件
    lunarYearInput.addEventListener('input', updateFromLunarYear);
    
    // 阴历月份变更事件
    lunarMonthSelect.addEventListener('change', updateFromLunarMonth);
    
    // 阴历日期变更事件
    lunarDaySelect.addEventListener('change', updateFromLunarDay);
    
    /**
     * 初始化阴历日期（从阳历）
     */
    function initLunar() {
        try {
            // 获取阳历日期
            const date = birthDateInput.valueAsDate;
            console.log("阳历日期:", date);
            
            // 使用Lunar.fromDate获取阴历对象
            const lunar = Lunar.fromDate(date);
            console.log("阴历年月日:", lunar.getYear(), lunar.getMonth(), lunar.getDay());
            
            // 设置阴历年份
            lunarYearInput.value = lunar.getYear();
            lunarYear = LunarYear.fromYear(2012);
            month_list = lunarYear.getMonths().map(month => month.toString());
            console.log("阴历月份:", month_list);


            
            
            // 设置阴历月份选项
            updateLunarMonthOptions();
            // 设置阴历日期选项
            updateLunarDayOptions();
            // 设置阴历月份值
            lunarMonthSelect.value = lunar.getMonth();
            // 设置阴历日期值
            lunarDaySelect.value = lunar.getDay();
        } catch (error) {
            console.error("初始化阴历失败:", error);
        }
    }
    
    /**
     * 阴历年份变更时更新
     */
    function updateFromLunarYear() {
        // 更新阴历月份选项
        updateLunarMonthOptions();
        // 更新阴历日期选项
        updateLunarDayOptions();
        // 更新阳历日期
        updateSolarDate();
    }
    
    /**
     * 阴历月份变更时更新
     */
    function updateFromLunarMonth() {
        // 更新阴历日期选项
        updateLunarDayOptions();
        // 更新阳历日期
        updateSolarDate();
    }
    
    /**
     * 阴历日期变更时更新
     */
    function updateFromLunarDay() {
        // 更新阳历日期
        updateSolarDate();
    }
    
    /**
     * 更新阴历月份选项
     */
    function updateLunarMonthOptions() {
        try {
            // 清空月份选择器
            lunarMonthSelect.innerHTML = '';
            
            // 获取阴历年份
            const year = parseInt(lunarYearInput.value);
            if (isNaN(year)) return;
            
            const lunarYear = LunarYear.fromYear(year)
            const monthList = lunarYear.getMonths().map(month => month.getMonth());


            
        // 填充新选项
        monthList.forEach(month => {
                const option = document.createElement("option");
                option.value = month; // 选项的值（可自定义，比如提取年月）
                option.textContent = month; // 选项显示的文本
                lunarMonthSelect.appendChild(option);
            });
        } catch (error) {
            console.error("更新阴历月份选项失败:", error);
        }
    }
    
    /**
     * 更新阴历日期选项
     */
    function updateLunarDayOptions() {
        try {
            // 清空日期选择器
            lunarDaySelect.innerHTML = '';
            
            // 获取阴历年月
            const year = parseInt(lunarYearInput.value);
            const monthStr = lunarMonthSelect.value;
            
            if (isNaN(year) || !monthStr) return;
            
            const lunarMonth = LunarMonth.fromYm(year, monthStr);
            const dayCount = lunarMonth.getDayCount();
            
            // 添加日期选项
            for (let i = 1; i <= dayCount; i++) {
                const option = document.createElement('option');
                option.value = i;
                option.textContent = i + '日';
                lunarDaySelect.appendChild(option);
            }
        } catch (error) {
            console.error("更新阴历日期选项失败:", error);
        }
    }
    
    /**
     * 从阴历更新阳历日期
     */
    function updateSolarDate() {
        try {
            // 获取阴历年月日
            const year = parseInt(lunarYearInput.value);
            const monthStr = lunarMonthSelect.value;
            const day = parseInt(lunarDaySelect.value);
            
            if (isNaN(year) || !monthStr || isNaN(day)) return;
            
            // 解析月份（处理闰月）
            const month = parseInt(monthStr);
            
            // 创建阴历对象
            let lunar;
            if (month < 0) {
                // 闰月（负数表示）
                lunar = Lunar.fromYmd(year, month, day);
            } else {
                lunar = Lunar.fromYmd(year, month, day);
            }
            
            // 转换为阳历
            const solar = lunar.getSolar();
            
            // 更新阳历日期输入框
            const dateStr = `${solar.getYear()}-${String(solar.getMonth()).padStart(2, '0')}-${String(solar.getDay()).padStart(2, '0')}`;
            birthDateInput.value = dateStr;
        } catch (error) {
            console.error("更新阳历日期失败:", error);
        }
    }
}); 