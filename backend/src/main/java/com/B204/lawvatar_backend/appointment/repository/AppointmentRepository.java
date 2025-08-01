package com.B204.lawvatar_backend.appointment.repository;

import com.B204.lawvatar_backend.appointment.entity.Appointment;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

public interface AppointmentRepository extends JpaRepository<Appointment, Long> {

    // Abstract Method
    List<Appointment> findByLawyerId(Long lawyerId);
    List<Appointment> findByApplicationId(Long applicationId);
}
