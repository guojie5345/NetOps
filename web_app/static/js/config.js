function toggleDeviceConfigs() {
    var button = document.getElementById("toggle-device-configs");
    var list = document.getElementById("device-configs-list");
    
    if (list.style.display === "none") {
        // 显示列表
        list.style.display = "block";
        button.textContent = "隐藏设备配置";
        button.classList.add("warning");
        // 重新初始化列拖动功能
        reinitTableResize();
    } else {
        // 隐藏列表
        list.style.display = "none";
        button.textContent = "查看设备配置";
        button.classList.remove("warning");
    }
}

function toggleRuleConfigs() {
    var button = document.getElementById("toggle-rule-configs");
    var list = document.getElementById("rule-configs-list");
    
    if (list.style.display === "none") {
        // 显示列表
        list.style.display = "block";
        button.textContent = "隐藏规则配置";
        button.classList.add("warning");
        
        // 动态加载规则配置文件列表
        loadRuleConfigs();
    } else {
        // 隐藏列表
        list.style.display = "none";
        button.textContent = "查看规则配置";
        button.classList.remove("warning");
    }
}

function toggleSystemConfigs() {
    var button = document.getElementById("toggle-system-configs");
    var list = document.getElementById("system-configs-list");
    
    if (list.style.display === "none") {
        // 显示列表
        list.style.display = "block";
        button.textContent = "隐藏系统设置";
        button.classList.add("warning");
        
        // 动态加载系统配置文件列表
        loadSystemConfigs();
    } else {
        // 隐藏列表
        list.style.display = "none";
        button.textContent = "查看系统设置";
        button.classList.remove("warning");
    }
}

function loadRuleConfigs() {
    fetch("/config/rule")
    .then(response => response.json())
    .then(data => {
        if (data.status === "success") {
            displayRuleConfigs(data.config_files);
        } else {
            document.getElementById("rule-configs-list").innerHTML = 
                '<div class="config-files-list"><p>加载规则配置文件列表失败: ' + data.message + '</p></div>';
        }
    })
    .catch(error => {
        document.getElementById("rule-configs-list").innerHTML = 
            '<div class="config-files-list"><p>加载规则配置文件列表时发生错误: ' + error + '</p></div>';
    });
}

function loadSystemConfigs() {
    fetch("/config/itsm")
    .then(response => response.json())
    .then(data => {
        if (data.status === "success") {
            displaySystemConfigs(data.config_files);
        } else {
            document.getElementById("system-configs-list").innerHTML = 
                '<div class="config-files-list"><p>加载系统配置文件列表失败: ' + data.message + '</p></div>';
        }
    })
    .catch(error => {
        document.getElementById("system-configs-list").innerHTML = 
            '<div class="config-files-list"><p>加载系统配置文件列表时发生错误: ' + error + '</p></div>';
    });
}

function displayRuleConfigs(configFiles) {
    var container = document.getElementById("rule-configs-list");
    
    if (configFiles.length === 0) {
        container.innerHTML = '<div class="config-files-list"><p>暂无规则配置文件</p></div>';
        return;
    }
    
    var html = `
        <div class="config-files-list">
            <h4>规则配置文件列表</h4>
            <table id="rule-config-table" class="table table-striped table-hover resizable-table">
                <thead class="thead-dark">
                    <tr>
                        <th class="filename-col resizable-col">文件名<div class="resize-handle"></div></th>
                        <th class="size-col resizable-col">大小 (字节)<div class="resize-handle"></div></th>
                        <th class="date-col resizable-col">修改时间<div class="resize-handle"></div></th>
                        <th class="action-col resizable-col">操作<div class="resize-handle"></div></th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    configFiles.forEach(function(file) {
        // 格式化时间
        var date = new Date(file.mtime * 1000);
        var formattedDate = date.getFullYear() + '-' + 
                            String(date.getMonth() + 1).padStart(2, '0') + '-' + 
                            String(date.getDate()).padStart(2, '0') + ' ' + 
                            String(date.getHours()).padStart(2, '0') + ':' + 
                            String(date.getMinutes()).padStart(2, '0') + ':' + 
                            String(date.getSeconds()).padStart(2, '0');
        
        html += `
            <tr>
                <td class="filename-col resizable-col">${file.filename}</td>
                <td class="size-col resizable-col">${file.size}</td>
                <td class="date-col resizable-col">${formattedDate}</td>
                <td class="action-col resizable-col action-buttons">
                    <a href="/config/view_rule/${encodeURIComponent(file.filename)}" class="btn btn-sm btn-primary action-btn">查看</a>
                    <a href="/config/edit_rule/${encodeURIComponent(file.filename)}" class="btn btn-sm btn-warning action-btn">编辑</a>
                    <button class="btn btn-sm btn-danger action-btn" onclick="deleteRuleConfig('${file.filename}')">删除</button>
                    <button class="btn btn-sm btn-info action-btn" onclick="backupRuleConfig('${file.filename}')">备份</button>
                    <button class="btn btn-sm btn-success action-btn" onclick="restoreRuleConfig('${file.filename}')">恢复</button>
                </td>
            </tr>
        `;
    });
    
    html += `
                </tbody>
            </table>
        </div>
    `;
    
    container.innerHTML = html;
    
    // 重新初始化列拖动功能
    setTimeout(function() {
        initTableResize();
    }, 100);
}

function displaySystemConfigs(configFiles) {
    var container = document.getElementById("system-configs-list");
    
    if (configFiles.length === 0) {
        container.innerHTML = '<div class="config-files-list"><p>暂无系统配置文件</p></div>';
        return;
    }
    
    var html = `
        <div class="config-files-list">
            <h4>系统配置文件列表</h4>
            <table id="system-config-table" class="table table-striped table-hover resizable-table">
                <thead class="thead-dark">
                    <tr>
                        <th class="filename-col resizable-col">文件名<div class="resize-handle"></div></th>
                        <th class="size-col resizable-col">大小 (字节)<div class="resize-handle"></div></th>
                        <th class="date-col resizable-col">修改时间<div class="resize-handle"></div></th>
                        <th class="action-col resizable-col">操作<div class="resize-handle"></div></th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    configFiles.forEach(function(file) {
        // 格式化时间
        var date = new Date(file.mtime * 1000);
        var formattedDate = date.getFullYear() + '-' + 
                            String(date.getMonth() + 1).padStart(2, '0') + '-' + 
                            String(date.getDate()).padStart(2, '0') + ' ' + 
                            String(date.getHours()).padStart(2, '0') + ':' + 
                            String(date.getMinutes()).padStart(2, '0') + ':' + 
                            String(date.getSeconds()).padStart(2, '0');
        
        html += `
            <tr>
                <td class="filename-col resizable-col">${file.filename}</td>
                <td class="size-col resizable-col">${file.size}</td>
                <td class="date-col resizable-col">${formattedDate}</td>
                <td class="action-col resizable-col action-buttons">
                    <a href="/config/view_itsm/${encodeURIComponent(file.filename)}" class="btn btn-sm btn-primary action-btn">查看</a>
                    <a href="/config/edit_itsm/${encodeURIComponent(file.filename)}" class="btn btn-sm btn-warning action-btn">编辑</a>
                    <button class="btn btn-sm btn-danger action-btn" onclick="deleteSystemConfig('${file.filename}')">删除</button>
                    <button class="btn btn-sm btn-info action-btn" onclick="backupSystemConfig('${file.filename}')">备份</button>
                    <button class="btn btn-sm btn-success action-btn" onclick="restoreSystemConfig('${file.filename}')">恢复</button>
                </td>
            </tr>
        `;
    });
    
    html += `
                </tbody>
            </table>
        </div>
    `;
    
    container.innerHTML = html;
    
    // 重新初始化列拖动功能
    setTimeout(function() {
        initTableResize();
    }, 100);
}

function deleteRuleConfig(filename) {
    if (confirm("确定要删除规则配置文件 " + filename + " 吗？此操作不可恢复！")) {
        fetch("/config/delete_rule/" + encodeURIComponent(filename), {
            method: "POST"
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                alert(data.message);
                // 重新加载规则配置列表
                loadRuleConfigs();
            } else {
                alert("删除失败: " + data.message);
            }
        })
        .catch(error => {
            alert("删除过程中发生错误: " + error);
        });
    }
}

function deleteSystemConfig(filename) {
    if (confirm("确定要删除系统配置文件 " + filename + " 吗？此操作不可恢复！")) {
        fetch("/config/delete_itsm/" + encodeURIComponent(filename), {
            method: "POST"
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                alert(data.message);
                // 重新加载系统配置列表
                loadSystemConfigs();
            } else {
                alert("删除失败: " + data.message);
            }
        })
        .catch(error => {
            alert("删除过程中发生错误: " + error);
        });
    }
}

function backupRuleConfig(filename) {
    fetch("/config/backup_rule/" + encodeURIComponent(filename), {
        method: "POST"
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === "success") {
            alert(data.message);
            // 重新加载规则配置列表
            loadRuleConfigs();
        } else {
            alert("备份失败: " + data.message);
        }
    })
    .catch(error => {
        alert("备份过程中发生错误: " + error);
    });
}

function backupSystemConfig(filename) {
    fetch("/config/backup_itsm/" + encodeURIComponent(filename), {
        method: "POST"
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === "success") {
            alert(data.message);
            // 重新加载系统配置列表
            loadSystemConfigs();
        } else {
            alert("备份失败: " + data.message);
        }
    })
    .catch(error => {
        alert("备份过程中发生错误: " + error);
    });
}

function restoreRuleConfig(filename) {
    if (confirm("确定要从备份恢复规则配置文件 " + filename + " 吗？这将覆盖当前文件！")) {
        fetch("/config/restore_rule/" + encodeURIComponent(filename), {
            method: "POST"
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                alert(data.message);
                // 重新加载规则配置列表
                loadRuleConfigs();
            } else {
                alert("恢复失败: " + data.message);
            }
        })
        .catch(error => {
            alert("恢复过程中发生错误: " + error);
        });
    }
}

function restoreSystemConfig(filename) {
    if (confirm("确定要从备份恢复系统配置文件 " + filename + " 吗？这将覆盖当前文件！")) {
        fetch("/config/restore_itsm/" + encodeURIComponent(filename), {
            method: "POST"
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                alert(data.message);
                // 重新加载系统配置列表
                loadSystemConfigs();
            } else {
                alert("恢复失败: " + data.message);
            }
        })
        .catch(error => {
            alert("恢复过程中发生错误: " + error);
        });
    }
}

function deleteConfig(filename) {
    if (confirm("确定要删除文件 " + filename + " 吗？此操作不可恢复！")) {
        fetch("/config/delete/" + encodeURIComponent(filename), {
            method: "POST"
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                alert(data.message);
                // 重新加载页面以更新文件列表
                location.reload();
            } else {
                alert("删除失败: " + data.message);
            }
        })
        .catch(error => {
            alert("删除过程中发生错误: " + error);
        });
    }
}

function backupConfig(filename) {
    fetch("/config/backup/" + encodeURIComponent(filename), {
        method: "POST"
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === "success") {
            alert(data.message);
            // 重新加载页面以显示备份文件
            location.reload();
        } else {
            alert("备份失败: " + data.message);
        }
    })
    .catch(error => {
        alert("备份过程中发生错误: " + error);
    });
}

function restoreConfig(filename) {
    if (confirm("确定要从备份恢复文件 " + filename + " 吗？这将覆盖当前文件！")) {
        fetch("/config/restore/" + encodeURIComponent(filename), {
            method: "POST"
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                alert(data.message);
                // 重新加载页面以更新文件状态
                location.reload();
            } else {
                alert("恢复失败: " + data.message);
            }
        })
        .catch(error => {
            alert("恢复过程中发生错误: " + error);
        });
    }
}

// 表格列拖动功能
function initTableResize() {
    const tables = document.querySelectorAll('.resizable-table');
    
    tables.forEach(table => {
        const ths = table.querySelectorAll('thead .resizable-col');
        const tds = table.querySelectorAll('tbody .resizable-col');
        
        // 从本地存储加载保存的列宽
        loadSavedColumnWidths(table, ths, tds);
        
        ths.forEach((th, index) => {
            const handle = th.querySelector('.resize-handle');
            if (!handle) return;
            
            let isResizing = false;
            let startX, startWidth;
            
            handle.addEventListener('mousedown', function(e) {
                isResizing = true;
                startX = e.clientX;
                startWidth = th.offsetWidth;
                
                // 添加活动状态
                handle.classList.add('active');
                
                // 防止文本选择
                e.preventDefault();
                
                // 添加全局事件监听器
                document.addEventListener('mousemove', handleMouseMove);
                document.addEventListener('mouseup', handleMouseUp);
            });
            
            function handleMouseMove(e) {
                if (!isResizing) return;
                
                const currentX = e.clientX;
                const diffX = currentX - startX;
                const newWidth = startWidth + diffX;
                
                // 设置最小宽度
                const minWidth = 50;
                if (newWidth >= minWidth) {
                    // 更新表头列宽
                    th.style.width = newWidth + 'px';
                    th.style.minWidth = newWidth + 'px';
                    
                    // 更新表体对应列的宽度
                    tds.forEach(td => {
                        if (td.cellIndex === index) {
                            td.style.width = newWidth + 'px';
                            td.style.minWidth = newWidth + 'px';
                        }
                    });
                }
            }
            
            function handleMouseUp() {
                if (!isResizing) return;
                
                isResizing = false;
                handle.classList.remove('active');
                
                // 保存调整后的列宽到本地存储
                saveColumnWidths(table, ths);
                
                // 移除全局事件监听器
                document.removeEventListener('mousemove', handleMouseMove);
                document.removeEventListener('mouseup', handleMouseUp);
            }
            
            // 双击重置列宽
            handle.addEventListener('dblclick', function() {
                // 获取原始宽度（从width属性或CSS类）
                const originalWidth = th.getAttribute('width') || 
                                    getComputedStyle(th).width;
                
                // 重置宽度
                th.style.width = originalWidth;
                th.style.minWidth = originalWidth;
                
                // 重置表体对应列的宽度
                tds.forEach(td => {
                    if (td.cellIndex === index) {
                        td.style.width = originalWidth;
                        td.style.minWidth = originalWidth;
                    }
                });
                
                // 从本地存储中删除保存的列宽
                clearSavedColumnWidths(table);
            });
        });
    });
}

// 保存列宽到本地存储
function saveColumnWidths(table, ths) {
    const columnWidths = {};
    
    ths.forEach((th, index) => {
        const className = th.className.split(' ').find(cls => cls.includes('-col'));
        if (className) {
            // 优先使用内联样式，如果没有则使用计算宽度
            columnWidths[className] = th.style.width || th.offsetWidth + 'px';
        }
    });
    
    // 使用表格ID作为键，如果没有ID则使用页面路径
    const tableId = table.id || 'config-table-default';
    const storageKey = `columnWidths_${tableId}`;
    
    localStorage.setItem(storageKey, JSON.stringify(columnWidths));
}

// 从本地存储加载列宽
function loadSavedColumnWidths(table, ths, tds) {
    const tableId = table.id || 'config-table-default';
    const storageKey = `columnWidths_${tableId}`;
    const savedWidths = localStorage.getItem(storageKey);
    
    if (savedWidths) {
        try {
            const columnWidths = JSON.parse(savedWidths);
            
            ths.forEach((th, index) => {
                const className = th.className.split(' ').find(cls => cls.includes('-col'));
                if (className && columnWidths[className]) {
                    // 应用保存的列宽（覆盖CSS固定宽度）
                    th.style.width = columnWidths[className];
                    th.style.minWidth = columnWidths[className];
                    
                    // 更新表体对应列的宽度
                    tds.forEach(td => {
                        if (td.cellIndex === index) {
                            td.style.width = columnWidths[className];
                            td.style.minWidth = columnWidths[className];
                        }
                    });
                }
            });
        } catch (error) {
            console.error('加载保存的列宽时出错:', error);
        }
    }
}

// 清除保存的列宽
function clearSavedColumnWidths(table) {
    const tableId = table.id || 'config-table-default';
    const storageKey = `columnWidths_${tableId}`;
    localStorage.removeItem(storageKey);
}

// 页面加载完成后初始化列拖动功能
document.addEventListener('DOMContentLoaded', function() {
    initTableResize();
});

// 当表格显示/隐藏时重新初始化列拖动功能
function reinitTableResize() {
    // 延迟执行以确保DOM已更新
    setTimeout(initTableResize, 100);
}