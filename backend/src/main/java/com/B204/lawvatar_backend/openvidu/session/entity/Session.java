package com.B204.lawvatar_backend.openvidu.session.entity;

import com.B204.lawvatar_backend.appointment.entity.Appointment;
import com.B204.lawvatar_backend.openvidu.room.entity.Room;
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
    private Long id;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "appointment_id", nullable = false)
    private Appointment appointment;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "room_id", nullable = false)
    private Room room;

    @Column(columnDefinition = "tinyint unsigned")
    private int participantCount;

}
