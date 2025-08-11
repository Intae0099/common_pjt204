package com.B204.ALaw.openvidu.room.service;

import com.B204.ALaw.appointment.entity.Appointment;
import com.B204.ALaw.appointment.entity.AppointmentStatus;
import com.B204.ALaw.appointment.repository.AppointmentRepository;
import com.B204.ALaw.openvidu.participant.entity.Participant;
import com.B204.ALaw.openvidu.participant.repository.ParticipantRepository;
import com.B204.ALaw.openvidu.room.dto.OpenViduConnectionResponse;
import com.B204.ALaw.openvidu.room.dto.OpenViduSessionResponse;
import com.B204.ALaw.openvidu.room.entity.Room;
import com.B204.ALaw.openvidu.room.repository.RoomRepository;
import com.B204.ALaw.openvidu.session.entity.Session;
import com.B204.ALaw.openvidu.session.repository.SessionRepository;
import com.B204.ALaw.user.client.entity.Client;
import com.B204.ALaw.user.client.repository.ClientRepository;
import com.B204.ALaw.user.lawyer.entity.Lawyer;
import com.B204.ALaw.user.lawyer.repository.LawyerRepository;
import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.RestTemplate;

import java.nio.charset.StandardCharsets;
import java.util.Base64;
import java.util.Map;
import java.util.NoSuchElementException;

@Service
@RequiredArgsConstructor
@Transactional
public class RoomService {

    // Field
    private static final String MY_OPENVIDU_SERVER_URL = "https://i13b204.p.ssafy.io";
    private static final String OPENVIDU_SECRET_KEY = "ssafy204openvidulawaid";

    private final RoomRepository roomRepository;
    private final AppointmentRepository appointmentRepository;
    private final ParticipantRepository participantRepository;
    private final SessionRepository sessionRepository;
    private final ClientRepository clientRepository;
    private final LawyerRepository lawyerRepository;

    private final RestTemplate restTemplate;

    // Method
    public String createRoom(Long appointmentId, String userType, Long userId) throws Exception{

        // 이 appointmentId에 대해 이미 생성돼있는 화상상담방이 있으면 에러 응답
        Session existingSession = sessionRepository.findByAppointmentId(appointmentId).orElse(null);
        if(existingSession != null) {
            throw new IllegalStateException("[RoomService - 002] 이미 화상상담방이 존재하는 상담입니다.");
        }

        // customSessionId 만들기
        String openviduCustomSessionId = Room.generateCustomSessionId();

        // 생성한 customSessionId 들고 sessionId 얻으러 가기
        String openviduSessionId = getSessionId(openviduCustomSessionId);

        // openvidu 관련 데이터들 가지고 Room 객체 생성해서 DB에 저장하기
        Room room = Room.builder().openviduCustomSessionId(openviduCustomSessionId).openviduSessionId(openviduSessionId).build();
        roomRepository.save(room);

        // sessionId 들고 connections 가서 토큰 얻어오기
        String openviduToken = getToken(openviduSessionId);

        // participant 테이블에 참가정보 저장하기
        // 유저타입에 따라 Participant 객체 만들어서 DB에 저장
        if(userType.equals("CLIENT")) {
            Client client = clientRepository.findById(userId).orElseThrow(() -> new NoSuchElementException("[RoomService - 003] 해당 ID 값을 가지는 Client가 없습니다."));

            if(participantRepository.findByClient(client) != null) {
                throw new IllegalStateException("[RoomService - 004] 이미 화상상담방에 참가중인 사용자입니다. 참가 중인 화상상담방에서 나온 후에 다시 요청해주세요.");
            }

            Participant participant = Participant.builder().client(client).room(room).build();
            participantRepository.save(participant);
        } else if(userType.equals("LAWYER")) {
            Lawyer lawyer = lawyerRepository.findById(userId).orElseThrow(() -> new NoSuchElementException("[RoomService - 005] 해당 ID 값을 가지는 Lawyer가 없습니다."));

            if(participantRepository.findByLawyer(lawyer) != null) {
                throw new IllegalStateException("[RoomService - 006] 이미 화상상담방에 참가중인 사용자입니다. 참가 중인 화상상담방에서 나온 후에 다시 요청해주세요.");
            }

            Participant participant = Participant.builder().lawyer(lawyer).room(room).build();
            participantRepository.save(participant);
        }

        // session 테이블에 세션정보 저장하기
        Appointment appointment = appointmentRepository.findById(appointmentId).orElseThrow(() -> new NoSuchElementException("[RoomService - 007] 해당 ID 값을 가지는 Appointment가 없습니다."));
        Session session = Session.builder().appointment(appointment).room(room).participantCount(1).build();
        sessionRepository.save(session);
        
        // appointment 테이블에서 appointment_status 'IN_PROGRESS'로 변경
        appointment.setAppointmentStatus(AppointmentStatus.IN_PROGRESS);

        return openviduToken;
    }

    public String participateRoom(Long appointmentId, String userType, Long userId) {

        // 이 Appointment 객체에 대한 Session 객체와 Room 객체 얻기
        Session session = sessionRepository.findByAppointmentId(appointmentId).orElseThrow(() -> new NoSuchElementException("[RoomService - 008] 화상상담방이 열려있지 않은 상담입니다."));

        Room room = session.getRoom();

        // Participant 테이블에 참가정보 저장하기
        // 유저타입에 따라 Participant 객체 만들어서 DB에 저장
        if(userType.equals("CLIENT")) {
            Client client = clientRepository.findById(userId).orElseThrow(() -> new NoSuchElementException("[RoomService - 010] 해당 ID 값을 가지는 Client가 없습니다."));
            
            // 여기서 다른방에 참여중인거 아닌지 검사
            // 요청한 사람이 이미 화상상담방에 참여중인 사람인지 participant 테이블 조회해서 찾기
            // 결과물이 null이 아니면 IllegalStateException 발생시키기
            if(participantRepository.findByClient(client) != null) {
                throw new IllegalStateException("[RoomService - 011] 이미 화상상담방에 참여중인 사용자입니다.");
            }

            // 이제 다시 room 기준으로 particicpant 테이블 조회하기
            Participant participant = participantRepository.findByRoom(room);

            // 얻은 Participant 객체의 client 자리에 client 넣기
            participant.setClient(client);

            // 더티체킹
        } else if(userType.equals("LAWYER")) {
            Lawyer lawyer = lawyerRepository.findById(userId).orElseThrow(() -> new NoSuchElementException("[RoomService - 012] 해당 ID 값을 가지는 Lawyer가 없습니다."));

            if(participantRepository.findByLawyer(lawyer) != null) {
                throw new IllegalStateException("[RoomService - 013] 이미 화상상담방에 참여중인 사용자입니다.");
            }

            Participant participant = participantRepository.findByRoom(room);
            participant.setLawyer(lawyer);
        }

        // Session 객체 참가자 수 올리기
        // 더티체킹 되기 때문에 따로 저장할 필요는 없음
        session.setParticipantCount(session.getParticipantCount()+1);

        // sessionId는 방금 찾아온 Room 객체에서 가져오기
        String openviduSessionId = room.getOpenviduSessionId();

        // sessionId 들고 토큰 받으러 가기
        String openviduToken = getToken(openviduSessionId);

        return openviduToken;
    }

    public String shareScreen(Long appointmentId, String userType, Long userId) {

        // Appointment 객체 얻기
        // 존재하지 않는 appointmentId를 준 경우, 여기서 에러터짐
        Appointment appointment = appointmentRepository.findById(appointmentId).orElseThrow(() -> new NoSuchElementException("[RoomService - 014] 해당 ID 값을 가지는 Appointment가 없습니다."));

        // appointmentId 기준으로 세션객체를 찾고 거기서 Room 객체 얻기
        // 화상상담방이 존재하지 않는 상담의 appointmentId를 준 경우 여기서 에러터짐
        Session session = sessionRepository.findByAppointmentId(appointmentId).orElseThrow(() -> new NoSuchElementException("[RoomService - 015] 화상상담방이 열려있지 않은 상담입니다."));
        Room room = session.getRoom();

        if(userType.equals("CLIENT")) {

            Participant participant = participantRepository.findByClientId(userId);

            if(participant == null) {
                throw new NoSuchElementException("[RoomService - 016] 화상상담방에 참여 중이지 않은 사용자입니다.");
            } else if(!participant.getRoom().getId().equals(room.getId())) {
                throw new IllegalStateException("[RoomService - 017] 자신이 참여 중인 화상상담방에 대해서만 화면공유용 토큰을 받을 수 있습니다.");
            }

        } else if(userType.equals("LAWYER")) {

            Participant participant = participantRepository.findByLawyerId(userId);

            if(participant == null) {
                throw new NoSuchElementException("[RoomService - 018] 화상상담방에 참여 중이지 않은 사용자입니다.");
            } else if(!participant.getRoom().getId().equals(room.getId())) {
                throw new IllegalStateException("[RoomService - 019] 자신이 참여 중인 화상상담방에 대해서만 화면공유용 토큰을 받을 수 있습니다.");
            }

        } else {
            throw new IllegalStateException("[RoomService - 020] 알 수 없는 에러가 발생했습니다. 관리자에게 문의하세요.");
        }

        // 그 Room 객체의 sessionId를 받기
        String sessionId = room.getOpenviduSessionId();

        // 그 sessionId를 가지고 getToken 가서 토큰 받아서 리턴
        return getToken(sessionId);
    }

    public void leaveRoom(Long appointmentId, String userType, Long userId) throws Exception{

        // appointmentId 기준으로 세션 객체 얻기
        Session session = sessionRepository.findByAppointmentId(appointmentId).orElseThrow(() -> new NoSuchElementException("[RoomService - 021] 화상상담방이 열려있지 않은 상담입니다."));

        // 세션에서 나간다면 남는 인원수
        int participantCount = session.getParticipantCount() - 1;

        // userType이 CLIENT일 때와 LAWYER일 때를 분기처리
        if(userType.equals("CLIENT")) {
            // 남는 인원수가 1명 이상일 때와 0명일 때를 분기처리
            // 1명 이상일 때는 참가 인원수 -1 하고, 참가정보(Participant)만 삭제하면 됨
            if(participantCount >= 1) {
                // 해당 세션 참가자수 -1
                session.setParticipantCount(participantCount);

                // 이 의뢰인의 참가정보 삭제
                Participant participant = participantRepository.findByClientId(userId);
                participant.setClient(null);

            } else if(participantCount == 0) { // 0명일 때는 세션정보(Session)와 openvidu 관련정보(Room)도 삭제해야 함

                // 이 화상상담방의 openvidu 관련정보 삭제
                Room room = sessionRepository.findByAppointmentId(appointmentId).orElseThrow(() -> new NoSuchElementException("[RoomService - 022] 화상상담방이 열려있지 않은 상담입니다.")).getRoom();
                room.setSession(null);
                room.getParticipantList().clear();
                roomRepository.saveAndFlush(room);
                roomRepository.delete(room);

                // appointment 테이블에서 appointment_status 'ENDED'로 변경
                Appointment appointment = appointmentRepository.findById(appointmentId).orElseThrow(() -> new NoSuchElementException("[RoomService - 023] 해당 ID 값을 가지는 Appointment가 없습니다."));
                appointment.setAppointmentStatus(AppointmentStatus.ENDED);

            }
        } else if(userType.equals("LAWYER")) { // userType이 LAWYER 일 때도 똑같이 반복

            if(participantCount >= 1) {

                session.setParticipantCount(participantCount);
                Participant participant = participantRepository.findByLawyerId(userId);
                participant.setLawyer(null);

            } else if(participantCount == 0) {

                Room room = sessionRepository.findByAppointmentId(appointmentId).orElseThrow(() -> new NoSuchElementException("[RoomService - 024] 화상상담방이 열려있지 않은 상담입니다.")).getRoom();
                room.setSession(null);
                room.getParticipantList().clear();
                roomRepository.saveAndFlush(room);
                roomRepository.delete(room);

                Appointment appointment = appointmentRepository.findById(appointmentId).orElseThrow(() -> new NoSuchElementException("[RoomService - 025] 해당 ID 값을 가지는 Appointment가 없습니다."));
                appointment.setAppointmentStatus(AppointmentStatus.ENDED);
            }
        }
    }

    public HttpStatusCode removeRoom(Long appointmentId) {

        // 화상상담방을 강제종료시키고 싶은 Appointment 객체 얻기
        Appointment appointment = appointmentRepository.findById(appointmentId).orElseThrow(() -> new NoSuchElementException("[RoomService - 026] 해당 ID 값을 가지는 Appointment가 없습니다."));

        // 이 Appointment에 해당하는 Session 객체 얻기
        Session session = sessionRepository.findByAppointmentId(appointmentId).orElseThrow(() -> new NoSuchElementException("[RoomService - 027] 화상상담방이 열려있지 않은 상담입니다."));

        // 이 Appointment에 대해 활성화된 세션이 없다면, 404 NotFound 에러 응답
        if(session == null) {
            throw new NoSuchElementException("[RoomService - 028] 해당 상담은 화상상담방이 열려있지 않습니다.");
        }

        // 이 Session이 참조중인 Room 객체 얻어내고 Session 데이터 DB에서 삭제하기
        Room room = session.getRoom();
        sessionRepository.delete(session);

        // sessionId 알아내고 Room 데이터도 DB에서 삭제하기
        String openviduSessionId = room.getOpenviduSessionId();

        // openVidu 서버에 강제종료 요청보내기
        String url = MY_OPENVIDU_SERVER_URL + "/openvidu/api/sessions/" + openviduSessionId;

        HttpHeaders headers = createHeaders();
        HttpEntity<Void> httpEntity = new HttpEntity<>(headers);

        try {
            ResponseEntity<Void> httpResponse = restTemplate.exchange(
                    url,
                    HttpMethod.DELETE,
                    httpEntity,
                    Void.class
            );

            return httpResponse.getStatusCode();

        } catch(HttpClientErrorException e) {
            return e.getStatusCode();
        }
    }

    private HttpHeaders createHeaders() {
        String auth = "OPENVIDUAPP:" + OPENVIDU_SECRET_KEY;
        String encodedAuth = Base64.getEncoder().encodeToString(auth.getBytes(StandardCharsets.UTF_8));
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.add("Authorization", "Basic " + encodedAuth);
        return headers;
    }

    private String getSessionId(String openviduCustomSessionId) {

        // customSessionId 들고 sessions 가서 openvidu 내부 sessionId 얻어오기
        String url = MY_OPENVIDU_SERVER_URL + "/openvidu/api/sessions";

        HttpHeaders headers = createHeaders();
        Map<String, String> body = Map.of("customSessionId", openviduCustomSessionId);

        HttpEntity<Map<String, String>> httpEntity = new HttpEntity<>(body, headers);

        ResponseEntity<OpenViduSessionResponse> openviduSessionResponse = restTemplate.postForEntity(url, httpEntity, OpenViduSessionResponse.class);

        return openviduSessionResponse.getBody().getId();
    }

    private String getToken(String openviduSessionId) {

        // sessionId 들고 sessions/{sessionId}/connections가서 토큰얻어오기
        String url = MY_OPENVIDU_SERVER_URL + "/openvidu/api/sessions/" + openviduSessionId + "/connection";

        HttpHeaders headers = createHeaders();

        Map<String, String> body = Map.of("role", "MODERATOR");

        HttpEntity<Map<String, String>> httpEntity = new HttpEntity<>(body, headers);

        ResponseEntity<OpenViduConnectionResponse> openviduConnectionResponse = restTemplate.postForEntity(url, httpEntity, OpenViduConnectionResponse.class);

        return openviduConnectionResponse.getBody().getToken(); // 토큰을 리턴해야함
    }
}
