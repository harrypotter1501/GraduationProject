// app.js
App({
  onLaunch() {
    // 展示本地存储能力
    const logs = wx.getStorageSync('logs') || []
    logs.unshift(Date.now())
    wx.setStorageSync('logs', logs)

    // 登录
    this.login()
    // 获取用户信息
    wx.getSetting({
      success: res => {
        if (res.authSetting['scope.userInfo']) {
          // 已经授权，可以直接调用 getUserInfo 获取头像昵称，不会弹框
          wx.getUserInfo({
            success: res => {
              // 可以将 res 发送给后台解码出 unionId
              this.globalData.userInfo = res.userInfo

              // 由于 getUserInfo 是网络请求，可能会在 Page.onLoad 之后才返回
              // 所以此处加入 callback 以防止这种情况
              if (this.userInfoReadyCallback) {
                this.userInfoReadyCallback(res)
              }
            }
          })
        }
      }
    })
  },
  login() {
    wx.login({
      success: res => {
        // 发送 res.code 到后台换取 openId, sessionKey, unionId
        if (res.code) {
          //var accountInfo = wx.getAccountInfoSync()
          wx.request({
            url: this.globalData.server + '/login',
            data: {
              code: res.code
            },
            success: res => {
              console.log(res)
              this.globalData.cookie = res.cookies[0]
              if (res.data === 'OK') {
                this.globalData.login = true
              } else if (res.data === 'REG') {
                console.log('Registration required.')
                this.globalData.register = true
              } else {
                console.error('WXLogin failed:', res.data)
              }
            }
          })
        } else {
          console.log('Login failed!' + res.errMsg)
        }
      }
    })
  },
  globalData: {
    userInfo: null,
    login: false,
    register: false,
    cookie: null,
    server: 'http://127.0.0.1:5000', //'http://119.29.13.194:5000',
    localServer: 'http://127.0.0.1:5000'
  }
})
