package com.B204.ALaw.openvidu.room.entity;

import com.B204.ALaw.openvidu.participant.entity.Participant;
import com.B204.ALaw.openvidu.session.entity.Session;
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
    @Column(columnDefinition = "int unsigned")
    private Long id;

    @Column(length = 100, nullable = false)
    private String openviduCustomSessionId;

    @Column(length = 100, nullable = false)
    private String openviduSessionId;

    @OneToOne(mappedBy = "room", cascade = CascadeType.ALL, orphanRemoval = true, fetch = FetchType.LAZY)
    private Session session;

    @OneToMany(mappedBy = "room", cascade = CascadeType.ALL, orphanRemoval = true, fetch = FetchType.LAZY)
    private List<Participant> participantList = new ArrayList<>();

    // Method
    /**
     * customSessoinId를 생성하는 메서드
     * @return UUID 방식의 문자열
     */
    public static String generateCustomSessionId() {
        return UUID.randomUUID().toString();
    }

}
