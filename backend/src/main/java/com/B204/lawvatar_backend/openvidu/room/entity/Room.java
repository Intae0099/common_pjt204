package com.B204.lawvatar_backend.openvidu.room.entity;
import jakarta.persistence.*;
import lombok.*;

import java.util.*;

@Entity
@Getter @Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Room {

    // Field
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String openviduCustomSessionId;

    @Column(nullable = false)
    private String openviduSessionId;

    // Method
    /**
     * customSessoinId를 생성하는 메서드
     * @return UUID 방식의 문자열
     */
    public static String generateCustomSessionId() {
        return UUID.randomUUID().toString();
    }

}
