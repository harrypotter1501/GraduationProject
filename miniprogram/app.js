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
    wx.getUserProfile({
      desc: 'For login purpose', // 声明获取用户个人信息后的用途，后续会展示在弹窗中，请谨慎填写
      success: (res) => {
        this.setData({
          userInfo: res.userInfo,
          hasUserInfo: true
        })
      }
    })
  },
  login() {
    wx.login({
      success: (res) => {
        // 发送 res.code 到后台换取 openId, sessionKey, unionId
        if (res.code) {
          //var accountInfo = wx.getAccountInfoSync()
          wx.request({
            url: this.globalData.server + '/login',
            data: {
              code: res.code
            },
            success: (res) => {
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
      },
      fail: (res) => {
        console.log(res)
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
