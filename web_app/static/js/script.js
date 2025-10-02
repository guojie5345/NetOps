// 全局JavaScript文件

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 可以在这里添加全局的JavaScript代码
    console.log('自动化运维工具Web应用程序已加载');
});

// 显示消息函数
function showMessage(message, type = 'info') {
    // 创建消息元素
    const messageElement = document.createElement('div');
    messageElement.className = `message message-${type}`;
    messageElement.textContent = message;

    // 添加到页面顶部
    const container = document.querySelector('.container');
    container.insertBefore(messageElement, container.firstChild);

    // 3秒后自动移除消息
    setTimeout(() => {
        messageElement.remove();
    }, 3000);
}

// 确认对话框函数
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// 表单验证函数
function validateForm(formId) {
    const form = document.getElementById(formId);
    const inputs = form.querySelectorAll('input[required]');

    for (let input of inputs) {
        if (!input.value.trim()) {
            showMessage(`请输入${input.previousElementSibling.textContent}`, 'error');
            return false;
        }
    }

    return true;
}