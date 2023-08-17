const dom = {
    text: document.querySelectorAll('.text'), msg: document.querySelector('.msg-svg'),//功能模式按钮
    earth: document.querySelector('.earth-svg'),//联网模式按钮
    ipt: document.querySelector('.ipt'), textFields: document.querySelector('.textFields'),//用户文本框内容
    affirm: document.querySelector('.affirm-svg'),//用户文本框内容发送键
    uls: document.querySelector('.uls'), file: document.querySelector('.file-svg'),//上传文件按钮
};

for (let i = 0; i < dom.text.length; i++) {
    if (dom.text[i].parentNode.className === 'chat' && dom.text[i].offsetHeight > 39) {
        dom.text[i].style.borderBottomRightRadius = '15px';
        dom.text[i].style.borderTopRightRadius = '15px';
    } else if (dom.text[i].parentNode.className === 'user' && dom.text[i].offsetHeight > 39) {
        dom.text[i].style.borderBottomLeftRadius = '15px';
        dom.text[i].style.borderTopLeftRadius = '15px';
    }
}

//默认聊天模式=normal
let state = 'normal';
let fstate = 'no';
let file_name = ''

dom.msg.addEventListener('click', () => {
    if (dom.msg.getAttribute('fill') === '#1B2841') {
        dom.msg.setAttribute('fill', 'white');
        dom.earth.setAttribute('fill', '#1B2841');
    } else {
        dom.msg.setAttribute('fill', '#1B2841');
    }
    //切换为功能模式=info
    if (state !== 'info') {
        state = 'info';
        dom.msg.setAttribute('fill', 'white');
        dom.earth.setAttribute('fill', '#1B2841');
        const xml = new XMLHttpRequest();
        xml.open('POST', 'http://localhost:8081/text2');
        xml.setRequestHeader('Content-Type', 'application/json');
        xml.onreadystatechange = function () {
            if (xml.readyState === 4 && xml.status === 200) {
                const temp = xml.responseText.replace(/"/g, '').replace(/\\n/g, '<br>');
                const chatLiHTML = `
                <li class="chat">
                    <div class="logo"><img src="./static/logo.svg" alt=""></div>
                    <div class="text">${temp}</div>
                </li>`;
                dom.uls.insertAdjacentHTML('beforeend', chatLiHTML);
            }
        };
        xml.send(JSON.stringify({
            switch: 4
        }));
    } else {
        //返回默认聊天模式
        state = 'normal';
        dom.msg.setAttribute('fill', '#1B2841');
        const xml = new XMLHttpRequest();
        xml.open('POST', 'http://localhost:8081/text2');
        xml.setRequestHeader('Content-Type', 'application/json');
        xml.onreadystatechange = function () {
            if (xml.readyState === 4 && xml.status === 200) {
                const temp = xml.responseText.replace(/"/g, '').replace(/\\n/g, '<br>');
                const chatLiHTML = `
                <li class="chat">
                    <div class="logo"><img src="./static/logo.svg" alt=""></div>
                    <div class="text">${temp}</div>
                </li>`;
                dom.uls.insertAdjacentHTML('beforeend', chatLiHTML);
            }
        };
        xml.send(JSON.stringify({switch: 0}));
    }
    if (dom.uls.lastElementChild.querySelector('.text').clientHeight > 85) {
        const txtElements = document.querySelectorAll('.text');
        txtElements.forEach(txtElement => {
            txtElement.style.borderBottomLeftRadius = '20px';
            txtElement.style.borderTopLeftRadius = '20px';
        });
    }
});

//联网模式=earth，需要改写接口部门
dom.earth.addEventListener('click', () => {
    if (dom.earth.getAttribute('fill') === '#1B2841') {
        dom.earth.setAttribute('fill', 'white');
        dom.msg.setAttribute('fill', '#1B2841');
    } else {
        dom.earth.setAttribute('fill', '#1B2841');
    }
    if (state !== 'earth') {
        state = 'earth';
        dom.earth.setAttribute('fill', 'white');
        dom.msg.setAttribute('fill', '#1B2841');
        const xml = new XMLHttpRequest();
        xml.open('POST', 'http://localhost:8081/text2');
        xml.setRequestHeader('Content-Type', 'application/json');
        xml.onreadystatechange = function () {
            if (xml.readyState === 4 && xml.status === 200) {
                const temp = xml.responseText.replace(/"/g, '').replace(/\\n/g, '<br>');
                const chatLiHTML = `
                <li class="chat">
                    <div class="logo"><img src="./static/logo.svg" alt=""></div>
                    <div class="text">${temp}</div>
                </li>`;
                dom.uls.insertAdjacentHTML('beforeend', chatLiHTML);
            }
        };
        xml.send(JSON.stringify({switch: 3}));
    } else {
        state = 'normal';
        dom.earth.setAttribute('fill', '#1B2841');
        const xml = new XMLHttpRequest();
        xml.open('POST', 'http://localhost:8081/text2');
        xml.setRequestHeader('Content-Type', 'application/json');
        xml.onreadystatechange = function () {
            if (xml.readyState === 4 && xml.status === 200) {
                const temp = xml.responseText.replace(/"/g, '').replace(/\\n/g, '<br>');
                const chatLiHTML = `
                <li class="chat">
                    <div class="logo"><img src="./static/logo.svg" alt=""></div>
                    <div class="text">${temp}</div>
                </li>`;
                dom.uls.insertAdjacentHTML('beforeend', chatLiHTML);
            }
        };
        xml.send(JSON.stringify({switch: 0}));
    }
    if (dom.uls.lastElementChild.querySelector('.text').clientHeight > 85) {
        const txtElements = document.querySelectorAll('.text');
        txtElements.forEach(txtElement => {
            txtElement.style.borderBottomLeftRadius = '20px';
            txtElement.style.borderTopLeftRadius = '20px';
        });
    }
});

//监听回车键
dom.textFields.addEventListener('keydown', (e) => {
    if (e.key === "Enter") {
        e.preventDefault();
        const val = dom.textFields.value.trim();
        if (val !== '') {
            const userLiHTML = `
                <li class="user">
                    <div class="text">${val}</div>
                    <div class="user-svg"> <img src="./static/images/user.svg" alt=""> </div>
                </li>`;
            dom.uls.insertAdjacentHTML('beforeend', userLiHTML);
            // ai
            const xml = new XMLHttpRequest();
            xml.open('POST', 'http://localhost:8081/text');
            xml.setRequestHeader('Content-Type', 'application/json');
            xml.send(JSON.stringify({userInput: val}));
            if (dom.uls.lastElementChild.querySelector('.text').clientHeight > 85) {
                const txtElements = document.querySelectorAll('.text');
                txtElements.forEach(txtElement => {
                    txtElement.style.borderBottomLeftRadius = '20px';
                    txtElement.style.borderTopLeftRadius = '20px';
                });
            }
            dom.textFields.value = '';
        }
    }
});

//监听点击键，和上面类似，需要改写接口
dom.affirm.addEventListener('click', (e) => {
    const val = dom.textFields.value.trim();
    // 用户
    if (val !== '') {
        const userLiHTML = `
            <li class="user">
                <div class="text">${val}</div>
                <div class="user-svg"> <img src="./static/images/user.svg" alt=""> </div>
            </li>`;
        dom.uls.insertAdjacentHTML('beforeend', userLiHTML);
        const xml = new XMLHttpRequest();
        xml.open('POST', 'http://localhost:8081/text');
        xml.setRequestHeader('Content-Type', 'application/json');
        xml.send(JSON.stringify({userInput: val}));
        if (dom.uls.lastElementChild.querySelector('.text').clientHeight > 85) {
            const txtElements = document.querySelectorAll('.text');
            txtElements.forEach(txtElement => {
                txtElement.style.borderBottomLeftRadius = '20px';
                txtElement.style.borderTopLeftRadius = '20px';
            });
        }
        dom.textFields.value = '';
    }
});

//切换上传文件模式，需要改写接口
dom.file.addEventListener('click', () => {
    if (dom.file.getAttribute('fill') === '#1B2841') {
        dom.file.setAttribute('fill', 'white');
    } else {
        dom.file.setAttribute('fill', '#1B2841');
    }
    if (fstate === 'no') {
        fstate = 'yes'
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.addEventListener('change', (event) => {
            const selectedFile = event.target.files[0];
            if (selectedFile) {
                const xhr = new XMLHttpRequest();
                xhr.open('POST', 'http://localhost:8081/data');
                const formData = new FormData();
                formData.append('file', selectedFile);
                xhr.onreadystatechange = function () {
                    if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
                        const obj = JSON.parse(xhr.responseText);
                        file_name = obj["filename"]
                        const chatLiHTML = `
                        <li class="chat">
                            <div class="logo"><img src="./static/logo.svg" alt=""></div>
                            <div class="text">${obj["message"]}</div>
                        </li>`;
                        dom.uls.insertAdjacentHTML('beforeend', chatLiHTML);
                        if (dom.uls.lastElementChild.querySelector('.text').clientHeight > 85) {
                            const txtElements = document.querySelectorAll('.text');
                            txtElements.forEach(txtElement => {
                                txtElement.style.borderBottomLeftRadius = '20px';
                                txtElement.style.borderTopLeftRadius = '20px';
                            });
                        }
                    }
                };
                xhr.send(formData);
            }
        });
        fileInput.click();
    } else {
        fstate = 'no'
        const xhr = new XMLHttpRequest();
        xhr.open('DELETE', `http://localhost:8081/data/${file_name}`);
        xhr.onreadystatechange = function () {
            if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
                const obj = JSON.parse(xhr.responseText);
                const chatLiHTML = `
                <li class="chat">
                    <div class="logo"><img src="./static/logo.svg" alt=""></div>
                    <div class="text">${obj["message"]}</div>
                </li>`;
                dom.uls.insertAdjacentHTML('beforeend', chatLiHTML);
                if (dom.uls.lastElementChild.querySelector('.text').clientHeight > 85) {
                    const txtElements = document.querySelectorAll('.text');
                    txtElements.forEach(txtElement => {
                        txtElement.style.borderBottomLeftRadius = '20px';
                        txtElement.style.borderTopLeftRadius = '20px';
                    });
                }
            }
        };
        xhr.send()
    }
});

document.addEventListener('DOMContentLoaded', () => {
    dom.textFields.focus();
});

function getMessage() {
    const xml = new XMLHttpRequest();
    xml.open('POST', 'http://localhost:8081/audio');
    xml.setRequestHeader('Content-Type', 'application/json');
    xml.onreadystatechange = function () {
        if (xml.readyState === 4 && xml.status === 200) {
            const obj = JSON.parse(xml.responseText);
            if (obj["bot"]) {
                const chatHTML = `
                <li class="chat">
                    <div class="logo"> <img src="./static/logo.svg" alt=""> </div>
                    <div class="text"> ${obj["result"]} </div>
                </li>`;
                dom.uls.insertAdjacentHTML('beforeend', chatHTML);
            } else {
                const userHTML = `
                <li class="user">
                    <div class="text">${obj["result"]}</div>
                    <div class="user-svg"><img src="./static/images/user.svg" alt=""></div>
                </li>`;
                dom.uls.insertAdjacentHTML('beforeend', userHTML);
            }
            if (dom.uls.lastElementChild.querySelector('.text').clientHeight > 85) {
                const txtElements = document.querySelectorAll('.text');
                txtElements.forEach(txtElement => {
                    txtElement.style.borderBottomLeftRadius = '20px';
                    txtElement.style.borderTopLeftRadius = '20px';
                });
            }
            getMessage()
        }
    }
    xml.send(JSON.stringify({userInput: "content"}));
}

getMessage()