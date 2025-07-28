package com.B204.lawvatar_backend.openvidu.room.entity;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.util.*;

@Entity
@Getter
@NoArgsConstructor
public class Room {

    // Field
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "room_id")
    private Long id;

    private String openviduCustomSessionId;
    private String openviduSessionId;

    // Method

    /**
     * customSessoinId를 생성하는 메서드
     * @return UUID 방식의 문자열
     */
    public static String generateCustomSessionId() {
        return UUID.randomUUID().toString();
    }

    /**
     * Room 객체 생성하는 정적 메서드
     * @param openviduCustomSessionId openVidu의 customSessionId
     * @param openviduSessionId openVidu의 sessionId
     * @return 생성된 Room 객체
     */
    public static Room createRoom(String openviduCustomSessionId, String openviduSessionId) {

        Room room = new Room();
        room.openviduCustomSessionId = openviduCustomSessionId;
        room.openviduSessionId = openviduSessionId;

        return room;
    }

}
