package com.B204.lawvatar_backend.appointment.repository;

import com.B204.lawvatar_backend.appointment.entity.Appointment;
import com.B204.lawvatar_backend.user.client.entity.Client;
import com.B204.lawvatar_backend.user.lawyer.entity.Lawyer;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface AppointmentRepository extends JpaRepository<Appointment, Long> {

  List<Appointment> findByLawyer(Lawyer lawyer);

  List<Appointment> findByClient(Client client);

  boolean existsByLawyerIdAndClientId(Long lawyerId, Long clientId);

  List<Appointment> findByLawyerId(Long lawyerId);
  
  List<Appointment> findByApplicationId(Long applicationId);
}
