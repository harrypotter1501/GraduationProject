const ImgQueue = function (capacity = 5) {
  this.capacity = capacity
  this.data = new Array(capacity)
  this.frontIdx = 0
  this.backIdx = 0
  this.full = false

  this.size = function () {
    return this.size
  }

  this.isFull = function () {
    return (this.backIdx === this.frontIdx) ? this.full : false;
  }

  this.isEmpty = function () {
    return (this.backIdx === this.frontIdx) ? (!this.full) : false;
  }

  this.clear = function () {
    this.data = []
    this.frontIdx = 0
    this.backIdx = 0
    this.full = false
  }

  this.setCapacity = function (newCap) {
    this.capacity = newCap
    this.data = Array(newCap)
  }

  this.front = function () {
    return this.isEmpty() ? null : this.data[this.frontIdx]
  }

  this.push = function (item) {
    if (this.full) {
      throw 'ImgQueue overflow'
    }
    this.data[this.backIdx++] = item
    this.backIdx = (this.backIdx < this.capacity) ? this.backIdx : 0
    if (this.backIdx === this.frontIdx) {
      this.full = true
    } else {
      this.full = false
    }
  }

  this.pop = function () {
    if (this.isEmpty()) {
      throw 'ImgQueue underflow'
    }
    var res = this.data[this.frontIdx++]
    this.frontIdx = (this.frontIdx < this.capacity) ? this.frontIdx : 0
    this.full = false
    return res
  }
}

module.exports = {
  ImgQueue
}