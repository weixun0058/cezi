document.addEventListener('DOMContentLoaded', function() {
    const inputs = document.querySelectorAll('.char-input');
    const calculateBtn = document.getElementById('calculateBtn');
    let strokes = [];
    let selectedType = null;

    function setStatus(message, type = '') {
        const status = document.getElementById('suanshiStatus');
        status.textContent = message;
        status.dataset.type = type;
    }

    // 修改检查输入函数，移除类型检查
    function checkInputs() {
        const allFilled = Array.from(inputs).every(input => 
            input.value.length === 1);
        calculateBtn.disabled = !allFilled;
    }

    // 输入框自动跳转
    inputs.forEach((input, index) => {
        input.addEventListener('input', function(e) {
            const value = e.target.value;
            if (value && !/^[\u4e00-\u9fa5]$/.test(value)) {
                e.target.value = '';
                return;
            }
            if (e.target.value.length === 1) {
                if (index < inputs.length - 1) {
                    inputs[index + 1].focus();
                }
            }
            checkInputs();
        });
    });

    calculateBtn.addEventListener('click', async function() {
        this.disabled = true;
        strokes = [];
        setStatus('正在查询笔画…');
        try {
            for (const input of inputs) {
                const response = await fetch('/get_strokes', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ character: input.value })
                });
                const data = await response.json();
                if (!response.ok || !data.strokes) throw new Error(data.error?.message || '笔画查询失败');
                strokes.push(data.strokes);
            }
        } catch (error) {
            setStatus(error.message || '笔画查询失败，请重试', 'error');
            return;
        } finally {
            this.disabled = false;
        }

        // 隐藏输入区域和介绍文本
        document.getElementById('characterInput').classList.add('hidden');
        document.querySelectorAll('.intro-text').forEach(element => {
            element.classList.add('hidden');
        });

        // 显示求测类型选择
        document.getElementById('qcTypeResult').classList.remove('hidden');
        setStatus('请选择求测方向');
    });

    // 求测类型按钮点击事件
    document.querySelectorAll('.qc-type-btn, .qc-sy-type-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            // 移除其他按钮的选中状态
            document.querySelectorAll('.qc-type-btn, .qc-sy-type-btn').forEach(b => 
                b.classList.remove('selected'));
            // 添加当前按钮的选中状态
            this.classList.add('selected');
            selectedType = this.dataset.type;
            
            // 隐藏求测类型区域
            document.getElementById('qcTypeResult').classList.add('hidden');
            
            // 显示笔画数结果
            document.getElementById('strokeResult').classList.remove('hidden');
            document.getElementById('stroke1').innerHTML = 
                `<span class="char-display">${inputs[0].value}</span>
                 <span class="stroke-display">${numToChineseUpper(strokes[0])}画</span>`;
            document.getElementById('stroke2').innerHTML = 
                `<span class="char-display">${inputs[1].value}</span>
                 <span class="stroke-display">${numToChineseUpper(strokes[1])}画</span>`;
            document.getElementById('stroke3').innerHTML = 
                `<span class="char-display">${inputs[2].value}</span>
                 <span class="stroke-display">${numToChineseUpper(strokes[2])}画</span>`;

            // 添加：确保显示"查看签号"按钮
            const showSignBtn = document.getElementById('showSignBtn');
            showSignBtn.classList.remove('hidden');
        });
    });

    // 添加数字转汉字函数
    function numToChineseUpper(num) {
        if (num < 0 || num > 99) {
            return num.toString();
        }

        const chineseUpperDigits = {
            0: '〇', 1: '一', 2: '二', 3: '三', 4: '四',
            5: '五', 6: '六', 7: '七', 8: '八', 9: '九'
        };

        if (num < 10) {
            return chineseUpperDigits[num];
        } else if (num < 20) {
            return '十' + (num === 10 ? '' : chineseUpperDigits[num % 10]);
        } else {
            const tens = Math.floor(num / 10);
            const ones = num % 10;
            return chineseUpperDigits[tens] + '十' + (ones === 0 ? '' : chineseUpperDigits[ones]);
        }
    }

    // 显示签号
    document.getElementById('showSignBtn').addEventListener('click', async function() {
        try {
            // 禁用按钮防止重复点击
            this.disabled = true;
            
            const response = await fetch('/calculate_sign', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ strokes: strokes })
            });
            const data = await response.json();
            
            if (!data || !data.sign_number) {
                throw new Error('无效的签号数据');
            }
            
            // 更新显示
            document.getElementById('signNumber').textContent = data.sign_number;
            document.getElementById('signResult').classList.remove('hidden');
            document.getElementById('strokeResult').classList.add('hidden');
            
            // 确保解卦按钮可见
            const showGuaBtn = document.getElementById('showGuaBtn');
            if (showGuaBtn) {
                // 移除所有可能的隐藏类
                showGuaBtn.classList.remove('hidden');
                showGuaBtn.style.display = 'block';
                
                // 使用 Promise 确保按钮渲染完成
                await new Promise(resolve => setTimeout(resolve, 100));
                
                // 检查按钮是否在视口内
                const buttonRect = showGuaBtn.getBoundingClientRect();
                if (buttonRect.bottom > window.innerHeight) {
                    window.scrollTo({
                        top: window.scrollY + buttonRect.bottom - window.innerHeight + 50,
                        behavior: 'smooth'
                    });
                }
            }
        } catch (error) {
            console.error('显示签号时出错:', error);
            setStatus('显示签号时出错，请重试', 'error');
        } finally {
            // 重新启用按钮
            this.disabled = false;
        }
    });

    // 修改显示卦象信息的部分
    document.getElementById('showGuaBtn').addEventListener('click', async function() {
        try {
            // 禁用按钮防止重复点击
            this.disabled = true;
            
            const signNumber = document.getElementById('signNumber').textContent;
            if (!signNumber) {
                throw new Error('未找到签号');
            }
            
            // 仅隐藏算事结果流程内的按钮，顶部导航始终可用
            document.querySelectorAll('.result-section .ancient-btn').forEach(btn => btn.classList.add('hidden'));
            document.querySelectorAll('.gua-section').forEach(section => section.classList.add('hidden'));
            
            const response = await fetch('/get_gua_info', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ sign_number: parseInt(signNumber) })
            });
            
            const data = await response.json();
            if (!response.ok || !data || data.error) {
                throw new Error(data.error?.message || '获取卦象信息失败');
            }
            
            // 保存数据
            window.guaData = data;
            
            // 更新显示
            document.getElementById('guaResult').classList.remove('hidden');
            document.getElementById('signResult').classList.add('hidden');
            
            // 显示签文区域并确保其可见
            const signSection = document.getElementById('signText').closest('.gua-section');
            signSection.classList.remove('hidden');
            
            // 逐字显示签文
            await typeWriter(document.getElementById('signText'), data.sign_text);
            
            // 确保下一个按钮可见
            const nextButton = document.getElementById('showGuaTypeBtn');
            if (nextButton) {
                nextButton.classList.remove('hidden');
                nextButton.style.display = 'block';
                
                // 检查按钮可见性
                await new Promise(resolve => setTimeout(resolve, 100));
                const buttonRect = nextButton.getBoundingClientRect();
                if (buttonRect.bottom > window.innerHeight) {
                    window.scrollTo({
                        top: window.scrollY + buttonRect.bottom - window.innerHeight + 50,
                        behavior: 'smooth'
                    });
                }
            }
        } catch (error) {
            console.error('显示卦象信息时出错:', error);
            setStatus('显示卦象信息时出错，请重试', 'error');
        } finally {
            // 重新启用按钮
            this.disabled = false;
        }
    });

    // 显示卦属
    document.getElementById('showGuaTypeBtn').addEventListener('click', async function() {
        this.classList.add('hidden');
        document.getElementById('guaTypeSection').classList.remove('hidden');
        
        await typeWriter(document.getElementById('guaType'), window.guaData.gua_type);
        showButton('showFortuneBtn');
    });

    // 显示吉凶
    document.getElementById('showFortuneBtn').addEventListener('click', async function() {
        this.classList.add('hidden');
        document.getElementById('fortuneSection').classList.remove('hidden');
        
        await typeWriter(document.getElementById('fortune'), window.guaData.fortune);
        showButton('showInterpretationBtn');
    });

    // 修改显示解签部分的代码
    document.getElementById('showInterpretationBtn').addEventListener('click', async function() {
        this.classList.add('hidden');
        document.getElementById('guaResult').classList.add('hidden');
        document.getElementById('interpretationResult').classList.remove('hidden');
        
        await typeWriter(document.getElementById('interpretation1'), 
            window.guaData.interpretation1);
        
        const typeMap = {
            'career': '事业',
            'wealth': '财运',
            'love': '情感',
            'health': '健康',
            'study': '学业',
            'general': '泛泛'
        };
        
        document.getElementById('specificTitle').textContent = 
            `${typeMap[selectedType]}解签`;
        await typeWriter(document.getElementById('specificInterpretation'), 
            window.guaData[selectedType]);
        showButton('restartBtn');
    });

    // 重新开始
    document.getElementById('restartBtn').addEventListener('click', function() {
        // 清空输入
        inputs.forEach(input => input.value = '');
        
        // 启用开始测算按钮（但保持禁用状态，直到输入完成）
        calculateBtn.disabled = true;
        calculateBtn.classList.remove('hidden');
        
        // 隐藏所有结果区域
        document.querySelectorAll('.result-section').forEach(section => {
            section.classList.add('hidden');
        });
        
        // 只重置算事流程按钮，不影响导航
        document.querySelectorAll('.result-section .ancient-btn').forEach(btn => {
            btn.classList.add('hidden');
        });
        
        // 清空所有内容
        document.getElementById('signText').textContent = '';
        document.getElementById('guaType').textContent = '';
        document.getElementById('fortune').textContent = '';
        document.getElementById('interpretation1').textContent = '';
        document.getElementById('specificInterpretation').textContent = '';
        
        // 重置所有section为隐藏状态
        document.getElementById('guaTypeSection').classList.add('hidden');
        document.getElementById('fortuneSection').classList.add('hidden');
        document.querySelectorAll('.interpretation-section').forEach(section => {
            section.classList.add('hidden');
        });
        
        // 显示输入区域和介绍文本
        document.getElementById('characterInput').classList.remove('hidden');
        document.querySelectorAll('.intro-text').forEach(element => {
            element.classList.remove('hidden');
        });
        // 显示导航按钮
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.remove('hidden');
        });
    });

    async function typeWriter(element, text, chunkSize = 3, interval = 45) {
        const characters = Array.from(text || '');
        element.textContent = '';

        if (!characters.length) return;
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            element.textContent = characters.join('');
            return;
        }

        for (let end = chunkSize; end < characters.length; end += chunkSize) {
            element.textContent = characters.slice(0, end).join('');

            if (end % (chunkSize * 6) === 0) {
                const elementRect = element.getBoundingClientRect();
                if (elementRect.bottom > window.innerHeight - 80) {
                    window.scrollBy({
                        top: Math.min(elementRect.bottom - window.innerHeight + 100, 240),
                        behavior: 'smooth'
                    });
                }
            }

            await new Promise(resolve => setTimeout(resolve, interval));
        }

        element.textContent = characters.join('');
    }

    // 添加一个通用的显示按钮函数
    function showButton(buttonId, delay = 500) {
        setTimeout(() => {
            const button = document.getElementById(buttonId);
            button.classList.remove('hidden');
            
            // 检查按钮是否在视口内
            const buttonRect = button.getBoundingClientRect();
            if (buttonRect.bottom > window.innerHeight) {
                const scrollOffset = buttonRect.bottom - window.innerHeight + 50;
                window.scrollBy({
                    top: scrollOffset,
                    behavior: 'smooth'
                });
            }
        }, delay);
    }

    // 添加全局错误处理
    window.addEventListener('error', function(event) {
        console.error('全局错误:', event.error);
    });

    // 添加按钮状态检查函数
    function checkButtonVisibility(buttonId) {
        const button = document.getElementById(buttonId);
        if (button && button.classList.contains('hidden')) {
            console.warn(`按钮 ${buttonId} 被隐藏，尝试显示`);
            button.classList.remove('hidden');
            button.style.display = 'block';
        }
    }

});
