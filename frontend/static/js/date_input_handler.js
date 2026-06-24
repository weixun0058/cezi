/**
 * 日期输入框处理工具
 * 用于处理日期输入框的格式化和键盘事件
 */

function setupDateInput(inputElement, onChange) {
    if (!inputElement) return;
    
    // 设置日期选择器的默认值为今天
    const today = new Date();
    inputElement.valueAsDate = today;
    
    // 添加日期选择器的change事件监听器
    inputElement.addEventListener('change', function() {
        const selectedDate = this.value;
        if (selectedDate && typeof onChange === 'function') {
            onChange(selectedDate);
        }
    });
    
    // 添加回车键确认事件
    inputElement.addEventListener('keyup', function(e) {
        if (e.key === 'Enter') {
            const selectedDate = this.value;
            if (selectedDate && typeof onChange === 'function') {
                onChange(selectedDate);
            }
        }
    });

    // 处理键盘输入事件
    inputElement.addEventListener('keydown', function(e) {
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
                    
                    // 日期输入完成，触发回调
                    if (typeof onChange === 'function') {
                        setTimeout(() => {
                            onChange(this.value);
                        }, 0);
                    }
                    return;
                }
            }
        }
    });
} 