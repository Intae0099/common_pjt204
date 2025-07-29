package com.B204.lawvatar_backend.openvidu.participant.entity;

import com.B204.lawvatar_backend.openvidu.room.entity.Room;
import com.B204.lawvatar_backend.user.client.entity.Client;
import com.B204.lawvatar_backend.user.lawyer.entity.Lawyer;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Entity
@Getter
@NoArgsConstructor
public class Participant {

    // Field
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "room_id")
    @Column(nullable = false)
    private Room room;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "client_id")
    @Column(nullable = false)
    private Client client;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "lawyer_id")
    @Column(nullable = false)
    private Lawyer lawyer;

    // Method
    /**
     * 클라이언트가 참가자인 Participant 객체를 생성하는 정적 메서드
     * @param room
     * @param client
     * @return
     */
    public static Participant createClientParticipant(Room room, Client client) {
        Participant participant = new Participant();
        participant.room = room;
        participant.client = client;

        return participant;
    }

    /**
     * 변호사가 참가자인 Participant 객체를 생성하는 정적 메서드
     * @param room
     * @param lawyer
     * @return
     */
    public static Participant createLawyerParticipant(Room room, Lawyer lawyer) {
        Participant participant = new Participant();
        participant.room = room;
        participant.lawyer = lawyer;

        return participant;
    }
}
