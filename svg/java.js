document.addEventListener('DOMContentLoaded', function () {
    /* 发送消息模块 */
    const chatContainer = document.getElementById('chatContainer');
    const textInput = document.getElementById('typing');
    const sendMessageButton = document.getElementById('send');
    // 发送消息
    sendMessageButton.addEventListener('click', function () {
        const inputText = textInput.value;
        if (inputText.trim() !== '') {
            const xml = new XMLHttpRequest();
            xml.open('POST', 'http://localhost:8081/text');
            xml.setRequestHeader('Content-Type', 'application/json');
            xml.send(JSON.stringify({userInput: inputText}));
            // 先清除之前的"server-message-wallpaper"
            const previousServerWallpapers = document.querySelectorAll('.server-message-wallpaper');
            previousServerWallpapers.forEach(function (element) {
                element.remove();
            });
            appendMessage('user', inputText); // 显示用户发送的消息
            textInput.value = ''; // 清空输入框
        }
    });


    // 文件接受
    function appendFile(sender, message) {
        const messageDiv = document.createElement('div');
        const messageDivunder = document.createElement('div');
        const messageText = document.createElement('div');
        const fill2 = document.createElement('span');
        fill2.className = 'fill2';
        // 创建包含消息文本的元素
        messageDiv.className = `${sender}-message-file`;
        // 创建小人logo
        const img = document.createElement('img');
        const deleted = document.createElement('img');
        img.src = 'svg/guy.svg'; // 设置服务器图像的路径
        deleted.src = 'svg/filedelete.svg'; // 设置服务器图像的路径
        img.className = 'avatar'; // 设置图像的样式类
        deleted.className = 'file_delete';
        messageDiv.appendChild(img);
        messageDiv.appendChild(fill2);
        messageDivunder.appendChild(messageText);
        messageDivunder.appendChild(deleted);
        messageDiv.appendChild(messageDivunder);
        messageDivunder.className = 'line1';
        messageText.textContent = `${message}`;
        // 添加图像和消息文本到消息容器
        messageDiv.appendChild(messageDivunder);
        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight; // 滚动到底部
        // 获取具有'file_delete'类的所有元素
        const elements = document.getElementsByClassName('file_delete');
        // 遍历每个元素并添加点击事件监听器
        for (let i = 0; i < elements.length; i++) {
            elements[i].addEventListener('click', function () {
                if (fstate) {
                    fstate = false;
                    const xml = new XMLHttpRequest();
                    xml.open('DELETE', `http://localhost:8081/data/${file_name}`);
                    xml.onreadystatechange = function () {
                        if (xml.readyState === 4 && xml.status === 200) {
                            const obj = JSON.parse(xml.responseText);
                            appendMessage('server', obj["message"]);
                        }
                    };
                    xml.send();
                }
            });
        }
    }

    // 接收服务器消息
    function appendMessage(sender, message) {
        const messageDiv = document.createElement('div');
        const messageText = document.createElement('div');
        const fill2 = document.createElement('span');
        fill2.className = 'fill2';
        // 创建包含消息文本的元素
        messageDiv.className = `${sender}-message`;
        if (sender === 'server') {
            // 创建小人logo
            const img = document.createElement('img');
            img.src = 'svg/guy.svg'; // 设置服务器图像的路径
            img.className = 'avatar'; // 设置图像的样式类
            messageDiv.appendChild(img);
            messageDiv.appendChild(fill2);
            messageText.className = 'line1';
        }
        messageText.textContent = `${message}`;
        // 添加图像和消息文本到消息容器
        messageDiv.appendChild(messageText);
        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight; // 滚动到底部
    }

    /* 壁纸模式 */
    // 壁纸模式服务器消息显示
    const next_wallpaper = document.createElement('img');
    const last_wallpaper = document.createElement('img');
    const set_wallpaper = document.createElement('img');
    const generate_wallpaper = document.createElement('img');

    next_wallpaper.src = 'svg/next_wallpaper.svg';
    last_wallpaper.src = 'svg/last_wallpaper.svg';
    set_wallpaper.src = 'svg/set_wallpaper.svg';
    generate_wallpaper.src = 'svg/generate_wallpaper.svg';

    // 创建壁纸
    const wallpaper = document.createElement('img');
    wallpaper.className = 'wallpaper'

    /// 定义包含初始图片路径的数组
    let imagePaths = [];
    console.log(imagePaths);
    let currentImageIndex = 0; // 当前显示的图片索引

    function appendIMG(sender, location) {
        const messageDiv = document.createElement('div');
        const fill2 = document.createElement('span');
        const fill3 = document.createElement('span');
        fill2.className = 'fill2';
        messageDiv.className = `${sender}-message-wallpaper`;

        console.log(location)
        // 创建小人logo
        const avatar = document.createElement('img');
        avatar.src = 'svg/guy.svg'; // 设置服务器图像的路径
        avatar.className = 'avatar'; // 设置图像的样式类
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(fill2);
        // 创建包含消息文本的元素
        const messageText = document.createElement('div');
        messageText.className = 'line2';
        messageText.textContent = '您可以选择将本张图片设置为您的桌面壁纸，也可以试试新的图片';
        messageDiv.appendChild(messageText);

//        wallpaper_list = JSON.parse(`${location}`);
//        console.log(wallpaper_list);
        // 将接收的图片路径存入imagePaths

        imagePaths = imagePaths.concat(location);
        console.log(imagePaths);
        for (const item of imagePaths) {
            wallpaper.src = item;
            messageDiv.appendChild(wallpaper);
        }

//      messageDiv.appendChild(imagePaths[0]);
        // 创建控制栏
        const chooser = document.createElement('div');
        /// 控制栏填充
        const fill4 = document.createElement('div'); //
        const fill5 = document.createElement('div');
        const fill6 = document.createElement('div');
        const fill7 = document.createElement('div');
        const fill8 = document.createElement('div');

        fill4.className = 'fill'; //中侧填充
        fill5.className = 'fill'; //中侧填充
        fill8.className = 'fill'; //中侧填充
        fill6.className = 'fill3'; //左右两侧填充
        fill7.className = 'fill3'; //左右两侧填充
        /// 控制栏控件
        chooser.className = 'chooser';
        chooser.appendChild(fill6);
        chooser.appendChild(last_wallpaper);
        chooser.appendChild(fill4);
        chooser.appendChild(generate_wallpaper);
        chooser.appendChild(fill8);
        chooser.appendChild(set_wallpaper);
        chooser.appendChild(fill5);
        chooser.appendChild(next_wallpaper);
        chooser.appendChild(fill7);

        messageDiv.appendChild(chooser);

        currentImageIndex += 4;
        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight; // 滚动到底部
    }

    // 壁纸轮播
    generate_wallpaper.addEventListener('click', function () {
        const newImagePath = 'svg/1.png'; // 替换成你的新图片路径
        addImageToPaths(newImagePath);
    });

    set_wallpaper.addEventListener('click', function () {
        const xml = new XMLHttpRequest();
        xml.open('POST', 'http://localhost:8081/image');
        xml.setRequestHeader('Content-Type', 'application/json');
        console.log(imagePaths[currentImageIndex])
        xml.send(JSON.stringify({wall_path: imagePaths[currentImageIndex]}));

    });

    next_wallpaper.addEventListener('click', function () {
        if (imagePaths.length > 0) {
            currentImageIndex = (currentImageIndex + 1) % imagePaths.length; // 循环显示图片
            wallpaper.src = imagePaths[currentImageIndex]; // 更新wallpaper元素的src属性
        }
    });

    last_wallpaper.addEventListener('click', function () {
        if (imagePaths.length > 0) {
            currentImageIndex = (currentImageIndex - 1 + imagePaths.length) % imagePaths.length; // 循环显示图片
            wallpaper.src = imagePaths[currentImageIndex]; // 更新wallpaper元素的src属性
        }
    });

    function addImageToPaths(imagePath) {
        imagePaths.push(imagePath);
        currentImageIndex = imagePaths.length - 1;
        console.log(imagePaths)
    }

    /* 接收消息模块 */

    // 接收消息到服务器的函数
    function getMessage() {
        const xml = new XMLHttpRequest();
        xml.open('POST', 'http://localhost:8081/audio');
        xml.setRequestHeader('Content-Type', 'application/json');
        xml.onreadystatechange = function () {
            if (xml.readyState === 4 && xml.status === 200) {
                const obj = JSON.parse(xml.responseText);
                if (obj["bot"]) {
                    if ("location" in obj) {
                        appendIMG('server', obj["location"]);
                    } else if ('result' in obj) {
                        if ('follow' in obj) {
                            if (obj['follow']) {
                                const lastMessageDiv = chatContainer.lastElementChild;
                                lastMessageDiv.textContent = `${obj["result"]}`;
                            } else {
                                appendMessage('server', obj["result"]);
                            }
                        } else {
                            appendMessage('server', obj["result"]);
                        }
                    }
                } else {
                    appendMessage('user', obj["result"])
                }
                getMessage()
            }
        }
        xml.send(JSON.stringify({userInput: "content"}));
    }

    getMessage()

    /* mode栏弹出 */
    const openTextingButton = document.querySelector('.typing');
    const closeModalButton = document.querySelector('.mid');
    const closeModalButton2 = document.querySelector('.send');
    const modalOverlay = document.querySelector('.texting_mode');

    openTextingButton.addEventListener('click', function () {
        modalOverlay.classList.add('active');
    });

    closeModalButton.addEventListener('click', function () {
        modalOverlay.classList.remove('active');
    });

    closeModalButton2.addEventListener('click', function () {
        modalOverlay.classList.remove('active');
    });

    /* 模式选择栏的弹出与隐藏 */
    // 获取元素
    const textingModeChoose = document.querySelector('.texting_mode_choose');
    const dropdownContent = document.querySelector('.dropdown-content');

    // 点击 text_mode_choose 显示 dropdown-content
    textingModeChoose.addEventListener('click', function () {
        dropdownContent.classList.toggle('show');
    });

    // 获取所有的 dropdown-content 中的 a 元素
    const dropdownLinks = document.querySelectorAll('.dropdown-content a');

    // 点击 dropdown-content 中的任何一个 a 元素隐藏 dropdown-content
    dropdownLinks.forEach(function (link) {
        link.addEventListener('click', function () {
            dropdownContent.classList.remove('show');
        });
    });

    /* 切换模式状态 */
    const dom = {
        net: document.getElementById('net'),
        analyze: document.getElementById('analyze'),
        paint: document.getElementById('paint'),
        chat: document.getElementById('chat'),
        stat: document.getElementById('texting_mode_status'),
        stat2: document.querySelector('.texting_mode_status2'),
        file: document.querySelector('.file'),//上传文件按钮
    };

    let state = '';
    let fstate = false;
    let file_name = '';

    // 切换联网模式
    dom.net.addEventListener('click', () => {
        if (state !== 'net') {
            state = 'net';
            dom.stat.textContent = '联网模式';
            dom.stat2.textContent = '联网';
            const xml = new XMLHttpRequest();
            xml.open('POST', 'http://localhost:8081/text2');
            xml.setRequestHeader('Content-Type', 'application/json');
            xml.send(JSON.stringify({switch: 3}));
        }
    })

    // 切换功能模式
    dom.analyze.addEventListener('click', () => {
        if (state !== 'analyze') {
            state = 'analyze';
            dom.stat.textContent = '功能模式';
            dom.stat2.textContent = '功能';
            const xml = new XMLHttpRequest();
            xml.open('POST', 'http://localhost:8081/text2');
            xml.setRequestHeader('Content-Type', 'application/json');
            xml.send(JSON.stringify({switch: 4}));
        }
    });

    // 切换绘画模式
    dom.paint.addEventListener('click', () => {
        if (state !== 'paint') {
            state = 'paint';
            dom.stat.textContent = '壁纸模式';
            dom.stat2.textContent = '壁纸';
            const xml = new XMLHttpRequest();
            xml.open('POST', 'http://localhost:8081/text2');
            xml.setRequestHeader('Content-Type', 'application/json');
            xml.send(JSON.stringify({switch: 6}));
        }
    });

    // 切换聊天模式
    dom.chat.addEventListener('click', () => {
        if (state !== 'chat') {
            state = 'chat';
            dom.stat.textContent = '聊天模式';
            dom.stat2.textContent = '聊天';
            const xml = new XMLHttpRequest();
            xml.open('POST', 'http://localhost:8081/text2');
            xml.setRequestHeader('Content-Type', 'application/json');
            xml.send(JSON.stringify({switch: 0}));
        }
    });

    // 文件分析
    dom.file.addEventListener('click', () => {
        if (!fstate) {
            fstate = !fstate;
            const fileInput = document.createElement('input');
            fileInput.type = 'file';
            fileInput.addEventListener('change', (event) => {
                const selectedFile = event.target.files[0];
                if (selectedFile) {
                    const xml = new XMLHttpRequest();
                    xml.open('POST', 'http://localhost:8081/data');
                    const formData = new FormData();
                    formData.append('file', selectedFile);
                    xml.onreadystatechange = function () {
                        if (xml.readyState === 4 && xml.status === 200) {
                            const obj = JSON.parse(xml.responseText);
                            file_name = obj["filename"];
                            appendFile('server', obj["message"]);
                        }
                    };
                    xml.send(formData);
                }
            });
            fileInput.click();
        }
    });
});