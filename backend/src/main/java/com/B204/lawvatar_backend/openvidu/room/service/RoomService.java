package com.B204.lawvatar_backend.openvidu.room.service;

import com.B204.lawvatar_backend.openvidu.room.dto.OpenViduConnectionResponse;
import com.B204.lawvatar_backend.openvidu.room.dto.OpenViduSessionResponse;
import com.B204.lawvatar_backend.openvidu.room.entity.Room;
import com.B204.lawvatar_backend.openvidu.room.repository.RoomRepository;
import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

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
    private static final String MY_OPENVIDU_SERVER_URL = "https://i13b204.p.ssafy.io:5443";
    private static final String OPENVIDU_SECRET_KEY = "ssafy204openvidulawaid";

    private final RoomRepository roomRepository;
    private final RestTemplate restTemplate;

    // Method
    public Map<String, Object> createRoom() throws Exception{

        String customSessionId = Room.generateCustomSessionId();

        // 생성한 customSessionId 들고 sessionId 얻으러 가기
        OpenViduSessionResponse openViduSessionResponse = getSessionId(customSessionId);
        String sessionId = openViduSessionResponse.getId();

        /// ///////////////////////////////////////////////////////
        System.out.println("얻어온 세션아이디:" + sessionId);
        /// ///////////////////////////////////////////////////////

        Room room = Room.createRoom(customSessionId, sessionId);
        Long roomId = roomRepository.save(room);

        // sessionId 들고 connections 가서 토큰 얻어오기
        String token = getToken(sessionId).getToken();

        /// ///////////////////////////////////////////////////////
        System.out.println("생성 토큰 획득 성공!");
        /// ///////////////////////////////////////////////////////

        Map<String, Object> result = new HashMap<>();

        // 방 생성 요청이므로 프론트에서 방금 생긴 방의 customSessionId을 아직 모르고 있으므로 방금 여기서 만든 customSessionId도 같이 돌려줘야함
        result.put("roomId", roomId);
        result.put("customSessionId", customSessionId);
        result.put("token", token);

        return result;
    }

    public Map<String, Object> participateRoom(String customSessionId) throws Exception {

        List<Room> rooms = roomRepository.findByCustomSessionId(customSessionId); // RoomRepository에 getSessionIdByCustomSessionId 메서드까지 두는 것은 너무 레포지토리에서 많은걸 하는거같아서 해당하는 room 객체만 가져오면 조건에 맞는 sessionId 찾는건 서비스 단에서 하기!
        String sessionId = rooms.get(0).getOpenviduSessionId();

        // sessionId 들고 토큰 받으러 가기
        String token = getToken(sessionId).getToken();

        /// ///////////////////////////////////////////////////////
        System.out.println("참가 토큰 획득 성공!");
        /// ///////////////////////////////////////////////////////

        Map<String, Object> result = new HashMap<>();

        result.put("roomId", rooms.get(0).getId());
        result.put("token", token);

        return result; // 토큰을 리턴해야함
    }

    private HttpHeaders createHeaders() {
        String auth = "OPENVIDUAPP:" + OPENVIDU_SECRET_KEY;
        String encodedAuth = Base64.getEncoder().encodeToString(auth.getBytes(StandardCharsets.UTF_8));
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.add("Authorization", "Basic " + encodedAuth);
        return headers;
    }

    private OpenViduSessionResponse getSessionId(String customSessionId) throws Exception{

        // customSessionId 들고 sessions 가서 openvidu 내부 sessionId 얻어오기
        String url = MY_OPENVIDU_SERVER_URL + "/openvidu/api/sessions";
        HttpHeaders headers = createHeaders();
        Map<String, String> body = Map.of("customSessionId", customSessionId);

        HttpEntity<Map<String, String>> httpEntity = new HttpEntity<>(body, headers);

        return restTemplate.postForEntity(url, httpEntity, OpenViduSessionResponse.class).getBody();
    }

    private OpenViduConnectionResponse getToken(String sessionId) {

        // 이제 sessionId 알고있으니깐(새로 생성됐으면 sessionId 리턴됐을거고, 이미 있는 customSessionId라 409 Conflict 발생했으면 그냥 기존에 알고있던 customSessionId를 sessionId로 쓰면 됨)
        // 그 sessionId 들고 sessions/{sessionId}/connections가서 토큰얻어오기
        String url = MY_OPENVIDU_SERVER_URL + "/openvidu/api/sessions/" + sessionId + "/connections";
        System.out.println("사용 url: " + url);
        HttpHeaders headers = createHeaders();

        HttpEntity<Void> httpEntity = new HttpEntity<>(headers);

        ResponseEntity<OpenViduConnectionResponse> connectionResponse = restTemplate.postForEntity(url, httpEntity, OpenViduConnectionResponse.class);

        return connectionResponse.getBody(); // 토큰을 리턴해야함
    }

    public List<Room> getRoomList() {

        return roomRepository.findAll();
    }
}
