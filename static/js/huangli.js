document.addEventListener('DOMContentLoaded', function() {
    // 当前选中的日期
    let currentDate = new Date();
    
    // 格式化日期为YYYY-MM-DD
    function formatDate(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }
    
    // 格式化日期为更友好的显示格式
    function formatDisplayDate(date) {
        const year = date.getFullYear();
        const month = date.getMonth() + 1;
        const day = date.getDate();
        const weekDays = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六'];
        const weekDay = weekDays[date.getDay()];
        return `${year}年${month}月${day}日 ${weekDay}`;
    }
    
    // 根据月日获取星座
    function getStarSign(month, day) {
        const dates = [[1, 20], [2, 19], [3, 21], [4, 20], [5, 21], [6, 22], 
                      [7, 23], [8, 23], [9, 23], [10, 24], [11, 23], [12, 22]];
        const signs = ['水瓶座', '双鱼座', '白羊座', '金牛座', '双子座', '巨蟹座', 
                      '狮子座', '处女座', '天秤座', '天蝎座', '射手座', '摩羯座'];
        
        if (day < dates[month-1][1]) {
            return signs[month-1];
        } else {
            return signs[month % 12];
        }
    }
    
    // 加载黄历数据
    async function loadHuangliData(date) {
        try {
            const dateStr = formatDate(date);
            const response = await fetch(`/api/huangli?date=${dateStr}`);
            
            if (!response.ok) {
                throw new Error('获取黄历数据失败');
            }
            
            const data = await response.json();
            displayHuangliData(data, date);
            
        } catch (error) {
            console.error('加载黄历数据出错:', error);
            alert('加载黄历数据时出错，请重试');
        }
    }
    
    // 显示黄历数据
    function displayHuangliData(data, date) {
        // 调试日志
        console.log("黄历数据:", data);
        console.log("彭祖百忌:", data.peng_zu_bai_ji);
        console.log("喜神:", data.xi_shen);
        console.log("福神:", data.fu_shen);
        console.log("财神:", data.cai_shen);
        
        // 显示日期信息
        document.getElementById('currentDate').textContent = formatDisplayDate(date);
        document.getElementById('solarDate').textContent = formatDisplayDate(date);
        document.getElementById('lunarDate').textContent = data.lunar_date || '无';
        
        // 显示天干地支和生肖
        const ganZhiText = `${data.gan_zhi_year || ''} ${data.gan_zhi_month || ''} ${data.gan_zhi_day || ''}`;
        document.getElementById('ganZhi').textContent = ganZhiText;
        document.getElementById('ganZhiHour').textContent = data.gan_zhi_hour || '无';
        document.getElementById('zodiac').textContent = data.zodiac || '无';
        
        // 显示宜忌
        const suitableItems = data.suitable ? data.suitable.split('、') : [];
        const unsuitableItems = data.unsuitable ? data.unsuitable.split('、') : [];
        displayListItems('suitable', suitableItems);
        displayListItems('unsuitable', unsuitableItems);
        
        // 显示彭祖百忌
        document.getElementById('pengZuBaiJi').textContent = data.peng_zu_bai_ji || '无';
        
        // 显示神煞信息
        document.getElementById('chongSha').textContent = data.chong_sha || '无';
        document.getElementById('xiShen').textContent = data.xi_shen || '无';
        document.getElementById('fuShen').textContent = data.fu_shen || '无';
        document.getElementById('caiShen').textContent = data.cai_shen || '无';
        document.getElementById('jiShen').textContent = data.ji_shen || '无';
        document.getElementById('xiongShen').textContent = data.xiong_shen || '无';
        
        // 显示节气信息（如果有）
        const solarTermSection = document.getElementById('solarTermSection');
        if (data.solar_term && data.solar_term !== '无') {
            document.getElementById('solarTermName').textContent = data.solar_term;
            solarTermSection.classList.remove('hidden');
        } else {
            solarTermSection.classList.add('hidden');
        }
        
        // 显示节日信息（如果有）
        const festivalSection = document.getElementById('festivalSection');
        const festivalList = document.getElementById('festivalList');
        
        if (data.festivals && data.festivals.length > 0) {
            festivalList.innerHTML = '';
            
            data.festivals.forEach(festival => {
                const festivalItem = document.createElement('div');
                festivalItem.className = 'festival-item';
                
                const festivalName = document.createElement('div');
                festivalName.className = 'festival-name';
                festivalName.textContent = `${festival.name} (${festival.type})`;
                
                festivalItem.appendChild(festivalName);
                festivalList.appendChild(festivalItem);
            });
            
            festivalSection.classList.remove('hidden');
        } else {
            festivalSection.classList.add('hidden');
        }
    }
    
    // 显示列表项
    function displayListItems(elementId, items) {
        const container = document.getElementById(elementId);
        container.innerHTML = '';
        
        if (items.length === 0) {
            const span = document.createElement('span');
            span.className = 'tag';
            span.textContent = '无';
            container.appendChild(span);
            return;
        }
        
        items.forEach(item => {
            if (item.trim()) {
                const span = document.createElement('span');
                span.className = 'tag';
                span.textContent = item;
                container.appendChild(span);
            }
        });
    }
    
    // 加载九天黄历数据
    async function loadNineDaysHuangliData() {
        try {
            const response = await fetch('/api/huangli/week');
            
            if (!response.ok) {
                throw new Error('获取九天黄历数据失败');
            }
            
            const data = await response.json();
            displayNineDaysHuangliData(data);
            
        } catch (error) {
            console.error('加载九天黄历数据出错:', error);
            alert('加载九天黄历数据时出错，请重试');
        }
    }
    
    // 显示九天黄历数据
    function displayNineDaysHuangliData(weekData) {
        const weekContainer = document.getElementById('weekHuangliContainer');
        if (!weekContainer) return;
        
        weekContainer.innerHTML = '';
        
        // 获取今天的日期字符串，用于比较
        const todayStr = formatDate(new Date());
        
        weekData.forEach(dayData => {
            const date = new Date(dayData.date);
            
            const dayCard = document.createElement('div');
            dayCard.className = 'day-card';
            
            // 如果是今天，添加active类
            if (dayData.date === todayStr) {
                dayCard.classList.add('active');
            }
            
            // 日期头部
            const dayHeader = document.createElement('div');
            dayHeader.className = 'day-header';
            
            const dayName = document.createElement('div');
            dayName.className = 'day-name';
            dayName.textContent = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'][date.getDay()];
            
            const dayDate = document.createElement('div');
            dayDate.className = 'day-date';
            dayDate.textContent = `${date.getMonth() + 1}月${date.getDate()}日`;
            
            dayHeader.appendChild(dayName);
            dayHeader.appendChild(dayDate);
            
            // 日期内容
            const dayContent = document.createElement('div');
            dayContent.className = 'day-content';
            
            const lunarDate = document.createElement('div');
            lunarDate.className = 'lunar-date';
            lunarDate.textContent = dayData.lunar_date || '无';
            
            const ganZhiDay = document.createElement('div');
            ganZhiDay.className = 'gan-zhi-day';
            ganZhiDay.textContent = dayData.gan_zhi_day || '无';
            
            const suitableItem = document.createElement('div');
            suitableItem.className = 'day-suitable';
            
            // 处理宜忌数据，取第一项显示
            let suitableText = '无';
            if (dayData.suitable) {
                const suitableItems = dayData.suitable.split('、');
                if (suitableItems.length > 0 && suitableItems[0].trim()) {
                    suitableText = suitableItems[0];
                }
            }
            suitableItem.innerHTML = `<span class="label">宜:</span> ${suitableText}`;
            
            const unsuitableItem = document.createElement('div');
            unsuitableItem.className = 'day-unsuitable';
            
            let unsuitableText = '无';
            if (dayData.unsuitable) {
                const unsuitableItems = dayData.unsuitable.split('、');
                if (unsuitableItems.length > 0 && unsuitableItems[0].trim()) {
                    unsuitableText = unsuitableItems[0];
                }
            }
            unsuitableItem.innerHTML = `<span class="label">忌:</span> ${unsuitableText}`;
            
            // 添加冲煞信息
            const chongShaItem = document.createElement('div');
            chongShaItem.className = 'day-chong-sha';
            
            let chongText = '无';
            if (dayData.chong_sha) {
                try {
                    // 提取冲的动物
                    const match = dayData.chong_sha.match(/冲(.*?)[\(（]/);
                    if (match && match[1]) {
                        chongText = match[1];
                    } else {
                        chongText = dayData.chong_sha.replace('冲', '');
                    }
                } catch (e) {
                    console.error('处理冲煞信息出错:', e);
                    chongText = '无';
                }
            }
            chongShaItem.innerHTML = `<span class="label">冲:</span> ${chongText}`;
            
            dayContent.appendChild(lunarDate);
            dayContent.appendChild(ganZhiDay);
            dayContent.appendChild(suitableItem);
            dayContent.appendChild(unsuitableItem);
            dayContent.appendChild(chongShaItem);
            
            // 组装卡片
            dayCard.appendChild(dayHeader);
            dayCard.appendChild(dayContent);
            
            // 添加点击事件，点击卡片跳转到对应日期
            dayCard.addEventListener('click', () => {
                currentDate = date;
                loadHuangliData(date);
                
                // 更新日期选择器
                const datePicker = document.getElementById('datePicker');
                if (datePicker) {
                    datePicker.valueAsDate = date;
                }
                
                // 移除其他卡片的active类，给当前卡片添加active类
                document.querySelectorAll('.day-card').forEach(card => {
                    card.classList.remove('active');
                });
                dayCard.classList.add('active');
            });
            
            weekContainer.appendChild(dayCard);
        });
    }
    
    // 初始化
    function init() {
        // 加载当天黄历
        loadHuangliData(currentDate);
        
        // 加载九天黄历
        loadNineDaysHuangliData();
        
        // 绑定日期选择器
        const datePicker = document.getElementById('datePicker');
        if (datePicker) {
            datePicker.valueAsDate = currentDate;
            datePicker.addEventListener('change', (e) => {
                currentDate = new Date(e.target.value);
                loadHuangliData(currentDate);
            });
        }
        
        // 绑定前一天按钮
        const prevDayBtn = document.getElementById('prevDayBtn');
        if (prevDayBtn) {
            prevDayBtn.addEventListener('click', () => {
                currentDate = new Date(currentDate.getTime() - 86400000); // 减去一天的毫秒数
                if (datePicker) datePicker.valueAsDate = currentDate;
                loadHuangliData(currentDate);
            });
        }
        
        // 绑定后一天按钮
        const nextDayBtn = document.getElementById('nextDayBtn');
        if (nextDayBtn) {
            nextDayBtn.addEventListener('click', () => {
                currentDate = new Date(currentDate.getTime() + 86400000); // 加上一天的毫秒数
                if (datePicker) datePicker.valueAsDate = currentDate;
                loadHuangliData(currentDate);
            });
        }
        
        // 绑定今天按钮
        const todayBtn = document.getElementById('todayBtn');
        if (todayBtn) {
            todayBtn.addEventListener('click', () => {
                currentDate = new Date();
                if (datePicker) datePicker.valueAsDate = currentDate;
                loadHuangliData(currentDate);
                loadNineDaysHuangliData();
            });
        }
    }
    
    // 页面加载完成后初始化
    init();
}); 