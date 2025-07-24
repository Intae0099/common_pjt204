// server.js
const express = require('express')
const http = require('http')
const { Server } = require('socket.io')
const cors = require('cors')

const app = express()
app.use(cors())

const server = http.createServer(app)
const io = new Server(server, {
  cors: {
    origin: '*', // 모든 출처 허용 (개발용)
    methods: ['GET', 'POST']
  }
})

// 연결 이벤트
io.on('connection', (socket) => {
  console.log('클라이언트 접속:', socket.id)

  socket.on('join', (roomId) => {
    socket.join(roomId)
    console.log(`${socket.id} joined room: ${roomId}`)

    // 방에 2명이 되면 signaling 시작
    const clients = Array.from(io.sockets.adapter.rooms.get(roomId) || [])
    if (clients.length > 1) {
      // offer를 보내라고 지시
      io.to(clients[0]).emit('joined')
    }
  })

  // offer 전달
  socket.on('offer', ({ roomId, offer }) => {
    socket.to(roomId).emit('offer', { offer })
  })

  // answer 전달
  socket.on('answer', ({ roomId, answer }) => {
    socket.to(roomId).emit('answer', { answer })
  })

  // ice-candidate 전달
  socket.on('ice-candidate', ({ roomId, candidate }) => {
    socket.to(roomId).emit('ice-candidate', { candidate })
  })

  socket.on('disconnect', () => {
    console.log('연결 종료:', socket.id)
  })
})

server.listen(3000, () => {
  console.log('signaling server on http://localhost:3000')
})
