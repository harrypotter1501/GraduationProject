// pages/test.js

const app = getApp()
import { formatTime } from '../../utils/util.js'
import { ImgQueue } from '../../utils/imgQueue.js'

Page({
  data: {
    datetime: '2021/1/1 00:00:00',
    temp: 0,
    humid: 0,
    modeIdx: 0,
    frameIdx: 0,

    imgSrc: '../../images/temp/demo.jpg',
    imgInter: null,
    initInter: null,
    alive: false,
    imgBufSize: 5,
    imgBuf: null,
    refreshPeriod: 500,
    button: 'Start',

    modeArray: ['QVGA', 'VGA', 'SVGA', 'SGA'],
    modeItems: ['QVGA', 'VGA', 'SVGA', 'SGA'],
    frameArray: ['Low', 'Medium', 'High'],
    frameItems: ['LOW', 'MEDIUM', 'HIGH'],

    retry: true,
  },
  onLoad () {
    //return
    var page = this
    this.data.initInter = setInterval( () => {
      if (page.data.retry) {
        page.data.retry = false
        page.checkDevice()
      }
    }, 1000)
  },
  onHide () {
    clearInterval(this.data.imgInter)
  },
  onUnload () {
    clearInterval(this.data.imgInter)
    clearInterval(this.data.initInter)
  },
  pickerModeChange(e) {
    this.setData({
      modeIdx: e.detail.value
    })
  },
  pickerFrameChange(e) {
    this.setData({
      frameIdx: e.detail.value
    })
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
    wx.request({
      url: app.globalData.server + '/stream/command',
      method: 'POST',
      header: {
        'content-type': 'application/x-www-form-urlencoded',
        cookie: app.globalData.cookie
      },
      data: {
        DHT: true,
        CAM: this.data.alive,
        MODE: this.data.modeItems[this.data.modeIdx],
        FRAME: this.data.frameItems[this.data.frameIdx],
      },
      complete: (res) => {
        console.log(res)
        app.globalData.requestCompleteCallback(res)
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
        complete: (res) => {
          app.globalData.requestCompleteCallback(res)
        },
        timeout: page.data.refreshPeriod * page.data.imgBufSize
      })
    }
  },
  getSensors () {
    wx.request({
      url: app.globalData.server + '/stream/sensors',
      header: {
        cookie: app.globalData.cookie
      },
      success: (res) => {
        console.log(res)
      },
      fail: (res) => {
        console.error(res)
      },
      complete: (res) => {
        app.globalData.requestCompleteCallback(res)
      }
    })
  },
  checkDevice () {
    wx.showLoading({
      title: 'Searching...',
    })
    wx.request({
      url: app.globalData.server + '/stream/alive',
      header: {
        cookie: app.globalData.cookie
      },
      success: (res) => {
        wx.hideLoading()
        if (res.data == 'OK') {
          console.log(res)
          wx.hideLoading()
          this.loadPage()
        } else {
          wx.showModal({
            title: 'No device connected!',
            confirmText: 'Retry',
            cancelText: 'Cancel',
            success: (res) => {
              if (res.confirm) {
                this.data.retry = true
              } else {
                clearInterval(this.data.initInter)
                wx.navigateBack({
                  delta: 1,
                })
              }
            }
          })
          console.error(res)
        }
      },
      fail: (res) => {
        console.error(res)
      },
      complete: (res) => {
        app.globalData.requestCompleteCallback(res)
      }
    })
  },
  loadPage () {
    this.getSensors()
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
  }
})
