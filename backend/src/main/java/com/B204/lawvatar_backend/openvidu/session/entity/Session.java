package com.B204.lawvatar_backend.openvidu.session.entity;

import com.B204.lawvatar_backend.appointment.entity.Appointment;
import com.B204.lawvatar_backend.openvidu.room.entity.Room;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Entity
@Getter
@NoArgsConstructor
public class Session {

    // Field
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "session_id")
    private Long id;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "appointment_id")
    private Appointment appointment;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "room_id")
    private Room room;

    @Column(columnDefinition = "tinyint unsigned")
    private int participantCount;

}
