// pages/test.js

const app = getApp()
import { formatTime } from '../../utils/util.js'
import { ImgQueue } from '../../utils/imgQueue.js'

Page({
  data: {
    datetime: '',
    imgSrc: '',
    imgInter: null,
    alive: false,
    imgBufSize: 8,
    imgBuf: null,
    refreshPeriod: 1000,
    button: 'Start'
  },
  onLoad () {
    this.data.imgBuf = new ImgQueue(this.data.imgBufSize * 2)
    for (var i = 0; i < this.data.imgBufSize; ++i) {
      this.imgDownload()
    }
    var page = this
    this.data.imgInter = setInterval( () => {
      page.setData({
        datetime: formatTime(new Date())
      })
      if (this.data.alive) {
        page.imgDownload()
        page.setData({
          imgSrc: page.data.imgBuf.pop()
        })
      }
    }, this.data.refreshPeriod)
  },
  onHide () {
    clearInterval(this.data.imgInter)
  },
  onUnload () {
    clearInterval(this.data.imgInter)
  },
  refresh (e) {
    var alv = this.data.alive
    var btn = this.data.button
    if (btn == 'Start') {
      btn = 'Stop'
    } else {
      btn = 'Start'
    }
    this.setData({
      alive: !alv,
      button: btn
    })
    return
    wx.downloadFile({
      url: app.globalData.server + '/stream?' + Date.now(),
      header: {
        cookie: app.globalData.cookie
      },
      success: (res) => {
        //app.globalData.cookie = res.cookies[0]
        if (res.statusCode === 200) {
          console.log(res)
          this.setData({
            imgSrc: res.tempFilePath
          })
        }
      },
      fail: (res) => {
        console.error(res.errMsg)
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
        success: (res) => {
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