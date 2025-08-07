package com.B204.ALaw.openvidu.session.entity;

import com.B204.ALaw.appointment.entity.Appointment;
import com.B204.ALaw.openvidu.room.entity.Room;
import jakarta.persistence.*;
import lombok.*;

@Entity
@Getter @Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Session {

    // Field
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(columnDefinition = "int unsigned")
    private Long id;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "appointment_id", nullable = false)
    private Appointment appointment;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "room_id", nullable = false)
    private Room room;

    @Column(columnDefinition = "tinyint unsigned default 1", nullable = false)
    private int participantCount = 1; // 세션정보가 만들어졌다는 건 참여 인원수가 최소 1명이라는 것

}
