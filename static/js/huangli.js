let weekHuangliLoaded = false;

document.addEventListener('DOMContentLoaded', function() {
    console.log('页面加载完成，初始化黄历功能');
    
    // 检查DOM元素是否存在
    console.log('检查DOM元素:');
    console.log('datePicker元素:', document.getElementById('datePicker') ? '存在' : '不存在');
    console.log('weekHuangliContainer元素:', document.getElementById('weekHuangliContainer') ? '存在' : '不存在');
    
    // 获取东八区的当前日期
    const now = new Date();
    // 获取当前的UTC时间，并调整为东八区(UTC+8)的时间
    const utcDate = now.getTime() + (now.getTimezoneOffset() * 60000);
    const today = new Date(utcDate + (3600000 * 8)); // UTC+8 对应东八区
    const datePicker = document.getElementById('datePicker');
    
    // 设置日期选择器的默认值为东八区的今天
    // 使用日期字符串而不是valueAsDate，避免浏览器的时区转换
    const todayStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
    datePicker.value = todayStr;
    console.log('设置日期选择器默认值为:', todayStr);
    
    // 获取按钮元素
    const prevDayBtn = document.getElementById('prevDayBtn');
    const nextDayBtn = document.getElementById('nextDayBtn');
    const todayBtn = document.getElementById('todayBtn');
    
    // 添加按钮事件监听器
    prevDayBtn.addEventListener('click', function() {
        const currentDate = new Date(datePicker.value);
        currentDate.setDate(currentDate.getDate() - 1);
        datePicker.valueAsDate = currentDate;
        fetchAndDisplayHuangliData(formatDate(currentDate));
    });
    
    nextDayBtn.addEventListener('click', function() {
        const currentDate = new Date(datePicker.value);
        currentDate.setDate(currentDate.getDate() + 1);
        datePicker.valueAsDate = currentDate;
        fetchAndDisplayHuangliData(formatDate(currentDate));
    });
    
    todayBtn.addEventListener('click', function() {
        // 获取东八区的当前日期
        const now = new Date();
        // 获取当前的UTC时间，并调整为东八区(UTC+8)的时间
        const utcDate = now.getTime() + (now.getTimezoneOffset() * 60000);
        const today = new Date(utcDate + (3600000 * 8)); // UTC+8 对应东八区
        
        // 使用日期字符串格式
        const todayStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
        datePicker.value = todayStr;
        
        // 触发日期变更事件
        const event = new Event('change');
        datePicker.dispatchEvent(event);
    });
    
    // 添加日期选择器的change事件监听器
    datePicker.addEventListener('change', function() {
        const selectedDate = this.value;
        if (selectedDate) {
            fetchAndDisplayHuangliData(selectedDate);
        }
    });
    
    // 添加回车键确认事件
    datePicker.addEventListener('keyup', function(e) {
        if (e.key === 'Enter') {
            const selectedDate = this.value;
            if (selectedDate) {
                fetchAndDisplayHuangliData(selectedDate);
            }
        }
    });

    datePicker.addEventListener('keydown', function(e) {
        // 只处理数字键输入，忽略控制键
        if (/^\d$/.test(e.key) && !e.ctrlKey && !e.altKey && !e.metaKey) {
            const curValue = this.value;
            const selStart = this.selectionStart;
            
            // 检查是否在输入年份部分
            if (!curValue.includes('-') || selStart <= curValue.indexOf('-')) {
                // 如果已经输入了4位年份，且光标在第4位之后
                const yearPart = !curValue.includes('-') ? curValue : curValue.split('-')[0];
                if (yearPart.length === 4 && selStart >= 4) {
                    // 阻止默认行为，添加分隔符并跳转到月份部分
                    e.preventDefault();
                    const newValue = yearPart + '-' + e.key;
                    this.value = newValue;
                    
                    // 设置光标位置到月份部分
                    setTimeout(() => this.setSelectionRange(6, 6), 0);
                    return;
                }
            }
            
            // 检查是否在输入月份部分
            if (curValue.includes('-') && curValue.split('-').length === 2) {
                const monthPart = curValue.split('-')[1];
                const monthStart = curValue.indexOf('-') + 1;
                
                // 如果已经输入了2位月份，且光标在月份末尾
                if (monthPart.length === 2 && selStart === monthStart + 2) {
                    // 阻止默认行为，添加分隔符并跳转到日期部分
                    e.preventDefault();
                    const newValue = curValue + '-' + e.key;
                    this.value = newValue;
                    
                    // 设置光标位置到日期部分
                    setTimeout(() => this.setSelectionRange(newValue.length, newValue.length), 0);
                    return;
                }
            }
            
            // 检查是否在输入日期部分
            if (curValue.includes('-') && curValue.split('-').length === 3) {
                const datePart = curValue.split('-')[2];
                const dateStart = curValue.lastIndexOf('-') + 1;
                
                // 如果已经输入了2位日期，且光标在日期末尾
                if (datePart.length === 2 && selStart === dateStart + 2) {
                    // 阻止默认行为
                    e.preventDefault();
                    
                    // 日期输入完成，触发数据更新
                    setTimeout(() => {
                        fetchAndDisplayHuangliData(this.value);
                    }, 0);
                    return;
                }
            }
        }
    });

    const weekHuangliToggle = document.getElementById('weekHuangliToggle');
    const weekHuangliPanel = document.getElementById('weekHuangliPanel');
    weekHuangliToggle.addEventListener('click', () => {
        const expanded = weekHuangliToggle.getAttribute('aria-expanded') !== 'true';
        weekHuangliToggle.setAttribute('aria-expanded', String(expanded));
        weekHuangliPanel.classList.toggle('hidden', !expanded);
        if (expanded && !weekHuangliLoaded) {
            fetchAndDisplayNineDaysHuangliData();
        }
    });
    document.getElementById('scenarioFilter').addEventListener('change', () => {
        fetchAndDisplayNineDaysHuangliData();
    });
    
    // 初始加载今天的黄历数据
    fetchAndDisplayHuangliData(formatDate(today));
    
    // 更新当前时辰
    updateCurrentTime();
    // 每分钟更新一次时辰
    setInterval(updateCurrentTime, 60000);
});

// 更新当前时辰
function updateCurrentTime() {
    const now = new Date();
    const hours = now.getHours();
    const minutes = now.getMinutes();
    
    const formattedTime = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;
    
    // 计算当前时辰
    const chineseHour = getChineseHour(hours);
    
    // 只在currentTime中显示时辰信息
    const timeElement = document.getElementById('currentTime');
    timeElement.textContent = `当前时间：${formattedTime} · ${chineseHour}`;
}

// 获取中国传统时辰
function getChineseHour(hour) {
    const chineseHours = [
        { name: "子时", start: 23, end: 1, desc: "夜半" },
        { name: "丑时", start: 1, end: 3, desc: "鸡鸣" },
        { name: "寅时", start: 3, end: 5, desc: "平旦" },
        { name: "卯时", start: 5, end: 7, desc: "日出" },
        { name: "辰时", start: 7, end: 9, desc: "食时" },
        { name: "巳时", start: 9, end: 11, desc: "隅中" },
        { name: "午时", start: 11, end: 13, desc: "日中" },
        { name: "未时", start: 13, end: 15, desc: "日昳" },
        { name: "申时", start: 15, end: 17, desc: "哺时" },
        { name: "酉时", start: 17, end: 19, desc: "日入" },
        { name: "戌时", start: 19, end: 21, desc: "黄昏" },
        { name: "亥时", start: 21, end: 23, desc: "人定" }
    ];
    
    for (let i = 0; i < chineseHours.length; i++) {
        const timeSlot = chineseHours[i];
        if (timeSlot.start < timeSlot.end) {
            // 正常时间段
            if (hour >= timeSlot.start && hour < timeSlot.end) {
                return `${timeSlot.name} (${timeSlot.desc}, ${timeSlot.start}:00-${timeSlot.end}:00)`;
            }
        } else {
            // 跨日的时间段（子时）
            if (hour >= timeSlot.start || hour < timeSlot.end) {
                return `${timeSlot.name} (${timeSlot.desc}, ${timeSlot.start}:00-${timeSlot.end}:00)`;
            }
        }
    }
    
    return "未知时辰";
}

// 格式化日期为 YYYY-MM-DD
function formatDate(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

// 获取并显示黄历数据
function fetchAndDisplayHuangliData(date) {
    showHuangliStatus('正在加载黄历…');
    fetch(`/api/huangli?date=${encodeURIComponent(date)}`)
        .then(response => {
            console.log('黄历API响应状态:', response.status);
            if (!response.ok) {
                throw new Error('网络响应不正常');
            }
            return response.json();
        })
        .then(data => {
            console.log('获取到黄历数据:', data);
            if (data && data.success) {
                console.log('黄历数据获取成功，开始显示数据');
                displayHuangliData(data.data);
            } else {
                console.error('获取黄历数据失败:', data ? data.message : '未知错误');
                showHuangliStatus(data?.error?.message || '获取黄历数据失败，请稍后再试。', 'error');
            }
        })
        .catch(error => {
            console.error('获取黄历数据出错:', error);
            showHuangliStatus('获取黄历数据出错，请稍后再试。', 'error');
        });
}

// 获取并显示九天黄历数据
function fetchAndDisplayNineDaysHuangliData() {
    console.log('开始获取九天黄历数据');
    const container = document.getElementById('weekHuangliContainer');
    container.innerHTML = '<div class="loading">加载中...</div>';
    const scenario = document.getElementById('scenarioFilter')?.value || '';
    fetch(`/api/week_huangli?scenario=${encodeURIComponent(scenario)}`)
        .then(response => {
            console.log('九天黄历API响应状态:', response.status);
            if (!response.ok) {
                throw new Error('网络响应不正常');
            }
            return response.json();
        })
        .then(data => {
            console.log('获取到九天黄历数据:', data);
            if (data && data.success && data.data && Array.isArray(data.data)) {
                weekHuangliLoaded = true;
                displayNineDaysHuangliData(data.data);
            } else {
                weekHuangliLoaded = false;
                console.error('获取九天黄历数据失败:', data ? data.message : '未知错误');
                document.getElementById('weekHuangliContainer').innerHTML = '<div class="error">获取九天黄历数据失败，请稍后再试。</div>';
            }
        })
        .catch(error => {
            weekHuangliLoaded = false;
            console.error('获取九天黄历数据出错:', error);
            document.getElementById('weekHuangliContainer').innerHTML = '<div class="error">获取九天黄历数据出错，请稍后再试。</div>';
        });
}

// 显示黄历数据
function displayHuangliData(data) {
    try {
        console.log("显示黄历数据:", data);
        
        showHuangliStatus('');
        // 获取当前时间，用于实时钟表
        const now = new Date();
        const hours = now.getHours();
        const minutes = now.getMinutes();
        const formattedTime = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;
        
        const selectedDate = new Date(`${data.date}T00:00:00`);
        document.getElementById('currentDate').textContent = selectedDate.toLocaleDateString('zh-CN', {
            year: 'numeric', month: 'long', day: 'numeric', weekday: 'long'
        });
        
        // 更新日期信息 - 移除对solarDate的引用
        document.getElementById('lunarDate').textContent = data.lunar_date || '未知';
        document.getElementById('ganZhi').textContent = `${data.gan_zhi_year || '未知'} ${data.gan_zhi_month || '未知'} ${data.gan_zhi_day || '未知'}`;
        
        // 更新时辰信息
        const ganZhiHourElement = document.getElementById('ganZhiHour');
        ganZhiHourElement.textContent = `所选日期子时：${data.gan_zhi_hour || '未知'}`;
        
        document.getElementById('zodiac').textContent = data.zodiac || '未知';
        
        // 更新节气
        document.getElementById('solarTermName').textContent = data.solar_term || '无';
        
        // 详细打印节气相关信息，用于调试
        console.log("节气相关数据:", {
            "当前节气": data.solar_term,
            "上一节气名称": data.prev_solar_term,
            "上一节气天数": data.prev_solar_term_days,
            "下一节气名称": data.next_solar_term, 
            "下一节气天数": data.next_solar_term_days
        });
        
        // 更新上一个节气和下一个节气信息
        const prevSolarTermElement = document.getElementById('prevSolarTerm');
        const nextSolarTermElement = document.getElementById('nextSolarTerm');
        
        // 无论是否有数据，都尝试显示，方便调试
        prevSolarTermElement.innerHTML = `<span>${data.prev_solar_term || '未知'}</span> <small>(${data.prev_solar_term_days || '?'}天前)</small>`;
        prevSolarTermElement.style.display = 'block';
        
        nextSolarTermElement.innerHTML = `<span>${data.next_solar_term || '未知'}</span> <small>(还有${data.next_solar_term_days || '?'}天)</small>`;
        nextSolarTermElement.style.display = 'block';
        
        // 更新节日
        const festivalList = document.getElementById('festivalList');
        if (data.festivals && data.festivals.length > 0) {
            festivalList.innerHTML = '';
            data.festivals.forEach(festival => {
                const festivalItem = document.createElement('div');
                festivalItem.className = 'festival-item';
                festivalItem.textContent = festival.name;
                festivalList.appendChild(festivalItem);
            });
        } else {
            festivalList.textContent = '今日无节日';
        }
        
        // 更新宜忌
        const suitableContainer = document.getElementById('suitable');
        let suitableItems = [];
        
        // 处理宜数据，可能是字符串或数组
        if (data.suitable) {
            if (typeof data.suitable === 'string') {
                // 如果是字符串，按、号分割
                suitableItems = data.suitable.split('、').filter(item => item.trim() !== '');
            } else if (Array.isArray(data.suitable)) {
                // 如果已经是数组
                suitableItems = data.suitable;
            }
        }
        
        if (suitableItems.length > 0) {
            suitableContainer.innerHTML = '';
            suitableItems.forEach(item => {
                const tag = document.createElement('div');
                tag.className = 'tag suitable-tag';
                tag.textContent = item;
                suitableContainer.appendChild(tag);
            });
        } else {
            suitableContainer.textContent = '无';
        }
        
        const unsuitableContainer = document.getElementById('unsuitable');
        let unsuitableItems = [];
        
        // 处理忌数据，可能是字符串或数组
        if (data.unsuitable) {
            if (typeof data.unsuitable === 'string') {
                // 如果是字符串，按、号分割
                unsuitableItems = data.unsuitable.split('、').filter(item => item.trim() !== '');
            } else if (Array.isArray(data.unsuitable)) {
                // 如果已经是数组
                unsuitableItems = data.unsuitable;
            }
        }
        
        if (unsuitableItems.length > 0) {
            unsuitableContainer.innerHTML = '';
            unsuitableItems.forEach(item => {
                const tag = document.createElement('div');
                tag.className = 'tag unsuitable-tag';
                tag.textContent = item;
                unsuitableContainer.appendChild(tag);
            });
        } else {
            unsuitableContainer.textContent = '无';
        }
        
        // 更新彭祖百忌
        document.getElementById('pengZuBaiJi').textContent = data.peng_zu_bai_ji || '无';
        
        // 更新神煞信息
        try {
            document.getElementById('chongSha').textContent = data.chong_sha || '无';
            document.getElementById('xiShen').textContent = data.xi_shen || '无';
            document.getElementById('fuShen').textContent = data.fu_shen || '无';
            document.getElementById('caiShen').textContent = data.cai_shen || '无';
            
            // 处理吉神
            const jiShenElement = document.getElementById('jiShen');
            if (data.ji_shen) {
                if (typeof data.ji_shen === 'string') {
                    jiShenElement.textContent = data.ji_shen;
                } else if (Array.isArray(data.ji_shen)) {
                    jiShenElement.textContent = data.ji_shen.join('、');
                }
            } else {
                jiShenElement.textContent = '无';
            }
            
            // 处理凶神
            const xiongShenElement = document.getElementById('xiongShen');
            if (data.xiong_shen) {
                if (typeof data.xiong_shen === 'string') {
                    xiongShenElement.textContent = data.xiong_shen;
                } else if (Array.isArray(data.xiong_shen)) {
                    xiongShenElement.textContent = data.xiong_shen.join('、');
                }
            } else {
                xiongShenElement.textContent = '无';
            }
        } catch (error) {
            console.error('处理神煞信息出错:', error);
            document.getElementById('chongSha').textContent = '无';
            document.getElementById('jiShen').textContent = '无';
            document.getElementById('xiongShen').textContent = '无';
            document.getElementById('xiShen').textContent = '无';
            document.getElementById('fuShen').textContent = '无';
            document.getElementById('caiShen').textContent = '无';
        }
    } catch (error) {
        console.error('显示黄历数据出错:', error);
        showHuangliStatus('显示黄历数据出错，请稍后再试。', 'error');
    }
}

// 显示九天黄历数据
function displayNineDaysHuangliData(weekData) {
    console.log("显示九天黄历数据:", weekData);
    
    try {
        const weekHuangliContainer = document.getElementById('weekHuangliContainer');
        if (!weekHuangliContainer) {
            console.error("找不到weekHuangliContainer容器");
            return;
        }
        
        console.log("找到weekHuangliContainer容器，开始处理数据");
        
        // 清空容器
        weekHuangliContainer.innerHTML = '';
        
        // 创建网格容器
        const gridContainer = document.createElement('div');
        gridContainer.className = 'week-grid';
        
        // 获取今天的日期，用于高亮显示
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        
        console.log("处理九天黄历数据，共", weekData.length, "天");
        
        // 遍历每天的数据
        weekData.forEach((dayData, index) => {
            console.log(`处理第${index+1}天数据:`, dayData.date);
            
            // 创建日期卡片
            const dayCard = document.createElement('div');
            dayCard.className = 'day-card';
            
            // 检查是否是今天
            const cardDate = new Date(dayData.date);
            cardDate.setHours(0, 0, 0, 0);
            if (cardDate.getTime() === today.getTime()) {
                dayCard.classList.add('today');
            }
            
            // 格式化日期
            const dateObj = new Date(dayData.date);
            const month = dateObj.getMonth() + 1;
            const day = dateObj.getDate();
            const weekday = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'][dateObj.getDay()];
            
            // 创建日期部分
            const dateSection = document.createElement('div');
            dateSection.className = 'date-section';
            dateSection.innerHTML = `
                <div class="solar-date">${month}月${day}日 ${weekday}</div>
                <div class="lunar-date">${dayData.lunar_date}</div>
            `;
            
            // 创建宜忌部分
            const suitableUnsuitableSection = document.createElement('div');
            suitableUnsuitableSection.className = 'suitable-unsuitable';
            
            // 创建宜忌内容的容器
            const suitableUnsuitableContent = document.createElement('div');
            suitableUnsuitableContent.className = 'suitable-unsuitable-content';
            
            // 处理宜的内容
            const suitableDiv = document.createElement('div');
            suitableDiv.className = 'suitable';
            
            const suitableLabel = document.createElement('div');
            suitableLabel.className = 'label';
            suitableLabel.textContent = '宜';
            
            const suitableContent = document.createElement('div');
            suitableContent.className = 'content';
            
            // 确保suitable是数组
            let suitableArray = [];
            if (dayData.suitable) {
                if (typeof dayData.suitable === 'string') {
                    suitableArray = dayData.suitable.split('、').filter(item => item.trim() !== '');
                } else if (Array.isArray(dayData.suitable)) {
                    suitableArray = dayData.suitable;
                }
            }
            
            suitableContent.textContent = suitableArray.length > 0 ? suitableArray.join('、') : '无';
            
            suitableDiv.appendChild(suitableLabel);
            suitableDiv.appendChild(suitableContent);
            
            // 处理忌的内容
            const unsuitableDiv = document.createElement('div');
            unsuitableDiv.className = 'unsuitable';
            
            const unsuitableLabel = document.createElement('div');
            unsuitableLabel.className = 'label';
            unsuitableLabel.textContent = '忌';
            
            const unsuitableContent = document.createElement('div');
            unsuitableContent.className = 'content';
            
            // 确保unsuitable是数组
            let unsuitableArray = [];
            if (dayData.unsuitable) {
                if (typeof dayData.unsuitable === 'string') {
                    unsuitableArray = dayData.unsuitable.split('、').filter(item => item.trim() !== '');
                } else if (Array.isArray(dayData.unsuitable)) {
                    unsuitableArray = dayData.unsuitable;
                }
            }
            
            unsuitableContent.textContent = unsuitableArray.length > 0 ? unsuitableArray.join('、') : '无';
            
            unsuitableDiv.appendChild(unsuitableLabel);
            unsuitableDiv.appendChild(unsuitableContent);
            
            // 将宜忌添加到内容容器
            suitableUnsuitableContent.appendChild(suitableDiv);
            suitableUnsuitableContent.appendChild(unsuitableDiv);
            
            // 将内容容器添加到宜忌部分
            suitableUnsuitableSection.appendChild(suitableUnsuitableContent);
            
            // 添加神煞信息
            const shenShaSection = document.createElement('div');
            shenShaSection.className = 'shen-sha-brief';
            
            // 冲煞信息
            let shenShaInfo = '';
            if (dayData.chong_sha) {
                shenShaInfo += `冲煞: ${dayData.chong_sha}`;
            }
            
            // 喜神、福神、财神信息
            let otherShenInfo = [];
            if (dayData.xi_shen) {
                otherShenInfo.push(`喜神: ${dayData.xi_shen}`);
            }
            if (dayData.fu_shen) {
                otherShenInfo.push(`福神: ${dayData.fu_shen}`);
            }
            if (dayData.cai_shen) {
                otherShenInfo.push(`财神: ${dayData.cai_shen}`);
            }
            
            if (otherShenInfo.length > 0) {
                if (shenShaInfo) shenShaInfo += '<br>';
                shenShaInfo += otherShenInfo.join(' | ');
            }
            
            shenShaSection.innerHTML = shenShaInfo || '神煞: 无';
            
            // 组装卡片
            dayCard.appendChild(dateSection);
            if (dayData.scenario_assessment && dayData.scenario_assessment.status !== '未载') {
                const scenarioNames = { '结婚': '婚嫁', '搬家': '搬迁', '开业': '开市' };
                const scenarioMark = document.createElement('div');
                scenarioMark.className = `scenario-mark scenario-${dayData.scenario_assessment.status}`;
                const scenarioName = scenarioNames[dayData.scenario_assessment.scenario]
                    || dayData.scenario_assessment.scenario;
                scenarioMark.textContent = `${dayData.scenario_assessment.status}${scenarioName}`;
                dayCard.appendChild(scenarioMark);
            }
            dayCard.appendChild(suitableUnsuitableSection);
            dayCard.appendChild(shenShaSection);
            
            // 添加点击事件
            dayCard.addEventListener('click', () => {
                // 设置日期选择器的值
                const datePicker = document.getElementById('datePicker');
                if (datePicker) {
                    datePicker.value = dayData.date;
                    // 触发日期变更事件
                    fetchAndDisplayHuangliData(dayData.date);
                }
            });
            
            // 添加到网格
            gridContainer.appendChild(dayCard);
        });
        
        console.log("九天黄历数据处理完成，添加到DOM");
        
        // 将网格添加到容器
        weekHuangliContainer.appendChild(gridContainer);
        
    } catch (error) {
        console.error("显示九天黄历数据时出错:", error);
        showHuangliStatus('显示九天黄历失败，请稍后重试。', 'error');
    }
}

function showHuangliStatus(message, type = '') {
    const status = document.getElementById('huangliStatus');
    if (!status) return;
    status.textContent = message;
    status.dataset.type = type;
}
