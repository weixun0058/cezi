/**
 * 论命功能的JavaScript代码
 * 处理用户输入、表单验证和结果展示
 */

document.addEventListener('DOMContentLoaded', function() {
    // 获取DOM元素
    const nameInput = document.getElementById('name');
    const birthDateInput = document.getElementById('birth-date');
    const birthTimeInput = document.getElementById('birth-time');
    const genderRadios = document.getElementsByName('gender');
    const resetBtn = document.getElementById('reset-btn');
    const analyzeBtn = document.getElementById('analyze-btn');
    const analysisContent = document.getElementById('analysis-content');
    const loadingContainer = document.getElementById('loading-container');
    const resultContainer = document.getElementById('result-container');
    
    // 初始化变量
    let textBuffer = '';
    let currentP = null;
    let initialP = null;
    
    // 设置当前日期时间作为默认值
    const now = new Date();
    birthDateInput.value = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
    birthTimeInput.value = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
    
    // 重置按钮事件
    resetBtn.addEventListener('click', function() {
        // 清空表单
        nameInput.value = '';
        document.querySelector('input[name="gender"][value="男"]').checked = true;
        birthDateInput.value = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
        birthTimeInput.value = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
        
        // 清空分析结果
        analysisContent.innerHTML = '';
        resultContainer.classList.add('hidden');
        loadingContainer.classList.add('hidden');
    });
    
    // 分析按钮事件
    analyzeBtn.addEventListener('click', async function() {
        console.log("分析按钮被点击");
        const name = nameInput.value;
        const gender = document.querySelector('input[name="gender"]:checked').value;
        const birthDate = birthDateInput.value;
        const birthTime = birthTimeInput.value;
        
        console.log("收集的数据:", { name, gender, birthDate, birthTime });
        
        // 验证输入
        if (!name || !birthDate || !birthTime) {
            alert('请填写完整信息');
            return;
        }
        
        // 显示加载动画
        loadingContainer.classList.remove('hidden');
        resultContainer.classList.remove('hidden'); // 立即显示结果容器
        analysisContent.innerHTML = '';
        
        // 创建初始段落
        currentP = document.createElement('p');
        currentP.className = 'analysis-content';
        analysisContent.appendChild(currentP);
        
        try {
            console.log("正在连接到服务器...");
            // 创建URL，添加时间戳防止缓存
            const timestamp = new Date().getTime();
            const url = `/api/lunming/stream?name=${encodeURIComponent(name)}&gender=${encodeURIComponent(gender)}&birth_date=${encodeURIComponent(birthDate)}&birth_time=${encodeURIComponent(birthTime)}&_=${timestamp}`;
            console.log("请求URL:", url);
            
            // 初始加载提示
            initialP = document.createElement('p');
            initialP.className = 'analysis-content';
            initialP.textContent = '正在连接服务器...';
            analysisContent.appendChild(initialP);
            
            // 添加超时检测
            let responseReceived = false;
            let connectionTimeout = setTimeout(() => {
                if (!responseReceived) {
                    console.error("API响应超时");
                    // 显示错误信息
                    const errorP = document.createElement('p');
                    errorP.className = 'analysis-error';
                    errorP.textContent = "服务器响应超时，请稍后重试";
                    analysisContent.appendChild(errorP);
                    loadingContainer.classList.add('hidden');
                    
                    // 如果EventSource已创建，关闭它
                    if (window.activeEventSource) {
                        window.activeEventSource.close();
                    }
                }
            }, 15000); // 15秒超时
            
            const eventSource = new EventSource(url);
            window.activeEventSource = eventSource; // 存储引用以便需要时关闭
            
            // 处理连接建立
            eventSource.onopen = function() {
                console.log("连接已建立");
                // 更新初始加载提示
                initialP.textContent = '连接已建立，正在等待分析结果...';
                // 设置超时计时器
                setTimeout(() => {
                    if (initialP.parentNode) {
                        initialP.textContent = '分析进行中，由于网络原因可能需要较长时间，请耐心等待...';
                    }
                }, 5000);
            };
            
            // 处理消息
            eventSource.onmessage = function(event) {
                responseReceived = true; // 标记收到响应
                clearTimeout(connectionTimeout); // 清除连接超时
                
                // 移除初始加载提示
                if (initialP && initialP.parentNode) {
                    analysisContent.removeChild(initialP);
                    initialP = null;
                }
                
                try {
                    console.log("收到消息:", event.data);
                    const data = JSON.parse(event.data);
                    
                    // 如果收到完成信号，关闭连接
                    if (data.done) {
                        console.log("分析完成");
                        // 处理可能存在的缓冲区内容
                        if (textBuffer.trim()) {
                            currentP.textContent = textBuffer.trim();
                        }
                        eventSource.close();
                        loadingContainer.classList.add('hidden');
                        return;
                    }
                    
                    // 处理错误
                    if (data.error) {
                        console.error("API错误:", data.error);
                        // 显示错误消息
                        const errorP = document.createElement('p');
                        errorP.className = 'analysis-error';
                        errorP.textContent = `分析过程中出现错误: ${data.error}`;
                        analysisContent.appendChild(errorP);
                        
                        eventSource.close();
                        loadingContainer.classList.add('hidden');
                        return;
                    }
                    
                    // 处理文本内容
                    if (data.text !== undefined) {
                        // 获取当前字符
                        const char = data.text;
                        
                        // 将字符添加到缓冲区
                        textBuffer += char;
                        
                        // 检测是否是段落结束（空行）
                        if (char === '\n' && textBuffer.endsWith('\n\n')) {
                            // 完成当前段落
                            currentP.textContent = textBuffer.trimEnd();
                            textBuffer = '';
                            
                            // 创建新段落
                            currentP = document.createElement('p');
                            currentP.className = 'analysis-content';
                            analysisContent.appendChild(currentP);
                            return;
                        }
                        
                        // 检测完整行
                        if (char === '\n') {
                            const line = textBuffer.trim();
                            
                            // 如果是空行，保留换行符
                            if (line === '') {
                                textBuffer = '\n';
                                return;
                            }
                            
                            // 处理Markdown标题: # 标题
                            if (line.match(/^#+\s+.+/)) {
                                // 创建标题元素
                                const titleP = document.createElement('p');
                                titleP.className = 'analysis-title';
                                // 去除所有#前缀和空格
                                titleP.textContent = line.replace(/^#+\s*/, '');
                                analysisContent.appendChild(titleP);
                                
                                // 重置缓冲区和创建新段落
                                textBuffer = '';
                                currentP = document.createElement('p');
                                currentP.className = 'analysis-content';
                                analysisContent.appendChild(currentP);
                                return;
                            }
                            
                            // 处理数字标题: 1. 标题
                            if (line.match(/^\d+\.\s+.+/)) {
                                // 仅当行较短且不像列表时当作标题处理
                                const isTitle = line.length < 50;
                                
                                if (isTitle) {
                                    // 创建标题元素
                                    const titleP = document.createElement('p');
                                    titleP.className = 'analysis-title';
                                    titleP.textContent = line;
                                    analysisContent.appendChild(titleP);
                                    
                                    // 重置缓冲区和创建新段落
                                    textBuffer = '';
                                    currentP = document.createElement('p');
                                    currentP.className = 'analysis-content';
                                    analysisContent.appendChild(currentP);
                                    return;
                                }
                            }
                            
                            // 处理列表项 (- 或 * 或 1. 开头)
                            if (line.match(/^(-|\*|\d+\.)\s+.+/)) {
                                // 这可能是列表项
                                const listP = document.createElement('p');
                                listP.className = 'analysis-list-item';
                                listP.textContent = line;
                                analysisContent.appendChild(listP);
                                
                                // 重置缓冲区，但不改变当前段落引用
                                textBuffer = '';
                                return;
                            }
                        }
                        
                        // 更新显示当前缓冲区内容
                        currentP.textContent = textBuffer;
                        
                        // 自动滚动到底部
                        currentP.scrollIntoView({ behavior: 'smooth', block: 'end' });
                    }
                } catch (e) {
                    console.error("处理消息时出错:", e, "原始数据:", event.data);
                    // 显示错误消息
                    const errorP = document.createElement('p');
                    errorP.className = 'analysis-error';
                    errorP.textContent = `处理消息时出错: ${e.message}`;
                    analysisContent.appendChild(errorP);
                }
            };
            
            // 处理错误
            eventSource.onerror = function(error) {
                console.error("EventSource错误:", error);
                eventSource.close();
                loadingContainer.classList.add('hidden');
                
                // 显示错误消息
                const errorP = document.createElement('p');
                errorP.className = 'analysis-error';
                errorP.textContent = "连接中断，请稍后重试";
                analysisContent.appendChild(errorP);
            };
            
        } catch (error) {
            console.error("启动分析时出错:", error);
            loadingContainer.classList.add('hidden');
            
            // 显示错误消息
            const errorP = document.createElement('p');
            errorP.className = 'analysis-error';
            errorP.textContent = `发生错误: ${error.message}`;
            analysisContent.appendChild(errorP);
        }
    });
});     });
});
