import logger from './logger'

// 错误处理模块
class ErrorHandler {
  // 初始化错误处理
  static init(app) {
    // Vue 应用错误处理
    this.setupVueErrorHandler(app)
    
    // 全局未捕获错误处理
    this.setupGlobalErrorHandler()
    
    // 全局未处理的Promise拒绝
    this.setupUnhandledRejectionHandler()
  }

  // Vue 应用错误处理
  static setupVueErrorHandler(app) {
    app.config.errorHandler = (err, instance, info) => {
      logger.error('Vue 应用错误：', {
        error: err.message,
        stack: err.stack,
        info
      })
    }
  }

  // 全局未捕获错误处理
  static setupGlobalErrorHandler() {
    window.addEventListener('error', (event) => {
      logger.error('未捕获错误：', {
        message: event.message,
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
        error: event.error
      })
    })
  }

  // 全局未处理的Promise拒绝
  static setupUnhandledRejectionHandler() {
    window.addEventListener('unhandledrejection', (event) => {
      logger.error('未处理的Promise拒绝：', {
        reason: event.reason
      })
    })
  }
}

export default ErrorHandler