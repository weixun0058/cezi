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
        // 显示日期信息
        document.getElementById('currentDate').textContent = formatDisplayDate(date);
        document.getElementById('solarDate').textContent = formatDisplayDate(date);
        document.getElementById('lunarDate').textContent = data.lunar_date;
        
        // 显示天干地支和生肖
        const ganZhiText = `${data.gan_zhi_year} ${data.gan_zhi_month} ${data.gan_zhi_day}`;
        document.getElementById('ganZhi').textContent = ganZhiText;
        document.getElementById('zodiac').textContent = data.zodiac;
        document.getElementById('starSign').textContent = getStarSign(date.getMonth() + 1, date.getDate());
        
        // 显示宜忌
        displayListItems('suitable', data.suitable.split('、'));
        displayListItems('unsuitable', data.unsuitable.split('、'));
        
        // 显示吉祥信息
        document.getElementById('luckyDirection').textContent = data.lucky_direction;
        document.getElementById('luckyColor').textContent = data.lucky_color;
        document.getElementById('luckyNumber').textContent = data.lucky_number;
        
        // 显示神煞信息
        document.getElementById('chongSha').textContent = data.chong_sha;
        document.getElementById('jiShen').textContent = data.ji_shen;
        document.getElementById('xiongShen').textContent = data.xiong_shen;
        
        // 显示当日运势
        document.getElementById('dayFortune').textContent = data.day_fortune;
        
        // 显示节气信息（如果有）
        const solarTermSection = document.getElementById('solarTermSection');
        if (data.solar_term) {
            document.getElementById('solarTermName').textContent = data.solar_term.name;
            document.getElementById('solarTermDesc').textContent = data.solar_term.description;
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
                
                const festivalDesc = document.createElement('div');
                festivalDesc.className = 'festival-desc';
                festivalDesc.textContent = festival.description;
                
                festivalItem.appendChild(festivalName);
                festivalItem.appendChild(festivalDesc);
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
        
        items.forEach(item => {
            if (item.trim()) {
                const span = document.createElement('span');
                span.className = 'tag';
                span.textContent = item;
                container.appendChild(span);
            }
        });
    }
    
    // 加载一周黄历数据
    async function loadWeekHuangliData() {
        try {
            const startDate = formatDate(currentDate);
            const response = await fetch(`/api/huangli/week?start_date=${startDate}`);
            
            if (!response.ok) {
                throw new Error('获取一周黄历数据失败');
            }
            
            const data = await response.json();
            displayWeekHuangliData(data);
            
        } catch (error) {
            console.error('加载一周黄历数据出错:', error);
            alert('加载一周黄历数据时出错，请重试');
        }
    }
    
    // 显示一周黄历数据
    function displayWeekHuangliData(weekData) {
        const weekContainer = document.getElementById('weekHuangliContainer');
        if (!weekContainer) return;
        
        weekContainer.innerHTML = '';
        
        weekData.forEach(dayData => {
            const date = new Date(dayData.date);
            
            const dayCard = document.createElement('div');
            dayCard.className = 'day-card';
            
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
            lunarDate.textContent = dayData.lunar_date;
            
            const ganZhiDay = document.createElement('div');
            ganZhiDay.className = 'gan-zhi-day';
            ganZhiDay.textContent = dayData.gan_zhi_day;
            
            const suitableItem = document.createElement('div');
            suitableItem.className = 'day-suitable';
            suitableItem.innerHTML = `<span class="label">宜:</span> ${dayData.suitable}`;
            
            const unsuitableItem = document.createElement('div');
            unsuitableItem.className = 'day-unsuitable';
            unsuitableItem.innerHTML = `<span class="label">忌:</span> ${dayData.unsuitable}`;
            
            dayContent.appendChild(lunarDate);
            dayContent.appendChild(ganZhiDay);
            dayContent.appendChild(suitableItem);
            dayContent.appendChild(unsuitableItem);
            
            // 组装卡片
            dayCard.appendChild(dayHeader);
            dayCard.appendChild(dayContent);
            
            // 添加点击事件，点击卡片跳转到对应日期
            dayCard.addEventListener('click', () => {
                currentDate = date;
                loadHuangliData(date);
            });
            
            weekContainer.appendChild(dayCard);
        });
    }
    
    // 初始化
    function init() {
        // 加载当天黄历
        loadHuangliData(currentDate);
        
        // 加载一周黄历
        loadWeekHuangliData();
        
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
                loadWeekHuangliData();
            });
        }
    }
    
    // 页面加载完成后初始化
    init();
}); 