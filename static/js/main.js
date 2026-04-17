/**
 * 在线投票系统 JavaScript 主文件
 * 包含通用的交互逻辑和工具函数
 */

/**
 * 格式化日期时间
 * @param {string} datetimeString - ISO 格式的日期时间字符串
 * @returns {string} 格式化后的日期时间字符串
 */
function formatDateTime(datetimeString) {
    const date = new Date(datetimeString);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');

    return `${year}-${month}-${day} ${hours}:${minutes}`;
}

/**
 * 防抖函数
 * @param {Function} func - 要执行的函数
 * @param {number} wait - 等待时间（毫秒）
 * @returns {Function} 防抖处理后的函数
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * 确认删除操作
 * @param {string} message - 确认消息文本
 * @returns {boolean} 用户是否确认
 */
function confirmDelete(message = '确定要删除吗？') {
    return confirm(message);
}

/**
 * 显示提示消息
 * @param {string} message - 消息文本
 * @param {string} type - 消息类型 ('success', 'error', 'info')
 */
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;

    const container = document.querySelector('.main .container');
    const existingAlerts = container.querySelector('.flash-messages');

    if (existingAlerts) {
        existingAlerts.appendChild(alertDiv);
    } else {
        const flashMessages = document.createElement('div');
        flashMessages.className = 'flash-messages';
        flashMessages.appendChild(alertDiv);
        container.insertBefore(flashMessages, container.firstChild);
    }

    // 3秒后自动移除
    setTimeout(() => {
        alertDiv.remove();
    }, 3000);
}

/**
 * 禁用按钮并显示加载状态
 * @param {HTMLElement} button - 要禁用的按钮元素
 */
function disableButton(button) {
    button.disabled = true;
    button.dataset.originalText = button.textContent;
    button.textContent = '加载中...';
}

/**
 * 恢复按钮状态
 * @param {HTMLElement} button - 要恢复的按钮元素
 */
function enableButton(button) {
    button.disabled = false;
    button.textContent = button.dataset.originalText || '提交';
}

/**
 * 处理表单提交错误
 * @param {Error} error - 错误对象
 * @param {HTMLElement} button - 关联的按钮元素
 */
function handleFormError(error, button) {
    console.error('表单提交错误：', error);
    showAlert('操作失败，请稍后重试', 'error');
    if (button) {
        enableButton(button);
    }
}

/**
 * 页面加载完成后初始化
 */
document.addEventListener('DOMContentLoaded', function() {
    // 自动格式化页面中的日期时间
    const dateElements = document.querySelectorAll('.datetime-format');
    dateElements.forEach(element => {
        const datetime = element.textContent.trim();
        if (datetime) {
            element.textContent = formatDateTime(datetime);
        }
    });

    // 为所有删除表单添加确认处理
    const deleteForms = document.querySelectorAll('.delete-form');
    deleteForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!confirmDelete('确定要删除这个投票吗？此操作无法撤销。')) {
                e.preventDefault();
            }
        });
    });
});

/**
 * AJAX 请求工具函数
 * @param {string} url - 请求URL
 * @param {Object} options - 请求选项
 * @returns {Promise} Promise 对象
 */
async function fetchAPI(url, options = {}) {
    const defaultOptions = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    };

    const config = { ...defaultOptions, ...options };

    try {
        const response = await fetch(url, config);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || '请求失败');
        }

        return data;
    } catch (error) {
        console.error('API 请求错误：', error);
        throw error;
    }
}
