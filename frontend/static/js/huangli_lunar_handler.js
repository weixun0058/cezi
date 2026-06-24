/**
 * 黄历页面的阴阳历日期处理工具
 * 实现公农历日期联动互转
 */

document.addEventListener('DOMContentLoaded', () => {
    // 获取DOM元素
    const birthDateInput = document.getElementById('datePicker');
    const lunarYearInput = document.getElementById('lunar-year');
    const lunarMonthSelect = document.getElementById('lunar-month');
    const lunarDaySelect = document.getElementById('lunar-day');
    const yearGanzhiDisplay = document.getElementById('year-ganzhi-display');
    const yearPickerIcon = document.getElementById('year-picker-icon');
    const yearDropdown = document.getElementById('year-dropdown');
    
    // 创建遮罩层
    let overlay = document.createElement('div');
    overlay.className = 'year-dropdown-overlay';
    document.body.appendChild(overlay);
    
    // 点击遮罩层关闭年份选择器
    overlay.addEventListener('click', function() {
        yearDropdown.style.display = 'none';
        overlay.style.display = 'none';
    });
    
    // 检查是否所有元素都存在
    if (!birthDateInput || !lunarYearInput || !lunarMonthSelect || !lunarDaySelect) {
        console.error("缺少必要的DOM元素");
        return;
    }
    
    console.log("初始化阴阳历联动功能");
    
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
            const ganzhiDisplay = document.querySelector('.lunar-year-ganzhi');
            if (ganzhiDisplay) {
                ganzhiDisplay.textContent = ganzhi;
                ganzhiDisplay.style.display = 'block';
            }
        }
    }
    
    /**
     * 生成年份选项
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
                selectedDecadeElement.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
        }, 100);
    }
    
    // 初始化阴历日期（从阳历）
    function initLunar() {
        try {
            // 获取阳历日期
            const dateStr = birthDateInput.value;
            if (!dateStr) return;
            
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
            
            // 立即更新干支显示
            if (yearGanzhiDisplay) {
                yearGanzhiDisplay.textContent = '(' + getChineseYearGanzhi(lunar.getYear()) + ')';
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
        // 处理年份变更但月份日期尚未选择的情况
        if (lunarMonthSelect.value && lunarDaySelect.value) {
            // 所有日期选项都已选择，可以更新阳历
            updateSolarDate();
        }
    }
    
    /**
     * 阴历月份变更时更新
     */
    function updateFromLunarMonth() {
        // 更新阴历日期选项
        updateLunarDayOptions();
        // 处理月份变更但日期尚未选择的情况
        if (lunarDaySelect.value) {
            // 日期已选择，可以更新阳历
            updateSolarDate();
        }
    }
    
    /**
     * 阴历日期变更时更新
     */
    function updateFromLunarDay() {
        // 更新阳历日期并查询黄历
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
                option.value = monthNumbers[i];
                option.textContent = monthStrings[i];
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
            // 保存当前选中的值
            const currentSelectedValue = lunarDaySelect.value;
            
            // 清空日期选择器
            lunarDaySelect.innerHTML = '';
            
            // 获取阴历年月
            const year = parseInt(lunarYearInput.value);
            const monthStr = lunarMonthSelect.value;
            
            if (isNaN(year) || !monthStr) return;
            
            const lunarMonth = LunarMonth.fromYm(year, parseInt(monthStr));
            const dayCount = lunarMonth.getDayCount();
            
            // 添加日期选项
            for (let i = 1; i <= dayCount; i++) {
                const option = document.createElement('option');
                option.value = i;
                
                // 获取日期的汉字表示
                let dayText;
                if (i === 1) {
                    dayText = '初一';
                } else if (i === 2) {
                    dayText = '初二';
                } else if (i === 3) {
                    dayText = '初三';
                } else if (i === 10) {
                    dayText = '初十';
                } else if (i === 20) {
                    dayText = '二十';
                } else if (i === 30) {
                    dayText = '三十';
                } else if (i < 10) {
                    dayText = '初' + chineseDigits[i];
                } else if (i < 20) {
                    dayText = '十' + chineseDigits[i - 10];
                } else if (i < 30) {
                    dayText = '廿' + chineseDigits[i - 20];
                } else {
                    dayText = '三十' + chineseDigits[i - 30];
                }
                
                option.textContent = dayText;
                lunarDaySelect.appendChild(option);
            }
            
            // 如果之前有选中的值，且在新的选项范围内，则恢复选中状态
            if (currentSelectedValue && parseInt(currentSelectedValue) <= dayCount) {
                lunarDaySelect.value = currentSelectedValue;
            } else if (dayCount > 0) {
                // 否则选择第一个选项
                lunarDaySelect.value = 1;
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
            
            // 只有当日期变化时才触发查询，避免不必要的请求
            if (birthDateInput.value !== dateStr) {
                birthDateInput.value = dateStr;
                
                // 触发公历日期的change事件，使用黄历页面现有逻辑查询数据
                const event = new Event('change', { bubbles: true });
                birthDateInput.dispatchEvent(event);
            }
            
            return dateStr;
        } catch (error) {
            console.error("更新阳历日期失败:", error);
            return null;
        }
    }
    
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
    
    // 初始化
    if (birthDateInput.value) {
        initLunar();
    } else {
        // 如果没有公历日期，设置为东八区的今天
        const now = new Date();
        // 获取当前的UTC时间，并调整为东八区(UTC+8)的时间
        const utcDate = now.getTime() + (now.getTimezoneOffset() * 60000);
        const today = new Date(utcDate + (3600000 * 8)); // UTC+8 对应东八区
        
        // 创建日期字符串，格式：YYYY-MM-DD
        const todayStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
        birthDateInput.value = todayStr;
        initLunar();
    }
}); 