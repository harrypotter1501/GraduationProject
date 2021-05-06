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
    // wx.request({
    //   url: this.globalData.server + '/login',
    //   data: {
    //     code: 'test_system'
    //   },
    //   success: (res) => {
    //     console.log(res)
    //     this.globalData.cookie = res.cookies[0]
    //     this.globalData.login = true
    //   },
    //   fail: (res) => {
    //     console.error(res)
    //   }
    // })
    // return
    this.globalData.requestCompleteCallback = this.setCookie
    wx.login({
      success: (res) => {
        // 发送 res.code 到后台换取 openId, sessionKey, unionId
        var code = 'test'
        if (res.code) {
          code = res.code
        } else {
          console.log('Login failed!' + res.errMsg)
          code = 'test'
        }
        wx.request({
          url: this.globalData.server + '/login',
          data: {
            code: code
          },
          success: (res) => {
            console.log(res)
            if (res.data === 'OK') {
              this.globalData.login = true
            } else if (res.data === 'REG') {
              console.log('Registration required.')
              this.globalData.register = true
            } else {
              console.error('WXLogin failed:', res.data)
            }
          },
          fail: (res) => {
            console.error(res)
          },
          complete: (res) => {
            this.globalData.requestCompleteCallback(res)
          }
        })
      },
      fail: (res) => {
        console.log(res)
      }
    })
  },
  setCookie (res) {
    if (res.cookies.length != 0) {
      this.globalData.cookie = res.cookies[0]
    }
  },
  globalData: {
    userInfo: null,
    login: false,
    register: false,
    cookie: null,
    server: 'http://127.0.0.1:8080', //'http://119.29.13.194:8080',
    //localServer: 'http://127.0.0.1:5000'
    requestCompleteCallback: null,
  }
})
