package com.B204.ALaw.openvidu.session.repository;

import com.B204.ALaw.openvidu.session.entity.Session;
import org.springframework.data.jpa.repository.JpaRepository;

public interface SessionRepository extends JpaRepository<Session, Long> {

    // Abstract Method
    Session findByAppointment_Id(Long appointmentId);

}
