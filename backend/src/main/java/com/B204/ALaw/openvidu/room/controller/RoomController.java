package com.B204.ALaw.openvidu.room.controller;

import com.B204.ALaw.common.principal.ClientPrincipal;
import com.B204.ALaw.common.principal.LawyerPrincipal;
import com.B204.ALaw.openvidu.room.dto.CreateRoomResponse;
import com.B204.ALaw.openvidu.room.dto.LeaveRoomResponse;
import com.B204.ALaw.openvidu.room.dto.ParticipateRoomResponse;
import com.B204.ALaw.openvidu.room.dto.ShareScreenResponse;
import com.B204.ALaw.openvidu.room.service.RoomService;
import com.B204.ALaw.user.lawyer.entity.Lawyer;
import lombok.RequiredArgsConstructor;
import org.springframework.boot.autoconfigure.graphql.GraphQlProperties;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.NoSuchElementException;

@RestController
@RequestMapping("/api/rooms")
@RequiredArgsConstructor
public class RoomController {

    // Field
    private final RoomService roomService;

    // Method
    /**
     * 유저가 상담에 대한 화상상담방을 생성하기 요청을 할 때 호출되는 메서드
     * @param authentication
     * @param appointmentId
     * @return
     */
    @PostMapping("/{appointmentId}")
    public ResponseEntity<CreateRoomResponse> createRoom(Authentication authentication, @PathVariable Long appointmentId) throws Exception {

        // Principal 객체 얻기
        Object principal = authentication.getPrincipal();

        // 유저타입을 서비스에 넘겨주면서 비즈니스 로직 시작
        String openviduToken = null;
        if(principal instanceof ClientPrincipal clientPrincipal) {
            try {
                openviduToken = roomService.createRoom(appointmentId, "CLIENT", clientPrincipal.getId());
            } catch(IllegalStateException e) {
                // dto 만들고 응답
                CreateRoomResponse createRoomResponse = CreateRoomResponse.builder()
                        .success(false)
                        .message(e.getMessage())
                        .build();

                return ResponseEntity.status(HttpStatus.CONFLICT).body(createRoomResponse);
            } catch(NoSuchElementException e) {
                // dto 만들고 응답
                CreateRoomResponse createRoomResponse = CreateRoomResponse.builder()
                        .success(false)
                        .message(e.getMessage())
                        .build();

                return ResponseEntity.status(HttpStatus.NOT_FOUND).body(createRoomResponse);
            }
        } else if(principal instanceof LawyerPrincipal lawyerPrincipal) {
            try {
                openviduToken = roomService.createRoom(appointmentId, "LAWYER", lawyerPrincipal.getId());
            } catch(IllegalStateException e) {
                // dto 만들고 응답
                CreateRoomResponse createRoomResponse = CreateRoomResponse.builder()
                        .success(false)
                        .message(e.getMessage())
                        .build();

                return ResponseEntity.status(HttpStatus.CONFLICT).body(createRoomResponse);
            } catch(NoSuchElementException e) {
                // dto 만들고 응답
                CreateRoomResponse createRoomResponse = CreateRoomResponse.builder()
                        .success(false)
                        .message(e.getMessage())
                        .build();

                return ResponseEntity.status(HttpStatus.NOT_FOUND).body(createRoomResponse);
            }
        }

        CreateRoomResponse createRoomResponse = CreateRoomResponse.builder()
                .success(true)
                .message("[RoomController - 001] 화상상담방 생성 성공")
                .data(CreateRoomResponse.Data.builder().openviduToken(openviduToken).build())
                .build();

        return ResponseEntity.status(HttpStatus.OK).body(createRoomResponse);
    }

    /**
     * 유저가 화상상담방에 참여하기 요청을 할 때 호출되는 메서드
     * @param authentication
     * @param appointmentId
     * @return
     */
    @PostMapping("/{appointmentId}/participants")
    public ResponseEntity<ParticipateRoomResponse> participateRoom(Authentication authentication, @PathVariable Long appointmentId) throws Exception {

        // Principal 객체 얻기
        Object principal = authentication.getPrincipal();

        // 유저타입을 서비스에 넘겨주면서 비즈니스 로직 시작
        String openviduToken = null;
        if(principal instanceof ClientPrincipal clientPrincipal) {
            try {
                openviduToken = roomService.participateRoom(appointmentId, "CLIENT", clientPrincipal.getId());
            } catch(NoSuchElementException e) {
                // dto 만들고 응답
                ParticipateRoomResponse participateRoomResponse = ParticipateRoomResponse.builder()
                        .success(false)
                        .message(e.getMessage())
                        .build();

                return ResponseEntity.status(HttpStatus.NOT_FOUND).body(participateRoomResponse);
            } catch(IllegalStateException e) {
                // dto 만들고 응답
                ParticipateRoomResponse participateRoomResponse = ParticipateRoomResponse.builder()
                        .success(false)
                        .message(e.getMessage())
                        .build();

                return ResponseEntity.status(HttpStatus.CONFLICT).body(participateRoomResponse);
            }
        } else if(principal instanceof LawyerPrincipal lawyerPrincipal) {
            try {
                openviduToken = roomService.participateRoom(appointmentId, "LAWYER", lawyerPrincipal.getId());
            } catch(NoSuchElementException e) {
                // dto 만들고 응답
                ParticipateRoomResponse participateRoomResponse = ParticipateRoomResponse.builder()
                        .success(false)
                        .message(e.getMessage())
                        .build();

                return ResponseEntity.status(HttpStatus.NOT_FOUND).body(participateRoomResponse);
            } catch(IllegalStateException e) {
                // dto 만들고 응답
                ParticipateRoomResponse participateRoomResponse = ParticipateRoomResponse.builder()
                        .success(false)
                        .message(e.getMessage())
                        .build();

                return ResponseEntity.status(HttpStatus.CONFLICT).body(participateRoomResponse);
            }
        }

        ParticipateRoomResponse participateRoomResponse = ParticipateRoomResponse.builder()
                .success(true)
                .message("[RoomController - 002] 화상상담방 참가토큰 생성 성공")
                .data(ParticipateRoomResponse.Data.builder().openviduToken(openviduToken).build())
                .build();

        return ResponseEntity.status(HttpStatus.OK).body(participateRoomResponse);
    }

    /**
     * 사용자가 화면공유를 위한 추가토큰 얻기 요청을 할 때 사용되는 메서드
     * @param authentication
     * @param appointmentId
     * @return
     * @throws Exception
     */
    @PostMapping("/{appointmentId}/screenshare")
    public ResponseEntity<ShareScreenResponse> shareScreen(Authentication authentication, @PathVariable Long appointmentId) throws Exception {

        // Principal 객체 얻기
        Object principal = authentication.getPrincipal();

        if(principal instanceof ClientPrincipal clientPrincipal) {

            String openviduToken = null;
            try {

                openviduToken = roomService.shareScreen(appointmentId, "CLIENT", clientPrincipal.getId());

            } catch(NoSuchElementException e) {

                ShareScreenResponse shareScreenResponse = ShareScreenResponse.builder()
                        .success(false)
                        .message(e.getMessage())
                        .build();

                return ResponseEntity.status(HttpStatus.NOT_FOUND).body(shareScreenResponse);

            } catch(IllegalStateException e) {

                ShareScreenResponse shareScreenResponse = ShareScreenResponse.builder()
                        .success(false)
                        .message(e.getMessage())
                        .build();

                return ResponseEntity.status(HttpStatus.FORBIDDEN).body(shareScreenResponse);

            }

            ShareScreenResponse shareScreenResponse = ShareScreenResponse.builder()
                    .success(true)
                    .message("[RoomController - 003] 화면공유용 토큰 얻기 성공!")
                    .data(ShareScreenResponse.Data.builder().openviduToken(openviduToken).build())
                    .build();

            return ResponseEntity.status(HttpStatus.OK).body(shareScreenResponse);

        } else if(principal instanceof LawyerPrincipal lawyerPrincipal) {

            String openviduToken = null;
            try {

                openviduToken = roomService.shareScreen(appointmentId, "LAWYER", lawyerPrincipal.getId());

            } catch(NoSuchElementException e) {

                ShareScreenResponse shareScreenResponse = ShareScreenResponse.builder()
                        .success(false)
                        .message(e.getMessage())
                        .build();

                return ResponseEntity.status(HttpStatus.NOT_FOUND).body(shareScreenResponse);

            } catch(IllegalStateException e) {

                ShareScreenResponse shareScreenResponse = ShareScreenResponse.builder()
                        .success(false)
                        .message(e.getMessage())
                        .build();

                return ResponseEntity.status(HttpStatus.FORBIDDEN).body(shareScreenResponse);

            }

            ShareScreenResponse shareScreenResponse = ShareScreenResponse.builder()
                    .success(true)
                    .message("[RoomController - 004 화면공유용 토큰 얻기 성공!")
                    .data(ShareScreenResponse.Data.builder().openviduToken(openviduToken).build())
                    .build();

            return ResponseEntity.status(HttpStatus.OK).body(shareScreenResponse);

        } else {

            // 의뢰인도 아니고 변호사도 아닌 경우 403 에러 응답
            ShareScreenResponse shareScreenResponse = ShareScreenResponse.builder()
                    .success(false)
                    .message("[RoomController - 005] 유효하지 않은 사용자입니다.")
                    .build();

            return ResponseEntity.status(HttpStatus.FORBIDDEN).body(shareScreenResponse);
        }
    }

    /**
     * 유저가 화상상담방 나가기 요청을 할 때 호출되는 메서드
     * @param authentication
     * @param appointmentId
     * @return
     */
    @DeleteMapping("/{appointmentId}/participants/me")
    public ResponseEntity<LeaveRoomResponse> leaveRoom(Authentication authentication, @PathVariable Long appointmentId) throws Exception {

        // Principal 객체 얻기
        Object principal = authentication.getPrincipal();

        // 유저타입을 서비스에 넘겨주면서 비즈니스 로직 시작
        if(principal instanceof ClientPrincipal clientPrincipal) {
            try {
                roomService.leaveRoom(appointmentId, "CLIENT", clientPrincipal.getId());
            } catch(NoSuchElementException e) {
                // dto 만들고 응답
                LeaveRoomResponse leaveRoomResponse = LeaveRoomResponse.builder()
                        .success(false)
                        .message(e.getMessage())
                        .build();

                return ResponseEntity.status(HttpStatus.NOT_FOUND).body(leaveRoomResponse);
            }
        } else if(principal instanceof LawyerPrincipal lawyerPrincipal) {
            try {
                roomService.leaveRoom(appointmentId, "LAWYER", lawyerPrincipal.getId());
            } catch(NoSuchElementException e) {
                // dto 만들고 응답
                LeaveRoomResponse leaveRoomResponse = LeaveRoomResponse.builder()
                        .success(false)
                        .message(e.getMessage())
                        .build();

                return ResponseEntity.status(HttpStatus.NOT_FOUND).body(leaveRoomResponse);
            }
        }

        LeaveRoomResponse leaveRoomResponse = LeaveRoomResponse.builder()
                .success(true)
                .message("[RoomController - 006] 화상상담방 나가기 성공")
                .build();

        return ResponseEntity.status(HttpStatus.OK).body(leaveRoomResponse);
    }
}
