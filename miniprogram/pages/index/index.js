// index.js
// 获取应用实例
const app = getApp()

Page({
  data: {
    motto: 'Hello World',
    userInfo: {},
    hasUserInfo: false,
    canIUse: wx.canIUse('button.open-type.getUserInfo'),
    login: false
  },
  // 事件处理函数
  bindViewTap() {
    /*wx.request({
      url: app.globalData.server + '/test',
      header: {
        'content-type': 'application/x-www-form-urlencoded',
        'cookie': app.globalData.cookie
      },
      success: res => {
        console.log(res)
      }
    })*/
    return
    wx.navigateTo({
      url: '../logs/logs'
    })
  },
  bindTextTap() {
    wx.navigateTo({
      url: '../test/test',
    })
  },
  onLoad() {
    if (app.globalData.userInfo) {
      this.setData({
        userInfo: app.globalData.userInfo,
        hasUserInfo: true
      })
    } else if (this.data.canIUse) {
      // 由于 getUserInfo 是网络请求，可能会在 Page.onLoad 之后才返回
      // 所以此处加入 callback 以防止这种情况
      app.userInfoReadyCallback = res => {
        this.setData({
          userInfo: res.userInfo,
          hasUserInfo: true
        })
      }
    } else {
      // 在没有 open-type=getUserInfo 版本的兼容处理
      wx.getUserInfo({
        success: res => {
          app.globalData.userInfo = res.userInfo
          this.setData({
            userInfo: res.userInfo,
            hasUserInfo: true
          })
        }
      })
    }
  },
  onReady() {
    var page = this
    var interval = setInterval(function () {
      if (page.data.hasUserInfo && app.globalData.login) {
        clearInterval(interval)
        page.setData({
          login: app.globalData.login
        })
        setTimeout(function () {
          wx.navigateTo({
            url: '../test/test',
          })
        }, 2000)
      } else if (app.globalData.register) {
        clearInterval(interval)
        wx.navigateTo({
          url: '../register/register',
        })
      }
    }, 100)
  },
  getUserInfo(e) {
    app.globalData.userInfo = e.detail.userInfo
    this.setData({
      userInfo: e.detail.userInfo,
      hasUserInfo: true
    })
  }
})