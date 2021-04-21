
function Queue(capacity = 5) {
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

class ImgQueue {
    capacity = 5
    data = []
    frontIdx = 0
    backIdx = 0
    full = false

    constructor(capacity) {
        this.capacity = capacity
        this.data = new Array(capacity)
    }

    size() {
        return (this.backIdx - this.frontIdx + this.capacity) % this.capacity
    }

    isFull() {
        return (this.backIdx === this.frontIdx) ? this.full : false
    }

    isEmpty() {
        return (this.backIdx === this.frontIdx) ? (!this.full) : false
    }

    clear() {
        this.data = []
        this.frontIdx = 0
        this.backIdx = 0
        this.full = false
    }

    setCapacity(newCap) {
        this.capacity = newCap
        this.data = Array(newCap)
    }

    front() {
        return this.isEmpty() ? null : this.data[this.frontIdx]
    }

    push(item) {
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

    pop() {
        if (this.isEmpty()) {
            throw 'ImgQueue underflow'
        }
        var res = this.data[this.frontIdx++]
        this.frontIdx = (this.frontIdx < this.capacity) ? this.frontIdx : 0
        this.full = false
        return res
    }
}

var q = new Queue(3)
for (var i = 0; i < 3; ++i) {
    q.push(i)
}
for (var i = 0; i < 2; ++i) {
    console.log(q.pop())
}
for (var i = 3; i < 5; ++i) {
    q.push(i)
}
for (var i = 0; i < 3; ++i) {
    console.log(q.pop())
}
