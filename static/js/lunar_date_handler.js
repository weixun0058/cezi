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
    const birthTimeSelect = document.getElementById('birth-time');
    const yearGanzhiDisplay = document.getElementById('year-ganzhi-display');
    const yearPickerIcon = document.getElementById('year-picker-icon');
    const yearDropdown = document.getElementById('year-dropdown');
    const solarDateContainer = document.getElementById('solar-date-container');
    const lunarDateContainer = document.getElementById('lunar-date-container');
    const dateTabs = document.querySelectorAll('.date-tab');
    
    console.log("初始化阴阳历联动");
    
    // 初始化阳历日期为今天
    const today = new Date();
    birthDateInput.valueAsDate = today;
    
    // 处理日期标签页切换
    if (dateTabs.length > 0) {
        dateTabs.forEach(tab => {
            tab.addEventListener('click', function() {
                // 移除所有标签的active类
                dateTabs.forEach(t => t.classList.remove('active'));
                
                // 为当前点击的标签添加active类
                this.classList.add('active');
                
                // 获取目标容器ID
                const targetId = this.getAttribute('data-target');
                
                // 隐藏所有日期输入容器
                if (solarDateContainer) solarDateContainer.style.display = 'none';
                if (lunarDateContainer) lunarDateContainer.style.display = 'none';
                
                // 显示目标容器
                const targetContainer = document.getElementById(targetId);
                if (targetContainer) {
                    targetContainer.style.display = 'flex';
                }
            });
        });
    }
    
    // 汉字数字转换函数
    const chineseDigits = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十'];
    
    /**
     * 将阿拉伯数字转换为传统汉字表示
     * @param {number} num - 阿拉伯数字
     * @return {string} 汉字表示
     */
    function numberToChinese(num) {
        if (num <= 10) {
            return chineseDigits[num];
        } else if (num < 20) {
            return '十' + (num > 10 ? chineseDigits[num - 10] : '');
        } else if (num < 100) {
            return chineseDigits[Math.floor(num / 10)] + '十' + (num % 10 > 0 ? chineseDigits[num % 10] : '');
        }
        return num.toString();
    }
    
    /**
     * 将日期数字转换为传统汉字表示（初一、十五、廿九等）
     * @param {number} day - 日期数字
     * @return {string} 汉字表示
     */
    function dayToChinese(day) {
        if (day === 1) {
            return '初一';
        } else if (day === 2) {
            return '初二';
        } else if (day === 3) {
            return '初三';
        } else if (day === 4) {
            return '初四';
        } else if (day === 5) {
            return '初五';
        } else if (day === 6) {
            return '初六';
        } else if (day === 7) {
            return '初七';
        } else if (day === 8) {
            return '初八';
        } else if (day === 9) {
            return '初九';
        } else if (day === 10) {
            return '初十';
        } else if (day === 11) {
            return '十一';
        } else if (day === 12) {
            return '十二';
        } else if (day === 13) {
            return '十三';
        } else if (day === 14) {
            return '十四';
        } else if (day === 15) {
            return '十五';
        } else if (day === 16) {
            return '十六';
        } else if (day === 17) {
            return '十七';
        } else if (day === 18) {
            return '十八';
        } else if (day === 19) {
            return '十九';
        } else if (day === 20) {
            return '二十';
        } else if (day < 30) {
            return '廿' + chineseDigits[day - 20];
        } else {
            return '三十' + (day === 30 ? '' : chineseDigits[day - 30]);
        }
    }
    
    /**
     * 将月份转换为传统汉字表示（正月、二月、闰二月等）
     * @param {number} month - 月份（负数表示闰月）
     * @return {string} 汉字表示
     */
    function monthToChinese(month) {
        const isLeap = month < 0;
        const absMonth = Math.abs(month);
        
        let result = '';
        if (isLeap) {
            result += '闰';
        }
        
        if (absMonth === 1) {
            result += '正月';
        } else if (absMonth === 12) {
            result += '腊月';
        } else if (absMonth === 11) {
            result += '冬月';
        } else if (absMonth === 10) {
            result += '十月';
        } else {
            result += numberToChinese(absMonth) + '月';
        }
        
        return result;
    }
    
    /**
     * 获取干支纪年
     * @param {number} year - 年份
     * @return {string} 干支表示
     */
    function getGanZhiYear(year) {
        // 创建一个农历对象来获取干支纪年
        const lunar = Lunar.fromYmd(year, 1, 1);
        return lunar.getYearInGanZhi();
    }
    
    /**
     * 生成年份选项
     */
    function generateYearOptions() {
        yearDropdown.innerHTML = '';
        
        // 创建行容器
        let rowDiv = document.createElement('div');
        rowDiv.className = 'year-dropdown-row';
        
        // 计算当前选中的年份或默认值
        const currentYear = parseInt(lunarYearInput.value) || new Date().getFullYear();
        
        // 生成从1900到2050的年份选项
        for (let year = 1900; year <= 2050; year++) {
            const yearOption = document.createElement('div');
            yearOption.className = 'year-option';
            yearOption.textContent = year;
            yearOption.dataset.year = year;
            
            // 点击年份选项时更新输入框
            yearOption.addEventListener('click', function() {
                lunarYearInput.value = this.dataset.year;
                
                // 手动触发input事件，使其更新干支和其他依赖项
                const event = new Event('input', { bubbles: true });
                lunarYearInput.dispatchEvent(event);
                
                yearDropdown.style.display = 'none';
            });
            
            rowDiv.appendChild(yearOption);
            
            // 每行显示3个，创建新行
            if ((year - 1900 + 1) % 3 === 0) {
                yearDropdown.appendChild(rowDiv);
                rowDiv = document.createElement('div');
                rowDiv.className = 'year-dropdown-row';
            }
        }
        
        // 添加最后一行（如果有剩余）
        if (rowDiv.children.length > 0) {
            yearDropdown.appendChild(rowDiv);
        }
        
        // 滚动到当前年份附近
        setTimeout(() => {
            const yearIndex = currentYear - 1900;
            const scrollPosition = Math.max(0, (yearIndex / 3) * 30 - 100);
            yearDropdown.scrollTop = scrollPosition;
        }, 10);
    }
    
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
    
    // 监听年份输入框的变化和data-ganzhi属性的变化
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'attributes' && mutation.attributeName === 'data-ganzhi') {
                if (yearGanzhiDisplay) {
                    yearGanzhiDisplay.textContent = '(' + lunarYearInput.getAttribute('data-ganzhi') + ')';
                }
            }
        });
    });
    
    if (lunarYearInput) {
        observer.observe(lunarYearInput, { attributes: true });
    }
    
    // 点击图标显示年份下拉列表
    if (yearPickerIcon) {
        yearPickerIcon.addEventListener('click', function(e) {
            e.stopPropagation(); // 阻止事件冒泡
            
            if (yearDropdown.style.display === 'block') {
                yearDropdown.style.display = 'none';
            } else {
                generateYearOptions();
                yearDropdown.style.display = 'block';
            }
        });
    }
    
    // 点击页面其他地方关闭下拉列表
    document.addEventListener('click', function() {
        if (yearDropdown) {
            yearDropdown.style.display = 'none';
        }
    });
    
    // 阻止点击下拉列表本身导致关闭
    if (yearDropdown) {
        yearDropdown.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    }
    
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
            
            // 更新年份显示
            updateYearDisplay();
            
            // 设置阴历月份选项
            updateLunarMonthOptions();
            
            // 设置阴历月份值
            lunarMonthSelect.value = lunar.getMonth();
            
            // 设置阴历日期选项（现在月份已经设置好了）
            updateLunarDayOptions();
            
            // 设置出生时辰选项
            updateBirthTimeOptions();
            
            // 设置阴历日期值
            lunarDaySelect.value = lunar.getDay();
            
            // 立即更新干支显示
            if (yearGanzhiDisplay) {
                yearGanzhiDisplay.textContent = '(' + getGanZhiYear(lunar.getYear()) + ')';
            }
        } catch (error) {
            console.error("初始化阴历失败:", error);
        }
    }
    
    /**
     * 更新年份显示（添加干支）
     */
    function updateYearDisplay() {
        const year = parseInt(lunarYearInput.value);
        if (!isNaN(year)) {
            const ganZhi = getGanZhiYear(year);
            lunarYearInput.setAttribute('data-ganzhi', ganZhi);
            
            // 直接更新显示
            if (yearGanzhiDisplay) {
                yearGanzhiDisplay.textContent = '(' + ganZhi + ')';
            }
        }
    }
    
    /**
     * 阴历年份变更时更新
     */
    function updateFromLunarYear() {
        // 更新年份显示
        updateYearDisplay();
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
            
            const lunarYear = LunarYear.fromYear(year);
            const months = lunarYear.getMonths();
            
            // 获取两种表示方式
            const monthNumbers = months.map(month => month.getMonth()); // 阿拉伯数字，用于值
            const monthStrings = months.map(month => month.toString()); // 完整汉字表示，用于显示
            
            // 填充新选项
            for (let i = 0; i < monthNumbers.length; i++) {
                const option = document.createElement("option");
                option.value = monthNumbers[i];// 选项的值保持原有的月份值（可能为负数表示闰月）
                option.textContent = monthStrings[i]; // 使用完整汉字表示
                lunarMonthSelect.appendChild(option);
            }            
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
            console.log("阴历月:", lunarMonth);
            console.log("阴历月天数:", dayCount);
            
            // 添加日期选项
            for (let i = 1; i <= dayCount; i++) {
                const option = document.createElement('option');
                option.value = i;
                option.textContent = dayToChinese(i); // 使用汉字表示日期
                lunarDaySelect.appendChild(option);
            }
        } catch (error) {
            console.error("更新阴历日期选项失败:", error);
        }
    }
    
    /**
     * 更新出生时辰选项
     */
    function updateBirthTimeOptions() {
        try {
            // 检查是否存在时辰选择器
            if (!birthTimeSelect) return;
            
            // 清空时辰选择器
            birthTimeSelect.innerHTML = '';
            
            // 添加"请选择时辰"选项
            const defaultOption = document.createElement('option');
            defaultOption.value = '';
            defaultOption.textContent = '请选择时辰';
            birthTimeSelect.appendChild(defaultOption);
            
            // 添加时辰选项，包含干支和时间范围
            const timeOptions = [
                { value: '子', text: '甲子时 (23:00-01:00)' },
                { value: '丑', text: '乙丑时 (01:00-03:00)' },
                { value: '寅', text: '丙寅时 (03:00-05:00)' },
                { value: '卯', text: '丁卯时 (05:00-07:00)' },
                { value: '辰', text: '戊辰时 (07:00-09:00)' },
                { value: '巳', text: '己巳时 (09:00-11:00)' },
                { value: '午', text: '庚午时 (11:00-13:00)' },
                { value: '未', text: '辛未时 (13:00-15:00)' },
                { value: '申', text: '壬申时 (15:00-17:00)' },
                { value: '酉', text: '癸酉时 (17:00-19:00)' },
                { value: '戌', text: '甲戌时 (19:00-21:00)' },
                { value: '亥', text: '乙亥时 (21:00-23:00)' }
            ];
            
            // 获取阴历年月日信息，用于确定天干
            const year = parseInt(lunarYearInput.value);
            const monthStr = lunarMonthSelect.value;
            const day = parseInt(lunarDaySelect.value);
            
            if (!isNaN(year) && monthStr && !isNaN(day)) {
                try {
                    // 创建阴历对象
                    const month = parseInt(monthStr);
                    const lunar = Lunar.fromYmd(year, month, day);
                    
                    // 获取当日干支
                    const dayGan = lunar.getDayGan();
                    
                    // 根据日干确定时辰干支
                    const gan = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸'];
                    const zhi = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥'];
                    const dayGanIndex = gan.indexOf(dayGan);
                    
                    if (dayGanIndex !== -1) {
                        // 循环添加时辰选项
                        zhi.forEach((z, index) => {
                            const ganIndex = (dayGanIndex * 2 + index) % 10; // 根据日干推算时辰干
                            const timeGan = gan[ganIndex];
                            
                            const option = document.createElement('option');
                            option.value = z;
                            
                            // 时间范围
                            let timeRange = '';
                            switch (z) {
                                case '子': timeRange = '23:00-01:00'; break;
                                case '丑': timeRange = '01:00-03:00'; break;
                                case '寅': timeRange = '03:00-05:00'; break;
                                case '卯': timeRange = '05:00-07:00'; break;
                                case '辰': timeRange = '07:00-09:00'; break;
                                case '巳': timeRange = '09:00-11:00'; break;
                                case '午': timeRange = '11:00-13:00'; break;
                                case '未': timeRange = '13:00-15:00'; break;
                                case '申': timeRange = '15:00-17:00'; break;
                                case '酉': timeRange = '17:00-19:00'; break;
                                case '戌': timeRange = '19:00-21:00'; break;
                                case '亥': timeRange = '21:00-23:00'; break;
                            }
                            
                            option.textContent = `${timeGan}${z}时 (${timeRange})`;
                            birthTimeSelect.appendChild(option);
                        });
                        
                        return; // 成功生成时辰选项后返回
                    }
                } catch (error) {
                    console.error("根据日干生成时辰干支失败:", error);
                }
            }
            
            // 如果无法根据日干确定时辰干支，使用默认的时辰选项
            timeOptions.forEach(option => {
                const elem = document.createElement('option');
                elem.value = option.value;
                elem.textContent = option.text;
                birthTimeSelect.appendChild(elem);
            });
        } catch (error) {
            console.error("更新时辰选项失败:", error);
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