function formatDateTime(datetimeString) {
    const date = new Date(datetimeString);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${year}-${month}-${day} ${hours}:${minutes}`;
}

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

function confirmDelete(message = '确定要删除吗？') {
    return confirm(message);
}

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

    setTimeout(() => {
        alertDiv.remove();
    }, 3000);
}

function disableButton(button) {
    button.disabled = true;
    button.dataset.originalText = button.textContent;
    button.textContent = '加载中...';
}

function enableButton(button) {
    button.disabled = false;
    button.textContent = button.dataset.originalText || '提交';
}

function handleFormError(error, button) {
    console.error('表单提交错误：', error);
    showAlert('操作失败，请稍后重试', 'error');
    if (button) {
        enableButton(button);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const dateElements = document.querySelectorAll('.datetime-format');
    dateElements.forEach(element => {
        const datetime = element.textContent.trim();
        if (datetime) {
            element.textContent = formatDateTime(datetime);
        }
    });

    const deleteForms = document.querySelectorAll('.delete-form');
    deleteForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!confirmDelete('确定要删除这个投票吗？此操作无法撤销。')) {
                e.preventDefault();
            }
        });
    });
});

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
