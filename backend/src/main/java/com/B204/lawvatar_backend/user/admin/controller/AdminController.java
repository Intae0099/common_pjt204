package com.B204.lawvatar_backend.user.admin.controller;

import com.B204.lawvatar_backend.appointment.dto.AppointmentResponseDto;
import com.B204.lawvatar_backend.appointment.entity.Appointment;
import com.B204.lawvatar_backend.appointment.repository.AppointmentRepository;
import com.B204.lawvatar_backend.user.client.dto.ClientAdminDto;
import com.B204.lawvatar_backend.user.client.entity.Client;
import com.B204.lawvatar_backend.user.client.repository.ClientRepository;
import com.B204.lawvatar_backend.user.lawyer.dto.LawyerAdminDto;
import com.B204.lawvatar_backend.user.lawyer.entity.CertificationStatus;
import com.B204.lawvatar_backend.user.lawyer.entity.Lawyer;
import com.B204.lawvatar_backend.user.lawyer.repository.LawyerRepository;
import com.B204.lawvatar_backend.user.lawyer.service.LawyerService;
import jakarta.persistence.EntityNotFoundException;
import java.util.List;
import java.util.Map;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/admin")
@RequiredArgsConstructor
public class AdminController {

  private final LawyerService lawyerService;

  private final ClientRepository clientRepo;
  private final AppointmentRepository appointmentRepo;

  @GetMapping("/lawyers/certifications")
  public ResponseEntity<List<LawyerAdminDto>> getLawyersByCertificationStatus(@RequestParam CertificationStatus status){

    List<Lawyer> lawyers = lawyerService.findByCertificationStatus(status);
    if(lawyers.isEmpty()) {
      return ResponseEntity.noContent().build();
    }

    List<LawyerAdminDto> res = lawyers.stream()
        .map(LawyerAdminDto::from)
        .toList();

    return ResponseEntity.ok(res);
  }

  @GetMapping("/clients")
  public ResponseEntity<List<ClientAdminDto>> getAllClients(){
    List<Client> clients = clientRepo.findAll();
    if(clients.isEmpty()){
      return ResponseEntity.noContent().build();
    }

    List<ClientAdminDto> res = clients.stream()
        .map(ClientAdminDto::from)
        .toList();

    return ResponseEntity.ok(res);
  }

  @PatchMapping("/{id}/approve")
  public ResponseEntity<?> approveLawyer(@PathVariable("id") Long id) {
    try{
      Lawyer l = lawyerService.approveLawyer(id);

      return ResponseEntity.ok(Map.of(
         "lawyerId", l.getId(),
          "status", l.getCertificationStatus().name()
      ));

    }catch (EntityNotFoundException e){
      return ResponseEntity.status(HttpStatus.NOT_FOUND)
          .body(Map.of("error", e.getMessage()));
    }catch (IllegalStateException e){
      return ResponseEntity.status(HttpStatus.BAD_REQUEST)
          .body(Map.of("error", e.getMessage()));
    }
  }

  @PatchMapping("/{id}/reject")
  public ResponseEntity<?> rejectLawyer(@PathVariable("id") Long id) {
    try{
      Lawyer l = lawyerService.rejectLawyer(id);

      return ResponseEntity.ok(Map.of(
          "lawyerId", l.getId(),
          "status", l.getCertificationStatus().name()
      ));

    }catch (EntityNotFoundException e){
      return ResponseEntity.status(HttpStatus.NOT_FOUND)
          .body(Map.of("error", e.getMessage()));
    }catch (IllegalStateException e){
      return ResponseEntity.status(HttpStatus.BAD_REQUEST)
          .body(Map.of("error", e.getMessage()));
    }
  }

  @GetMapping("/appointments")
  public ResponseEntity<List<AppointmentResponseDto>> getAllAppointments(){
    List<Appointment> appts = appointmentRepo.findAll();

    if(appts.isEmpty()){
      return ResponseEntity.noContent().build();
    }

    List<AppointmentResponseDto> res = appts.stream()
        .map(AppointmentResponseDto::from)
        .toList();

    return ResponseEntity.ok(res);
  }

}
