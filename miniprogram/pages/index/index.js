// index.js
// 获取应用实例
const app = getApp()

Page({
  data: {
    motto: 'Hello World!',
    userInfo: {},
    hasUserInfo: false,
    canIUseGetUserProfile: false,
    login: false
  },
  // 事件处理函数
  bindViewTap() {
    wx.navigateTo({
      url: '../logs/logs'
    })
  },
  bindTextTap() {
    wx.navigateTo({
      url: '../stream/stream',
    })
  },
  onLoad() {
    if (wx.getUserProfile) {
      this.setData({
        canIUseGetUserProfile: true
      })
    }
  },
  onReady() {
    // wx.redirectTo({
    //   url: '../stream/stream',
    // })
    // return
    var page = this
    var interval = setInterval(() => {
      if (page.data.hasUserInfo && app.globalData.login) {//(app.globalData.login) {//
        clearInterval(interval)
        page.setData({
          login: app.globalData.login
        })
        setTimeout(() => {
          wx.navigateTo({
            url: '../stream/stream',
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
  getUserProfile(e) {
    // 推荐使用wx.getUserProfile获取用户信息，开发者每次通过该接口获取用户个人信息均需用户确认
    // 开发者妥善保管用户快速填写的头像昵称，避免重复弹窗
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
  getUserInfo(e) {
    // 不推荐使用getUserInfo获取用户信息，预计自2021年4月13日起，getUserInfo将不再弹出弹窗，并直接返回匿名的用户个人信息
    this.setData({
      userInfo: e.detail.userInfo,
      hasUserInfo: true
    })
  },
})