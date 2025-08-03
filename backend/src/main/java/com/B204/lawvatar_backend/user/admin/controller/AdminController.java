package com.B204.lawvatar_backend.user.admin.controller;

import com.B204.lawvatar_backend.appointment.dto.AppointmentResponseDto;
import com.B204.lawvatar_backend.appointment.entity.Appointment;
import com.B204.lawvatar_backend.appointment.repository.AppointmentRepository;
import com.B204.lawvatar_backend.common.principal.LawyerPrincipal;
import com.B204.lawvatar_backend.openvidu.room.service.RoomService;
import com.B204.lawvatar_backend.user.client.dto.ClientAdminDto;
import com.B204.lawvatar_backend.user.client.entity.Client;
import com.B204.lawvatar_backend.user.client.repository.ClientRepository;
import com.B204.lawvatar_backend.user.lawyer.dto.LawyerAdminDto;
import com.B204.lawvatar_backend.user.lawyer.entity.CertificationStatus;
import com.B204.lawvatar_backend.user.lawyer.entity.Lawyer;
import com.B204.lawvatar_backend.user.lawyer.service.LawyerService;
import jakarta.persistence.EntityNotFoundException;
import java.util.List;
import java.util.Map;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.HttpStatusCode;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequestMapping("/api/admin")
@RequiredArgsConstructor
public class AdminController {

  private final LawyerService lawyerService;
  private final RoomService roomService;

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

  @DeleteMapping("/rooms/{appointmentId")
  public ResponseEntity<Void> removeRoom(Authentication authentication, @PathVariable Long appointmentId) {

    // Principal 객체 얻기
    Object principal = authentication.getPrincipal();

    // 변호사이면 비즈니스 로직 진행, 아니면 403 Forbidden 에러 발생 (변호사만 관리자가 될 수 있음)
    if (principal instanceof LawyerPrincipal lawyerPrincipal) {

      HttpStatusCode result = roomService.removeRoom(appointmentId);

      if (result == HttpStatus.NO_CONTENT) {
        System.out.println(appointmentId + "번 상담의 화상상담방이 강제종료 되었습니다.");
        return ResponseEntity.status(HttpStatus.OK).build();
      } else {
        System.out.println("[에러코드: " + result + "] 화상상담방 강제종료에 실패하였습니다.");
        throw new ResponseStatusException(result, "[AdminController - 001][에러코드: " + result + "] 알 수 없는 이유로 화상상담방 강제종료에 실패하였습니다.");
      }

    } else {
      throw new ResponseStatusException(HttpStatus.FORBIDDEN, "[AdminController - 002] 관리자만 이용할 수 있는 기능입니다.");
    }
  }
}
