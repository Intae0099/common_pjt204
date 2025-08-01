package com.B204.lawvatar_backend.openvidu.room.controller;

import com.B204.lawvatar_backend.common.principal.ClientPrincipal;
import com.B204.lawvatar_backend.common.principal.LawyerPrincipal;
import com.B204.lawvatar_backend.openvidu.room.dto.CreateRoomResponse;
import com.B204.lawvatar_backend.openvidu.room.dto.ParticipateRoomResponse;
import com.B204.lawvatar_backend.openvidu.room.service.RoomService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/rooms")
@RequiredArgsConstructor
public class RoomController {

    // Field
    private final RoomService roomService;

    // Method
    @PostMapping("/{appointmentId}")
    public ResponseEntity<CreateRoomResponse> createRoom(Authentication authentication, @PathVariable Long appointmentId) throws Exception {

        // Principal 객체 얻기
        Object principal = authentication.getPrincipal();

        // 유저타입을 서비스에 넘겨주면서 비즈니스 로직 시작
        String token = null;
        if(principal instanceof ClientPrincipal clientPrincipal) {
            token = roomService.createRoom(appointmentId, "CLIENT", clientPrincipal.getId());
        } else if(principal instanceof LawyerPrincipal lawyerPrincipal) {
            token = roomService.createRoom(appointmentId, "LAWYER", lawyerPrincipal.getId());
        }

        CreateRoomResponse createRoomResponse = CreateRoomResponse.builder().token(token).build();

        return ResponseEntity.status(HttpStatus.OK).body(createRoomResponse);
    }

    @PostMapping("/{appointmentId}/participants") // 특정 방에 참가자를 추가로 생성(Post요청)한다는 의미에서 요청경로 이렇게 작성
    public ResponseEntity<ParticipateRoomResponse> participateRoome(Authentication authentication, @PathVariable Long appointmentId) throws Exception {

        // Principal 객체 얻기
        Object principal = authentication.getPrincipal();

        // 유저타입을 서비스에 넘겨주면서 비즈니스 로직 시작
        String token = null;
        if(principal instanceof ClientPrincipal clientPrincipal) {
            token = roomService.participateRoom(appointmentId, "CLIENT", clientPrincipal.getId());
        } else if(principal instanceof LawyerPrincipal lawyerPrincipal) {
            token = roomService.participateRoom(appointmentId, "LAWYER", lawyerPrincipal.getId());
        }

        ParticipateRoomResponse participateRoomResponse = ParticipateRoomResponse.builder().token(token).build();

        return ResponseEntity.status(HttpStatus.OK).body(participateRoomResponse);
    }
}
