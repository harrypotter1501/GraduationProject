// pages/test.js

const app = getApp()
import { formatTime } from '../../utils/util.js'
import { ImgQueue } from '../../utils/imgQueue.js'

Page({
  data: {
    datetime: '',
    imgSrc: '',
    imgInter: null,
    imgBufSize: 8,
    imgBuf: null,
    refreshPeriod: 200
  },
  onLoad () {
    return
    this.data.imgBuf = new ImgQueue(this.data.imgBufSize * 2)
    for (var i = 0; i < this.data.imgBufSize; ++i) {
      this.imgDownload()
    }
    var page = this
    this.data.imgInter = setInterval( () => {
      page.setData({
        datetime: formatTime(new Date())
      })
      page.imgDownload()
        page.setData({
          imgSrc: page.data.imgBuf.pop()
        })
    }, this.data.refreshPeriod)
  },
  onHide () {
    clearInterval(this.data.imgInter)
  },
  onUnload () {
    clearInterval(this.data.imgInter)
  },
  windowTap () {
    wx.downloadFile({
      url: app.globalData.server + '/stream?' + Date.now(),
      header: {
        cookie: app.globalData.cookie
      },
      success: res => {
        console.log(res)
        app.globalData.cookie = res.cookies[0]
        if (res.statusCode === 200) {
          this.setData({
            imgSrc: res.tempFilePath
          })
        }
      },
      fail: res => {
        console.error(res.errMsg)
      }
    })
    return
    wx.request({
      url: app.globalData.server + '/stream',
      header: {
        cookie: app.globalData.cookie
      },
      success: res => {
        //
      }
    })
  },
  imgDownload () {
    if (!this.data.imgBuf.isFull()) {
      var page = this
      wx.downloadFile({
        url: app.globalData.server + '/stream?' + Date.now(),
        header: {
          cookie: app.globalData.cookie
        },
        success: res => {
          if (res.statusCode === 200) {
            page.data.imgBuf.push(res.tempFilePath)
          }
        },
        fail: res => {
          console.error(res.errMsg)
        },
        timeout: page.data.refreshPeriod * page.data.imgBufSize
      })
    }
  }
})