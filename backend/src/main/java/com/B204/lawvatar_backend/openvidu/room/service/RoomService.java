package com.B204.lawvatar_backend.openvidu.room.service;

import com.B204.lawvatar_backend.appointment.entity.Appointment;
import com.B204.lawvatar_backend.appointment.repository.AppointmentRepository;
import com.B204.lawvatar_backend.openvidu.participant.entity.Participant;
import com.B204.lawvatar_backend.openvidu.participant.repository.ParticipantRepository;
import com.B204.lawvatar_backend.openvidu.room.dto.OpenViduConnectionResponse;
import com.B204.lawvatar_backend.openvidu.room.dto.OpenViduSessionResponse;
import com.B204.lawvatar_backend.openvidu.room.entity.Room;
import com.B204.lawvatar_backend.openvidu.room.repository.RoomRepository;
import com.B204.lawvatar_backend.openvidu.session.entity.Session;
import com.B204.lawvatar_backend.openvidu.session.repository.SessionRepository;
import com.B204.lawvatar_backend.user.client.entity.Client;
import com.B204.lawvatar_backend.user.client.repository.ClientRepository;
import com.B204.lawvatar_backend.user.lawyer.entity.Lawyer;
import com.B204.lawvatar_backend.user.lawyer.repository.LawyerRepository;
import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import org.springframework.boot.autoconfigure.graphql.GraphQlProperties;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.server.ResponseStatusException;

import java.nio.charset.StandardCharsets;
import java.util.Base64;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

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
    public String createRoom(Long appointmentId, String userType, Long userId) {

        String openviduCustomSessionId = Room.generateCustomSessionId();

        // 생성한 customSessionId 들고 sessionId 얻으러 가기
        String openviduSessionId = getSessionId(openviduCustomSessionId);

        /// ///////////////////////////////////////////////////////
        System.out.println("sessionId 획득 성공! " + openviduSessionId);
        /// ///////////////////////////////////////////////////////

        // openvidu 관련 데이터들 가지고 Room 객체 생성해서 DB에 저장하기
        Room room = Room.builder().openviduCustomSessionId(openviduCustomSessionId).openviduSessionId(openviduSessionId).build();
        roomRepository.save(room);

        // sessionId 들고 connections 가서 토큰 얻어오기
        String openviduToken = getToken(openviduSessionId);

        /// ///////////////////////////////////////////////////////
        System.out.println("token 획득 성공! " + openviduToken);
        /// ///////////////////////////////////////////////////////

        // Participant 테이블에 참가정보 저장하기
        // 유저타입에 따라 Participant 객체 만들어서 DB에 저장
        if(userType.equals("CLIENT")) {
            Client client = clientRepository.findById(userId).orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "[RoomService - 001] 해당 ID 값을 가지는 Client가 없습니다."));
            Participant participant = Participant.builder().client(client).room(room).build();
            participantRepository.save(participant);
        } else if(userType.equals("LAWYER")) {
            Lawyer lawyer = lawyerRepository.findById(userId).orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "[RoomService - 002] 해당 ID 값을 가지는 Lawyer가 없습니다."));
            Participant participant = Participant.builder().lawyer(lawyer).room(room).build();
            participantRepository.save(participant);
        }

        // Session 테이블에 세션정보 저장하기
        Appointment appointment = appointmentRepository.findById(appointmentId).orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "[RoomService - 003] 해당 ID 값을 가지는 Appointment가 없습니다."));
        Session session = Session.builder().appointment(appointment).room(room).participantCount(1).build();
        sessionRepository.save(session);

        return openviduToken;
    }

    public String participateRoom(Long appointmentId, String userType, Long userId) {

        // 이 Appointment 객체에 대한 Session 객체와 Room 객체 얻기
        Session session = sessionRepository.findByAppointmentId(appointmentId);
        Room room = session.getRoom();

        // Participant 테이블에 참가정보 저장하기
        // 유저타입에 따라 Participant 객체 만들어서 DB에 저장
        if(userType.equals("CLIENT")) {
            Client client = clientRepository.findById(userId).orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "[RoomService - 004] 해당 ID 값을 가지는 Client가 없습니다."));
            Participant participant = Participant.builder().client(client).room(room).build();
            participantRepository.save(participant);
        } else if(userType.equals("LAWYER")) {
            Lawyer lawyer = lawyerRepository.findById(userId).orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "[RoomService - 005] 해당 ID 값을 가지는 Lawyer가 없습니다."));
            Participant participant = Participant.builder().lawyer(lawyer).room(room).build();
            participantRepository.save(participant);
        }

        // Session 객체 참가자 수 올리기
        // 더티체킹 되기 때문에 따로 저장할 필요는 없음
        session.setParticipantCount(session.getParticipantCount()+1);

        // sessionId는 방금 찾아온 Room 객체에서 가져오기
        String openviduSessionId = room.getOpenviduSessionId();

        // sessionId 들고 토큰 받으러 가기
        String openviduToken = getToken(openviduSessionId);

        /// ///////////////////////////////////////////////////////
        System.out.println("token 획득 성공! " + openviduToken);
        /// ///////////////////////////////////////////////////////

        return openviduToken;
    }

    public void leaveRoom(Long appointmentId, String userType, Long userId) {

        // appointmentId 기준으로 세션 객체 얻기
        Session session = sessionRepository.findByAppointmentId(appointmentId);

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
                participantRepository.deleteByClientId(userId);

            } else if(participantCount == 0) { // 0명일 때는 세션정보(Session)와 openvidu 관련정보(Room)도 삭제해야 함

                // 이 화상상담방의 openvidu 관련정보 삭제해야 해서 해당하는 Room 객체 얻어놓기
                Room room = sessionRepository.findByAppointmentId(appointmentId).getRoom();

                // 해당 세션을 삭제
                sessionRepository.delete(session);

                // 이 의뢰인의 참가정보 삭제
                participantRepository.deleteByClientId(userId);

                // 이 화상상담방의 openvidu 관련정보 삭제
                roomRepository.delete(room);

            }
        } else if(userType.equals("LAWYER")) { // userType이 LAWYER 일 때도 똑같이 반복ㅠ

            if(participantCount >= 1) {

                session.setParticipantCount(participantCount);
                participantRepository.deleteByLawyerId(userId);

            } else if(participantCount == 0) {

                Room room = sessionRepository.findByAppointmentId(appointmentId).getRoom();
                sessionRepository.delete(session);
                participantRepository.deleteByLawyerId(userId);
                roomRepository.delete(room);
            }
        }
    }

    public HttpStatusCode removeRoom(Long appointmentId) {

        // 화상상담방을 파괴하고 싶은 Appointment 객체 얻기
        Appointment appointment = appointmentRepository.findById(appointmentId).orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "[RoomService - 00] 해당 ID 값을 가지는 Appointment가 없습니다."));

        // 이 Appointment에 해당하는 Session 객체 얻기
        Session session = sessionRepository.findByAppointmentId(appointmentId);

        // 이 Appointment에 대해 활성화된 세션이 없다면, 404 NotFound 에러 응답
        if(session == null) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "[RoomService - 00] 해당 상담은 화상상담방이 열려있지 않습니다.");
        }

        // 이 Session이 참조중인 Room 객체 얻어내고 Session 데이터 DB에서 삭제하기
        Room room = session.getRoom();
        sessionRepository.delete(session);

        // sessionId 알아내고 Room 데이터도 DB에서 삭제하기
        String openviduSessionId = room.getOpenviduSessionId();

        // openVidu 서버에 강제종료 요청보내기
        String url = MY_OPENVIDU_SERVER_URL + "/openvidu/api/sessions/" + openviduSessionId;

        /// ///////////////////////////////////////////////////////
        System.out.println("세션 종료시킬 때 사용한 url: " + url);
        /// ///////////////////////////////////////////////////////

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

        /// ///////////////////////////////////////////////////////
        System.out.println("sessionId 발급받을 때 사용한 url: " + url);
        /// ///////////////////////////////////////////////////////

        HttpHeaders headers = createHeaders();
        Map<String, String> body = Map.of("customSessionId", openviduCustomSessionId);

        HttpEntity<Map<String, String>> httpEntity = new HttpEntity<>(body, headers);

        ResponseEntity<OpenViduSessionResponse> openviduSessionResponse = restTemplate.postForEntity(url, httpEntity, OpenViduSessionResponse.class);

        return openviduSessionResponse.getBody().getId();
    }

    private String getToken(String openviduSessionId) {

        // 이제 sessionId 알고있으니깐(새로 생성됐으면 sessionId 리턴됐을거고, 이미 있는 customSessionId라 409 Conflict 발생했으면 그냥 기존에 알고있던 customSessionId를 sessionId로 쓰면 됨)
        // 그 sessionId 들고 sessions/{sessionId}/connections가서 토큰얻어오기
        String url = MY_OPENVIDU_SERVER_URL + "/openvidu/api/sessions/" + openviduSessionId + "/connection";

        /// ///////////////////////////////////////////////////////
        System.out.println("token 발급받을 때 사용한 url: " + url);
        /// ///////////////////////////////////////////////////////

        HttpHeaders headers = createHeaders();

        HttpEntity<Void> httpEntity = new HttpEntity<>(headers);

        ResponseEntity<OpenViduConnectionResponse> openviduConnectionResponse = restTemplate.postForEntity(url, httpEntity, OpenViduConnectionResponse.class);

        return openviduConnectionResponse.getBody().getToken(); // 토큰을 리턴해야함
    }
}
