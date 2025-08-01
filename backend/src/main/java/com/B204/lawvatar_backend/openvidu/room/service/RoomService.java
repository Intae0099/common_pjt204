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
import org.springframework.http.*;
import org.springframework.stereotype.Service;
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
    private static final String MY_OPENVIDU_SERVER_URL = "https://i13b204.p.ssafy.io/openvidu/api/sessions";
    private static final String OPENVIDU_SECRET_KEY = "ssafy204openvidulawaid";

    private final RoomRepository roomRepository;
    private final AppointmentRepository appointmentRepository;
    private final ParticipantRepository participantRepository;
    private final SessionRepository sessionRepository;
    private final ClientRepository clientRepository;
    private final LawyerRepository lawyerRepository;

    private final RestTemplate restTemplate;

    // Method
    public String createRoom(Long appointmentId, String userType, Long id) throws Exception{

        String openviduCustomSessionId = Room.generateCustomSessionId();

        // 생성한 customSessionId 들고 sessionId 얻으러 가기
        OpenViduSessionResponse openViduSessionResponse = getSessionId(openviduCustomSessionId);
        String openviduSessionId = openViduSessionResponse.getId();

        /// ///////////////////////////////////////////////////////
        System.out.println("얻어온 세션아이디:" + openviduSessionId);
        /// ///////////////////////////////////////////////////////

        // openvidu 관련 데이터들 가지고 Room 객체 생성해서 DB에 저장하기
        Room room = Room.builder().openviduCustomSessionId(openviduCustomSessionId).openviduSessionId(openviduSessionId).build();
        roomRepository.save(room);

        // sessionId 들고 connections 가서 토큰 얻어오기
        String token = getToken(openviduSessionId).getToken();

        /// ///////////////////////////////////////////////////////
        System.out.println("생성 토큰 획득 성공!" + token);
        /// ///////////////////////////////////////////////////////

        // Participant 테이블에 참가정보 저장하기
        // 유저타입에 따라 Participant 객체 만들어서 DB에 저장
        if(userType.equals("CLIENT")) {
            Client client = clientRepository.findById(id).orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "[RoomService - 00] 해당 ID 값을 가지는 Client가 없습니다."));
            Participant participant = Participant.builder().client(client).room(room).build();
            participantRepository.save(participant);
        } else if(userType.equals("LAWYER")) {
            Lawyer lawyer = lawyerRepository.findById(id).orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "[RoomService - 00] 해당 ID 값을 가지는 Lawyer가 없습니다."));
            Participant participant = Participant.builder().lawyer(lawyer).room(room).build();
            participantRepository.save(participant);
        }

        // Session 테이블에 세션정보 저장하기
        Appointment appointment = appointmentRepository.findById(appointmentId).orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "[RoomService - 00] 해당 ID 값을 가지는 Appointment가 없습니다."));
        Session session = Session.builder().appointment(appointment).room(room).participantCount(1).build();
        sessionRepository.save(session);

        return token;
    }

    public String participateRoom(Long appointmentId, String userType, Long id) throws Exception {

        // 이 Appointment 객체에 대한 Session 객체와 Room 객체 얻기
        Session session = sessionRepository.findByAppointmentId(appointmentId);
        Room room = session.getRoom();

        // Participant 테이블에 참가정보 저장하기
        // 유저타입에 따라 Participant 객체 만들어서 DB에 저장
        if(userType.equals("CLIENT")) {
            Client client = clientRepository.findById(id).orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "[RoomService - 00] 해당 ID 값을 가지는 Client가 없습니다."));
            Participant participant = Participant.builder().client(client).room(room).build();
            participantRepository.save(participant);
        } else if(userType.equals("LAWYER")) {
            Lawyer lawyer = lawyerRepository.findById(id).orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "[RoomService - 00] 해당 ID 값을 가지는 Lawyer가 없습니다."));
            Participant participant = Participant.builder().lawyer(lawyer).room(room).build();
            participantRepository.save(participant);
        }

        // Session 객체 참가자 수 올리기
        // 더티체킹 되기 때문에 따로 저장할 필요는 없음
        session.setParticipantCount(session.getParticipantCount()+1);

        // sessionId는 방금 찾아온 Room 객체에서 가져오기
        String openviduSessionId = room.getOpenviduSessionId();

        // sessionId 들고 토큰 받으러 가기
        String token = getToken(openviduSessionId).getToken();

        /// ///////////////////////////////////////////////////////
        System.out.println("참가 토큰 획득 성공!" + token);
        /// ///////////////////////////////////////////////////////

        return token;
    }

    private HttpHeaders createHeaders() {
        String auth = "OPENVIDUAPP:" + OPENVIDU_SECRET_KEY;
        String encodedAuth = Base64.getEncoder().encodeToString(auth.getBytes(StandardCharsets.UTF_8));
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.add("Authorization", "Basic " + encodedAuth);
        return headers;
    }

    private OpenViduSessionResponse getSessionId(String openviduCustomSessionId) throws Exception{

        // customSessionId 들고 sessions 가서 openvidu 내부 sessionId 얻어오기
        HttpHeaders headers = createHeaders();
        Map<String, String> body = Map.of("customSessionId", openviduCustomSessionId);

        HttpEntity<Map<String, String>> httpEntity = new HttpEntity<>(body, headers);

        return restTemplate.postForEntity(MY_OPENVIDU_SERVER_URL, httpEntity, OpenViduSessionResponse.class).getBody();
    }

    private OpenViduConnectionResponse getToken(String openviduSessionId) {

        // 이제 sessionId 알고있으니깐(새로 생성됐으면 sessionId 리턴됐을거고, 이미 있는 customSessionId라 409 Conflict 발생했으면 그냥 기존에 알고있던 customSessionId를 sessionId로 쓰면 됨)
        // 그 sessionId 들고 sessions/{sessionId}/connections가서 토큰얻어오기
        String url = MY_OPENVIDU_SERVER_URL + openviduSessionId + "/connections";
        System.out.println("사용 url: " + url);
        HttpHeaders headers = createHeaders();

        HttpEntity<Void> httpEntity = new HttpEntity<>(headers);

        ResponseEntity<OpenViduConnectionResponse> connectionResponse = restTemplate.postForEntity(url, httpEntity, OpenViduConnectionResponse.class);

        return connectionResponse.getBody(); // 토큰을 리턴해야함
    }
}
