import log from 'loglevel'

// 日志配置
const logger = log.getLogger('app')
logger.setLevel('debug')

// 读取项目里的 log.txt
async function readLogFile() {
  try {
    const res = await fetch('/log.txt')
    const text = await res.text()
    return text || ''
  } catch (e) {
    return ''
  }
}

// 写入 log.txt（追加模式）
async function appendToLogFile(newLine) {
  try {
    const oldContent = await readLogFile()
    const time = new Date().toLocaleString()
    const logLine = `[${time}] ${newLine}\n`
    const finalContent = oldContent + logLine

    // 把新内容写入 log.txt
    await fetch('/log.txt', {
      method: 'PUT',
      body: finalContent,
      headers: { 'Content-Type': 'text/plain' }
    })
  } catch (err) {
    console.error('写入日志失败', err)
  }
}

// 输出日志并自动写入文件
function autoLog(level, ...args) {
  const msg = args.join(' ')
  logger[level](msg)
  appendToLogFile(`[${level.toUpperCase()}] ${msg}`)
}

export default {
  debug(...args) { autoLog('debug', ...args) },
  info(...args) { autoLog('info', ...args) },
  warn(...args) { autoLog('warn', ...args) },
  error(...args) { autoLog('error', ...args) }
}