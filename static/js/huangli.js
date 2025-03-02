document.addEventListener('DOMContentLoaded', function() {
    console.log('页面加载完成，初始化黄历功能');
    
    // 检查DOM元素是否存在
    console.log('检查DOM元素:');
    console.log('datePicker元素:', document.getElementById('datePicker') ? '存在' : '不存在');
    console.log('weekHuangliContainer元素:', document.getElementById('weekHuangliContainer') ? '存在' : '不存在');
    
    // 获取当前日期
    const today = new Date();
    const datePicker = document.getElementById('datePicker');
    
    // 设置日期选择器的默认值为今天
    datePicker.valueAsDate = today;
    console.log('设置日期选择器默认值为:', formatDate(today));
    
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
        datePicker.valueAsDate = new Date();
        fetchAndDisplayHuangliData(formatDate(new Date()));
    });
    
    // 日期选择器变化事件
    datePicker.addEventListener('change', function() {
        fetchAndDisplayHuangliData(this.value);
    });
    
    // 初始加载今天的黄历数据
    fetchAndDisplayHuangliData(formatDate(today));
    
    // 加载九天黄历数据
    fetchAndDisplayNineDaysHuangliData();
    
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
    const timeElement = document.getElementById('currentTime');
    
    // 计算当前时辰
    const chineseHour = getChineseHour(hours);
    
    // 格式化当前时间
    const formattedTime = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;
    
    // 更新显示
    timeElement.textContent = `当前时辰: ${chineseHour} (${formattedTime})`;
    
    // 每分钟更新一次
    setTimeout(updateCurrentTime, 60000 - (now.getSeconds() * 1000));
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
    console.log('开始获取黄历数据:', date);
    fetch(`/api/huangli?date=${date}`)
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
                alert('获取黄历数据失败，请稍后再试。');
            }
        })
        .catch(error => {
            console.error('获取黄历数据出错:', error);
            alert('获取黄历数据出错，请稍后再试。');
        });
}

// 获取并显示九天黄历数据
function fetchAndDisplayNineDaysHuangliData() {
    console.log('开始获取九天黄历数据');
    fetch('/api/week_huangli')
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
                displayNineDaysHuangliData(data.data);
            } else {
                console.error('获取九天黄历数据失败:', data ? data.message : '未知错误');
                document.getElementById('weekHuangliContainer').innerHTML = '<div class="error">获取九天黄历数据失败，请稍后再试。</div>';
            }
        })
        .catch(error => {
            console.error('获取九天黄历数据出错:', error);
            document.getElementById('weekHuangliContainer').innerHTML = '<div class="error">获取九天黄历数据出错，请稍后再试。</div>';
        });
}

// 显示黄历数据
function displayHuangliData(data) {
    try {
        console.log("显示黄历数据:", data);
        
        // 更新日期标题
        document.getElementById('currentDate').textContent = data.date || '未知日期';
        
        // 更新日期信息
        document.getElementById('solarDate').textContent = data.date || '未知';
        document.getElementById('lunarDate').textContent = data.lunar_date || '未知';
        document.getElementById('ganZhi').textContent = `${data.gan_zhi_year || '未知'} ${data.gan_zhi_month || '未知'} ${data.gan_zhi_day || '未知'}`;
        
        // 更新时辰信息
        const ganZhiHourElement = document.getElementById('ganZhiHour');
        if (data.gan_zhi_hour) {
            ganZhiHourElement.textContent = data.gan_zhi_hour;
        } else {
            // 如果API没有返回时辰信息，则使用当前时辰
            const now = new Date();
            const hours = now.getHours();
            const chineseHour = getChineseHour(hours);
            ganZhiHourElement.textContent = chineseHour;
        }
        
        document.getElementById('zodiac').textContent = data.zodiac || '未知';
        
        // 更新节气
        document.getElementById('solarTermName').textContent = data.solar_term || '无';
        
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
        alert('显示黄历数据出错，请稍后再试。');
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
        alert("显示黄历数据失败，请刷新页面重试。");
    }
} 