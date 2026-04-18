import logger from './logger'

export default function setupErrorHandler(app) {
  // Vue 组件错误
  app.config.errorHandler = (err) => {
    logger.error('Vue 渲染错误：', err.message)
  }

  // Promise 错误（axios 走这里）
  window.addEventListener('unhandledrejection', (event) => {
    logger.error('Promise 异常：', event.reason.message)
    event.preventDefault()
  })

  // JS 全局错误
  window.addEventListener('error', (e) => {
    logger.error(`JS 错误：${e.message} (${e.filename}:${e.lineno})`)
  })
}