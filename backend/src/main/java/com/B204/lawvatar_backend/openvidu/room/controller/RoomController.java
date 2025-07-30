package com.B204.lawvatar_backend.openvidu.room.controller;

import com.B204.lawvatar_backend.openvidu.room.dto.CreateRoomResponse;
import com.B204.lawvatar_backend.openvidu.room.dto.GetRoomListResponse;
import com.B204.lawvatar_backend.openvidu.room.dto.ParticipateRoomResponse;
import com.B204.lawvatar_backend.openvidu.room.entity.Room;
import com.B204.lawvatar_backend.openvidu.room.service.RoomService;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/rooms")
@RequiredArgsConstructor
public class RoomController {

    // Field
    private final RoomService roomService;

    // Method
    @PostMapping("/create")
    public ResponseEntity<CreateRoomResponse> createClientRoom(HttpServletRequest servletRequest) throws Exception {

        Map<String, Object> result = roomService.createRoom();

        CreateRoomResponse createRoomResponse = new CreateRoomResponse((Long)result.get("roomId"), (String)result.get("customSessionId"), (String)result.get("token"));

        return ResponseEntity.status(HttpStatus.OK).body(createRoomResponse);
    }

    @PostMapping("/{customSessionId}/participants") // 특정 방에 참가자를 추가로 생성(Post요청)한다는 의미에서 요청경로 이렇게 작성
    public ResponseEntity<ParticipateRoomResponse> participateClientRoom(@PathVariable String customSessionId, HttpServletRequest servletRequest) throws Exception {

        Map<String, Object> result = roomService.participateRoom(customSessionId);

        ParticipateRoomResponse participateRoomResponse = new ParticipateRoomResponse((Long)result.get("roomId"), (String)result.get("token"));

        return ResponseEntity.status(HttpStatus.OK).body(participateRoomResponse);
    }

    @GetMapping("/list")
    public ResponseEntity<GetRoomListResponse> getRoomList() {

        List<Room> roomList = roomService.getRoomList();

        GetRoomListResponse getRoomListResponse = new GetRoomListResponse(roomList);

        return ResponseEntity.status(HttpStatus.OK).body(getRoomListResponse);
    }
}
