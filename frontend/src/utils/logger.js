// 日志工具类
class Logger {
  constructor() {
    this.logs = []
    this.maxLogs = 1000 // 最大日志数量
  }

  // 格式化时间
  _formatTime() {
    const now = new Date()
    const year = now.getFullYear()
    const month = String(now.getMonth() + 1).padStart(2, '0')
    const day = String(now.getDate()).padStart(2, '0')
    const hours = String(now.getHours()).padStart(2, '0')
    const minutes = String(now.getMinutes()).padStart(2, '0')
    const seconds = String(now.getSeconds()).padStart(2, '0')
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
  }

  // 添加日志
  _addLog(level, message, data) {
    const log = {
      level,
      message,
      data,
      timestamp: this._formatTime(),
      stack: new Error().stack
    }

    this.logs.push(log)
    
    // 限制日志数量
    if (this.logs.length > this.maxLogs) {
      this.logs.shift()
    }

    // 存储到本地
    this._saveToLocal()

    // 打印到控制台
    this._printToConsole(log)
  }

  // 保存到本地存储
  _saveToLocal() {
    try {
      localStorage.setItem('appLogs', JSON.stringify(this.logs))
    } catch (error) {
      console.error('日志存储失败：', error)
    }
  }

  // 从本地存储加载
  loadFromLocal() {
    try {
      const storedLogs = localStorage.getItem('appLogs')
      if (storedLogs) {
        this.logs = JSON.parse(storedLogs)
      }
    } catch (error) {
      console.error('日志加载失败：', error)
      this.logs = []
    }
  }

  // 打印到控制台
  _printToConsole(log) {
    const { level, message, data, timestamp } = log
    const prefix = `[${timestamp}] [${level.toUpperCase()}]`

    switch (level) {
      case 'debug':
        console.debug(prefix, message, data)
        break
      case 'info':
        console.info(prefix, message, data)
        break
      case 'warn':
        console.warn(prefix, message, data)
        break
      case 'error':
        console.error(prefix, message, data)
        break
      default:
        console.log(prefix, message, data)
    }
  }

  // 清除日志
  clear() {
    this.logs = []
    localStorage.removeItem('appLogs')
  }

  // 获取所有日志
  getAllLogs() {
    return this.logs
  }

  // 按级别获取日志
  getLogsByLevel(level) {
    return this.logs.filter(log => log.level === level)
  }

  // 调试日志
  debug(message, data = null) {
    this._addLog('debug', message, data)
  }

  // 信息日志
  info(message, data = null) {
    this._addLog('info', message, data)
  }

  // 警告日志
  warn(message, data = null) {
    this._addLog('warn', message, data)
  }

  // 错误日志
  error(message, data = null) {
    this._addLog('error', message, data)
  }
}

// 导出单例
const logger = new Logger()
logger.loadFromLocal()

export default logger