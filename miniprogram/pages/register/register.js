// pages/register.js

const app = getApp()

Page({
  bindFormSubmit(e) {
    var form = e.detail.value
    wx.request({
      url: app.globalData.server + '/login/register',
      method: 'POST',
      header: {
        'content-type': 'application/x-www-form-urlencoded',
        cookie: app.globalData.cookie
      },
      data: {
        device_id: form.device_id,
        device_key: form.device_key
      },
      success: res => {
        console.log(res)
        if (res.data === 'OK') {
          app.globalData.register = false
          app.login()
          wx.redirectTo({
            url: '../index/index',
          })
        }
      }
    })
  }
})