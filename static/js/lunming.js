/**
 * 论命功能的JavaScript代码
 * 处理用户输入、表单验证和结果展示
 */

document.addEventListener('DOMContentLoaded', () => {
    const analyzeBtn = document.getElementById('analyze-btn');
    const resetBtn = document.getElementById('reset-btn');
    const resultContainer = document.getElementById('result-container');
    const loadingContainer = document.getElementById('loading-container');
    const analysisContent = document.getElementById('analysis-content');
    
    // 初始化当前时间为表单默认值
    const today = new Date();
    const formattedDate = today.toISOString().split('T')[0];
    const formattedTime = today.getHours().toString().padStart(2, '0') + ':' + 
                          today.getMinutes().toString().padStart(2, '0');
    
    document.getElementById('birth-date').value = formattedDate;
    document.getElementById('birth-time').value = formattedTime;
    
    // 重置按钮事件
    resetBtn.addEventListener('click', () => {
        document.getElementById('name').value = '';
        document.querySelector('input[name="gender"][value="男"]').checked = true;
        
        // 日期重置已在lunar_date_handler.js中处理
        
        resultContainer.classList.add('hidden');
        analysisContent.innerHTML = '';
    });
    
    // 分析按钮事件
    analyzeBtn.addEventListener('click', async () => {
        // 获取表单数据
        const name = document.getElementById('name').value.trim();
        const gender = document.querySelector('input[name="gender"]:checked').value;
        const birthDate = document.getElementById('birth-date').value;
        const birthTime = document.getElementById('birth-time').value;
        
        // 表单验证
        if (!name) {
            alert('请输入姓名');
            return;
        }
        
        if (!birthDate) {
            alert('请选择出生日期');
            return;
        }
        
        if (!birthTime) {
            alert('请选择出生时间');
            return;
        }
        
        // 清空分析内容区域
        analysisContent.innerHTML = '';
        
        // 显示结果容器和加载状态
        resultContainer.classList.remove('hidden');
        loadingContainer.classList.remove('hidden');
        
        try {
            // 关闭之前可能存在的连接
            if (window.activeEventSource) {
                window.activeEventSource.close();
            }
            
            // 创建一个新的EventSource连接
            const eventSource = new EventSource(`/api/lunming/stream?name=${encodeURIComponent(name)}&gender=${encodeURIComponent(gender)}&birth_date=${encodeURIComponent(birthDate)}&birth_time=${encodeURIComponent(birthTime)}`);
            window.activeEventSource = eventSource; // 存储引用以便需要时关闭
            
            // 句子处理系统
            const sentenceProcessor = {
                buffer: '',            // 当前句子缓冲区
                isProcessing: false,   // 是否正在处理一个句子
                displayQueue: [],      // 待显示的句子队列
                startedProcessing: false, // 是否已开始处理内容
                initialTitle: false,   // 是否已处理第一个标题
                
                // 添加字符到缓冲区
                addChar(char) {
                    this.buffer += char;
                    
                    // 检查缓冲区是否包含完整的标题，即使该标题被分成多次接收
                    if (this.buffer.includes('###') && !this.initialTitle && this.buffer.includes('\n')) {
                        // 提取标题部分
                        const titleMatch = this.buffer.match(/###[^#\n]+/);
                        if (titleMatch) {
                            const title = titleMatch[0].trim();
                            // 将标题添加到队列
                            this.displayQueue.push(title);
                            this.initialTitle = true;
                            this.startedProcessing = true;
                            
                            // 删除已处理的标题
                            this.buffer = this.buffer.replace(titleMatch[0], '');
                            
                            // 如果当前没有在处理句子，开始处理
                            if (!this.isProcessing) {
                                this.processNextSentence();
                            }
                        }
                    }
                    
                    // 当遇到换行符时，表示一个句子结束
                    if (char === '\n') {
                        // 将完整的句子添加到显示队列
                        const sentence = this.buffer.trim();
                        
                        // 过滤掉任何包含"正在分析"或"请稍候"的消息
                        if (sentence && (sentence.includes("正在分析") || sentence.includes("请稍候"))) {
                            this.buffer = '';  // 清空缓冲区，不处理这个消息
                            return;
                        }
                        
                        if (sentence) {
                            this.startedProcessing = true;  // 标记已经开始处理实际内容
                            this.displayQueue.push(sentence);
                        }
                        
                        this.buffer = ''; // 重置缓冲区
                        
                        // 如果当前没有在处理句子，开始处理
                        if (!this.isProcessing) {
                            this.processNextSentence();
                        }
                    }
                },
                
                // 处理下一个句子
                processNextSentence() {
                    if (this.displayQueue.length === 0) {
                        this.isProcessing = false;
                        return;
                    }
                    
                    this.isProcessing = true;
                    const sentence = this.displayQueue.shift();
                    
                    // 判断句子类型（标题或内容）
                    if (this.isTitle(sentence)) {
                        this.displayTitle(sentence);
                    } else {
                        this.displayContent(sentence);
                    }
                },
                
                // 判断是否为标题
                isTitle(sentence) {
                    // 以 # 开头的是标题
                    return sentence.startsWith('#');
                },
                
                // 显示标题
                displayTitle(title) {
                    // 确定标题级别
                    const level = (title.match(/^#+/) || ['#'])[0].length;
                    const cleanTitle = title.replace(/^#+\s*/, '');
                    
                    // 创建标题元素
                    const titleElement = document.createElement(`h${Math.min(level, 6)}`);
                    titleElement.className = `analysis-title analysis-title-h${level}`;
                    analysisContent.appendChild(titleElement);
                    
                    // 字符动画显示
                    this.animateCharacters(titleElement, cleanTitle);
                },
                
                // 显示普通内容
                displayContent(content) {
                    // 检查是否为列表项（以-或*开头）
                    if (content.trim().startsWith('-') || content.trim().startsWith('*')) {
                        // 创建列表项元素
                        const listItem = document.createElement('div');
                        listItem.className = 'analysis-list-item';
                        analysisContent.appendChild(listItem);
                        
                        // 处理内容中的双星号加粗
                        const processedText = this.processBoldText(content.trim().substring(1).trim());
                        
                        // 字符动画显示（不允许HTML，将使用HTML元素方式）
                        this.animateCharacters(listItem, processedText, true);
                    } else {
                        // 创建普通段落元素
                        const paragraph = document.createElement('p');
                        paragraph.className = 'analysis-paragraph';
                        analysisContent.appendChild(paragraph);
                        
                        // 处理内容中的双星号加粗
                        const processedText = this.processBoldText(content);
                        
                        // 字符动画显示（允许HTML）
                        this.animateCharacters(paragraph, processedText, true);
                    }
                },
                
                // 处理双星号加粗文本
                processBoldText(text) {
                    // 将所有的**文本**替换为HTML加粗标签
                    return text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
                },
                
                // 逐字动画显示
                animateCharacters(element, text, allowHTML = false) {
                    // 如果文本包含HTML标签，需要特殊处理
                    if (allowHTML && text.includes('<strong>')) {
                        // 解析包含HTML的文本
                        const parser = new DOMParser();
                        const doc = parser.parseFromString(`<div>${text}</div>`, 'text/html');
                        const container = doc.body.firstChild;
                        
                        // 用于存储所有字符的数组（包括HTML节点）
                        const contentNodes = [];
                        
                        // 递归处理节点
                        function processNode(node) {
                            if (node.nodeType === Node.TEXT_NODE) {
                                // 如果是文本节点，将每个字符添加到数组
                                const textContent = node.textContent;
                                for (let i = 0; i < textContent.length; i++) {
                                    contentNodes.push({
                                        type: 'text',
                                        content: textContent[i]
                                    });
                                }
                            } else if (node.nodeType === Node.ELEMENT_NODE) {
                                if (node.tagName.toLowerCase() === 'strong') {
                                    // 如果是strong标签
                                    contentNodes.push({
                                        type: 'strong-start'
                                    });
                                    
                                    // 处理子节点
                                    for (const childNode of node.childNodes) {
                                        processNode(childNode);
                                    }
                                    
                                    contentNodes.push({
                                        type: 'strong-end'
                                    });
                                } else {
                                    // 处理其他标签的子节点
                                    for (const childNode of node.childNodes) {
                                        processNode(childNode);
                                    }
                                }
                            }
                        }
                        
                        // 处理container的所有子节点
                        for (const childNode of container.childNodes) {
                            processNode(childNode);
                        }
                        
                        // 清除元素内容
                        element.innerHTML = '';
                        
                        let isStrong = false;  // 跟踪是否在加粗范围内
                        let currentText = '';  // 当前累积的文本
                        let index = 0;         // 当前处理的索引
                        
                        // 使用定时器逐个显示字符
                        const displayInterval = setInterval(() => {
                            if (index < contentNodes.length) {
                                const node = contentNodes[index];
                                
                                if (node.type === 'strong-start') {
                                    // 当遇到strong开始标签时
                                    if (currentText) {
                                        // 添加之前累积的文本
                                        element.insertAdjacentText('beforeend', currentText);
                                        currentText = '';
                                    }
                                    isStrong = true;
                                } else if (node.type === 'strong-end') {
                                    // 当遇到strong结束标签时
                                    if (currentText) {
                                        // 添加加粗文本
                                        const strongElement = document.createElement('strong');
                                        strongElement.textContent = currentText;
                                        element.appendChild(strongElement);
                                        currentText = '';
                                    }
                                    isStrong = false;
                                } else if (node.type === 'text') {
                                    // 累积文本
                                    currentText += node.content;
                                    
                                    // 如果不在加粗范围内，直接添加文本
                                    if (!isStrong && currentText.length >= 3) {
                                        element.insertAdjacentText('beforeend', currentText);
                                        currentText = '';
                                    }
                                }
                                
                                index++;
                                
                                // 自动滚动到底部
                                analysisContent.scrollTop = analysisContent.scrollHeight;
                            } else {
                                // 处理可能剩余的文本
                                if (currentText) {
                                    if (isStrong) {
                                        const strongElement = document.createElement('strong');
                                        strongElement.textContent = currentText;
                                        element.appendChild(strongElement);
                                    } else {
                                        element.insertAdjacentText('beforeend', currentText);
                                    }
                                }
                                
                                // 字符显示完毕
                                clearInterval(displayInterval);
                                
                                // 处理队列中的下一个句子
                                setTimeout(() => {
                                    this.processNextSentence();
                                }, 100); // 短暂延迟，使句子之间有停顿感
                            }
                        }, 30); // 每个字符显示的间隔时间（毫秒）
                    } else {
                        // 原始的逐字显示逻辑，用于没有HTML的普通文本
                        const chars = text.split('');
                        let index = 0;
                        
                        // 清除可能的现有内容
                        element.textContent = '';
                        
                        // 使用定时器逐个显示字符
                        const displayInterval = setInterval(() => {
                            if (index < chars.length) {
                                // 添加下一个字符
                                element.textContent += chars[index];
                                index++;
                                
                                // 自动滚动到底部
                                analysisContent.scrollTop = analysisContent.scrollHeight;
                            } else {
                                // 字符显示完毕
                                clearInterval(displayInterval);
                                
                                // 处理队列中的下一个句子
                                setTimeout(() => {
                                    this.processNextSentence();
                                }, 100); // 短暂延迟，使句子之间有停顿感
                            }
                        }, 30); // 每个字符显示的间隔时间（毫秒）
                    }
                },
                
                // 处理流结束
                complete() {
                    // 处理缓冲区中可能剩余的内容
                    if (this.buffer.trim()) {
                        this.displayQueue.push(this.buffer.trim());
                        this.buffer = '';
                        
                        if (!this.isProcessing) {
                            this.processNextSentence();
                        }
                    }
                }
            };
            
            // 处理接收到的消息
            eventSource.onmessage = function(event) {
                // 获取返回的数据
                try {
                    const data = JSON.parse(event.data);
                    
                    // 处理完成信号
                    if (data.done) {
                        eventSource.close();
                        sentenceProcessor.complete();
                        loadingContainer.classList.add('hidden');
                        return;
                    }
                    
                    // 处理错误信息
                    if (data.error) {
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
                        // 过滤掉带有"正在分析"或"请稍候"的文本
                        if (data.text.includes("正在分析") || data.text.includes("请稍候")) {
                            return; // 跳过这些提示文本
                        }
                        sentenceProcessor.addChar(data.text);
                    }
                } catch (e) {
                    // 如果不是JSON格式，检查并过滤掉提示信息
                    if (event.data.includes("正在分析") || event.data.includes("请稍候")) {
                        return; // 跳过这些提示文本
                    }
                    // 如果不包含提示信息，直接将内容添加到处理器
                    sentenceProcessor.addChar(event.data);
                }
            };
            
            // 处理连接关闭
            eventSource.onclose = function() {
                console.log("EventSource连接已关闭");
                sentenceProcessor.complete();
                    loadingContainer.classList.add('hidden');
            };
            
            // 处理错误
            eventSource.onerror = function(event) {
                console.error("EventSource错误:", event);
                eventSource.close();
                
                // 显示错误信息（如果分析内容为空）
                if (analysisContent.children.length === 0) {
                    const errorP = document.createElement('p');
                    errorP.className = 'analysis-error';
                    errorP.textContent = "连接中断，请稍后重试";
                    analysisContent.appendChild(errorP);
                }
                
                loadingContainer.classList.add('hidden');
            };
            
        } catch (error) {
            console.error("启动分析时出错:", error);
            
            // 显示错误消息
            const errorP = document.createElement('p');
            errorP.className = 'analysis-error';
            errorP.textContent = `发生错误: ${error.message}`;
            analysisContent.appendChild(errorP);
            
            loadingContainer.classList.add('hidden');
        }
        });
}); 

