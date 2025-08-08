package com.B204.lawvatar_backend.openvidu.session.repository;

import com.B204.lawvatar_backend.openvidu.session.entity.Session;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface SessionRepository extends JpaRepository<Session, Long> {

    // Abstract Method
    Session findByAppointment_Id(Long appointmentId);

}
