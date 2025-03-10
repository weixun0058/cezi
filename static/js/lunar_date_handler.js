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
    
    // 创建遮罩层
    let overlay = document.createElement('div');
    overlay.className = 'year-dropdown-overlay';
    document.body.appendChild(overlay);
    
    // 点击遮罩层关闭年份选择器
    overlay.addEventListener('click', function() {
        yearDropdown.style.display = 'none';
        overlay.style.display = 'none';
    });
    
    // 初始化阳历日期为东八区的今天
    const now = new Date();
    // 获取当前的UTC时间，并调整为东八区(UTC+8)的时间
    const utcDate = now.getTime() + (now.getTimezoneOffset() * 60000);
    const today = new Date(utcDate + (3600000 * 8)); // UTC+8 对应东八区
    
    // 创建日期字符串，格式：YYYY-MM-DD
    const todayStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
    birthDateInput.value = todayStr; // 使用字符串值而不是valueAsDate，避免浏览器的时区转换
    
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
     * 获取中国干支纪年
     */
    function getChineseYearGanzhi(year) {
        year = parseInt(year);
        if (isNaN(year)) return '';
        
        // 创建农历对象获取干支纪年
        const lunar = Lunar.fromYmd(year, 1, 1);
        return lunar.getYearInGanZhi();
    }
    
    /**
     * 更新干支显示
     */
    function updateGanzhiDisplay(year) {
        year = parseInt(year);
        if (!isNaN(year)) {
            // 获取干支
            const ganzhi = getChineseYearGanzhi(year);
            // 更新显示
            if (yearGanzhiDisplay) {
                yearGanzhiDisplay.textContent = ganzhi;
                yearGanzhiDisplay.style.display = 'block';
            }
        }
    }
    
    /**
     * 生成年份选择器
     */
    function generateYearDropdown() {
        const yearDropdown = document.getElementById('year-dropdown');
        yearDropdown.innerHTML = '';
        
        // 添加关闭按钮
        const closeButton = document.createElement('div');
        closeButton.className = 'year-dropdown-close';
        closeButton.innerHTML = '×';
        closeButton.addEventListener('click', function() {
            yearDropdown.style.display = 'none';
            document.querySelector('.year-dropdown-overlay').style.display = 'none';
        });
        yearDropdown.appendChild(closeButton);
        
        const decades = [
            { title: '1900年代', start: 1900, end: 1909 },
            { title: '1910年代', start: 1910, end: 1919 },
            { title: '1920年代', start: 1920, end: 1929 },
            { title: '1930年代', start: 1930, end: 1939 },
            { title: '1940年代', start: 1940, end: 1949 },
            { title: '1950年代', start: 1950, end: 1959 },
            { title: '1960年代', start: 1960, end: 1969 },
            { title: '1970年代', start: 1970, end: 1979 },
            { title: '1980年代', start: 1980, end: 1989 },
            { title: '1990年代', start: 1990, end: 1999 },
            { title: '2000年代', start: 2000, end: 2009 },
            { title: '2010年代', start: 2010, end: 2019 },
            { title: '2020年代', start: 2020, end: 2029 },
            { title: '2030年代', start: 2030, end: 2039 },
            { title: '2040年代', start: 2040, end: 2049 }
        ];
        
        // 获取当前年份
        const currentYear = new Date().getFullYear();
        // 获取当前选中的年份
        const selectedYear = parseInt(document.getElementById('lunar-year').value) || currentYear;
        
        // 创建并添加每个年代区块
        decades.forEach(decade => {
            const sectionDiv = document.createElement('div');
            sectionDiv.className = 'year-section';
            sectionDiv.id = `decade-${decade.start}`;
            
            // 添加年代标题
            const titleDiv = document.createElement('div');
            titleDiv.className = 'year-section-title';
            titleDiv.textContent = decade.title;
            sectionDiv.appendChild(titleDiv);
            
            // 添加年份按钮容器
            const yearRowDiv = document.createElement('div');
            yearRowDiv.className = 'year-row';
            
            // 添加年份按钮
            for (let year = decade.start; year <= decade.end; year++) {
                const yearButton = document.createElement('button');
                yearButton.className = 'year-option';
                yearButton.textContent = year;
                yearButton.dataset.year = year;
                
                // 如果是当前年份，添加高亮样式
                if (year === currentYear) {
                    yearButton.classList.add('current-year');
                }
                
                // 如果是选中的年份，添加选中样式
                if (year === selectedYear) {
                    yearButton.classList.add('selected');
                }
                
                yearButton.addEventListener('click', function() {
                    // 更新年份输入框的值
                    document.getElementById('lunar-year').value = year;
                    
                    // 隐藏年份选择器和遮罩层
                    yearDropdown.style.display = 'none';
                    document.querySelector('.year-dropdown-overlay').style.display = 'none';
                    
                    // 触发input事件，使其执行与手动输入相同的操作
                    const inputEvent = new Event('input', { bubbles: true });
                    document.getElementById('lunar-year').dispatchEvent(inputEvent);
                });
                
                yearRowDiv.appendChild(yearButton);
            }
            
            sectionDiv.appendChild(yearRowDiv);
            yearDropdown.appendChild(sectionDiv);
        });
        
        // 滚动到包含当前选中年份的区块
        setTimeout(() => {
            const selectedDecadeStart = Math.floor(selectedYear / 10) * 10;
            const selectedDecadeElement = document.getElementById(`decade-${selectedDecadeStart}`);
            if (selectedDecadeElement) {
                selectedDecadeElement.scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'center'  // 确保元素在视口中居中显示
                });
                
                // 找到当前选中的年份按钮并添加视觉提示
                const yearButtons = document.querySelectorAll('.year-option');
                yearButtons.forEach(btn => {
                    if (parseInt(btn.dataset.year) === selectedYear) {
                        btn.classList.add('selected');
                        // 为按钮添加一个闪烁动画，提高可见性
                        btn.style.animation = 'highlight 1s ease-in-out';
                    }
                });
            }
        }, 150); // 增加延迟时间，确保DOM渲染完成
    }
    
    // 初始化阴历日期（从阳历）
    initLunar();
    
    // 确保时辰选项被正确初始化，即使initLunar因为某些原因失败
    updateBirthTimeOptions();
    
    // 阳历日期变更事件
    birthDateInput.addEventListener('change', function() {
        initLunar();
        // 直接调用updateBirthTimeOptions确保时辰选项更新
        updateBirthTimeOptions();
    });
    
    // 阴历年份变更事件
    lunarYearInput.addEventListener('input', function() {
        updateFromLunarYear();
        // 更新时辰选项
        updateBirthTimeOptions();
    });
    
    // 阴历月份变更事件
    lunarMonthSelect.addEventListener('change', function() {
        updateFromLunarMonth();
        // 更新时辰选项
        updateBirthTimeOptions();
    });
    
    // 阴历日期变更事件
    lunarDaySelect.addEventListener('change', function() {
        updateFromLunarDay();
        // 更新时辰选项
        updateBirthTimeOptions();
    });
    
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
                overlay.style.display = 'none';
            } else {
                generateYearDropdown();
                yearDropdown.style.display = 'block';
                overlay.style.display = 'block';
                
                // 延迟执行滚动，确保DOM完全渲染
                setTimeout(() => {
                    // 获取当前选中的年份
                    const selectedYear = parseInt(lunarYearInput.value) || new Date().getFullYear();
                    const selectedDecadeStart = Math.floor(selectedYear / 10) * 10;
                    const selectedDecadeElement = document.getElementById(`decade-${selectedDecadeStart}`);
                    
                    if (selectedDecadeElement) {
                        // 使用scrollIntoView滚动到对应区块
                        selectedDecadeElement.scrollIntoView({ 
                            behavior: 'smooth', 
                            block: 'center'  // 确保元素在视口中居中显示
                        });
                    }
                }, 150); // 增加延迟时间，确保DOM渲染完成
            }
        });
    }
    
    // 点击页面其他地方关闭下拉列表
    document.addEventListener('click', function() {
        if (yearDropdown) {
            yearDropdown.style.display = 'none';
            overlay.style.display = 'none';
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
            // 获取阳历日期字符串
            const dateStr = birthDateInput.value;
            if (!dateStr) return;
            
            // 将日期字符串转换为日期对象
            const date = new Date(dateStr);
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
            
            // 设置阴历日期值
            lunarDaySelect.value = lunar.getDay();
            
            // 更新时辰选项
            updateBirthTimeOptions();
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
            const ganZhi = getChineseYearGanzhi(year);
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
            
            // 时辰的地支（固定的）
            const zhi = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥'];
            // 时间范围
            const timeRanges = [
                '23:00-01:00', '01:00-03:00', '03:00-05:00', '05:00-07:00', 
                '07:00-09:00', '09:00-11:00', '11:00-13:00', '13:00-15:00', 
                '15:00-17:00', '17:00-19:00', '19:00-21:00', '21:00-23:00'
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
                    console.log("当日天干:", dayGan);
                    
                    // 根据口诀确定子时的天干
                    let ziGanIndex; // 子时的天干索引
                    const gan = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸'];
                    
                    // 甲己还加甲
                    if (dayGan === '甲' || dayGan === '己') {
                        ziGanIndex = gan.indexOf('甲');
                    }
                    // 乙庚丙作初
                    else if (dayGan === '乙' || dayGan === '庚') {
                        ziGanIndex = gan.indexOf('丙');
                    }
                    // 丙辛从戊起
                    else if (dayGan === '丙' || dayGan === '辛') {
                        ziGanIndex = gan.indexOf('戊');
                    }
                    // 丁壬庚子居
                    else if (dayGan === '丁' || dayGan === '壬') {
                        ziGanIndex = gan.indexOf('庚');
                    }
                    // 戊癸何方发，壬子是真途
                    else if (dayGan === '戊' || dayGan === '癸') {
                        ziGanIndex = gan.indexOf('壬');
                    }
                    
                    console.log("子时天干索引:", ziGanIndex);
                    
                    // 生成所有时辰的天干地支
                    for (let i = 0; i < zhi.length; i++) {
                        // 计算当前时辰的天干
                        const currentGanIndex = (ziGanIndex + i) % 10;
                        const currentGan = gan[currentGanIndex];
                        const currentZhi = zhi[i];
                        
                        // 创建选项
                        const option = document.createElement('option');
                        option.value = currentZhi; // 仍然只存储地支作为值
                        option.textContent = `${currentGan}${currentZhi}时 (${timeRanges[i]})`;
                        
                        // 添加自定义属性以存储完整干支
                        option.dataset.ganzhi = `${currentGan}${currentZhi}`;
                        
                        birthTimeSelect.appendChild(option);
                    }
                    
                    console.log("成功生成时辰选项");
                } catch (error) {
                    console.error("确定时辰干支时出错:", error);
                    
                    // 如果出错，使用默认的时辰选项（不准确，但至少不会阻止用户选择）
                    fallbackTimeOptions();
                }
            } else {
                // 如果没有完整的年月日信息，使用默认的时辰选项
                fallbackTimeOptions();
            }
        } catch (error) {
            console.error("更新时辰选项时出错:", error);
            // 使用默认选项
            fallbackTimeOptions();
        }
        
        // 回退方案：使用固定干支的时辰选项
        function fallbackTimeOptions() {
            const defaultOptions = [
                { value: '子', text: '子时 (23:00-01:00)' },
                { value: '丑', text: '丑时 (01:00-03:00)' },
                { value: '寅', text: '寅时 (03:00-05:00)' },
                { value: '卯', text: '卯时 (05:00-07:00)' },
                { value: '辰', text: '辰时 (07:00-09:00)' },
                { value: '巳', text: '巳时 (09:00-11:00)' },
                { value: '午', text: '午时 (11:00-13:00)' },
                { value: '未', text: '未时 (13:00-15:00)' },
                { value: '申', text: '申时 (15:00-17:00)' },
                { value: '酉', text: '酉时 (17:00-19:00)' },
                { value: '戌', text: '戌时 (19:00-21:00)' },
                { value: '亥', text: '亥时 (21:00-23:00)' }
            ];
            
            defaultOptions.forEach(option => {
                const el = document.createElement('option');
                el.value = option.value;
                el.textContent = option.text;
                birthTimeSelect.appendChild(el);
            });
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