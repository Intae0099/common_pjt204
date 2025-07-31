package com.B204.lawvatar_backend.appointment.controller;

import com.B204.lawvatar_backend.application.repository.ApplicationRepository;
import com.B204.lawvatar_backend.appointment.dto.AppointmentRequestDto;
import com.B204.lawvatar_backend.appointment.dto.AppointmentResponseDto;
import com.B204.lawvatar_backend.appointment.dto.AppointmentStatusRequestDto;
import com.B204.lawvatar_backend.appointment.dto.MyAppointmentDto;
import com.B204.lawvatar_backend.appointment.entity.Appointment;
import com.B204.lawvatar_backend.appointment.entity.AppointmentStatus;
import com.B204.lawvatar_backend.appointment.repository.AppointmentRepository;
import com.B204.lawvatar_backend.appointment.service.AppointmentService;
import com.B204.lawvatar_backend.common.principal.ClientPrincipal;
import com.B204.lawvatar_backend.common.principal.LawyerPrincipal;
import com.B204.lawvatar_backend.common.util.JwtUtil;
import com.B204.lawvatar_backend.user.client.entity.Client;
import com.B204.lawvatar_backend.user.client.repository.ClientRepository;
import com.B204.lawvatar_backend.user.lawyer.entity.Lawyer;
import com.B204.lawvatar_backend.user.lawyer.repository.LawyerRepository;
import io.jsonwebtoken.Claims;
import jakarta.validation.Valid;
import java.net.URI;
import java.nio.file.attribute.UserPrincipal;
import java.util.Collections;
import java.util.List;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequestMapping("/api/appointments")
public class AppointmentController {

  private final AppointmentService appointmentService;

  private final AppointmentRepository appointmentRepo;
  private final LawyerRepository lawyerRepo;
  private final ClientRepository clientRepo;

  public AppointmentController(AppointmentRepository appointmentRepo, JwtUtil jwtUtil,
      AppointmentService appointmentService,
      LawyerRepository lawyerRepo, ClientRepository clientRepo) {
    this.appointmentRepo = appointmentRepo;
    this.appointmentService = appointmentService;
    this.lawyerRepo = lawyerRepo;
    this.clientRepo = clientRepo;
  }

  @GetMapping("/me")
  public ResponseEntity<List<MyAppointmentDto>> getMyAppointments(
      Authentication authentication,
      @RequestParam(value = "status", required = false) AppointmentStatus status
  ) {
    Object principal = authentication.getPrincipal();
    List<Appointment> appts = List.of();

    if (principal instanceof LawyerPrincipal lawyerPrincipal) {
      // 변호사로 로그인 됐으면
      Lawyer lawyer = lawyerRepo.findById(lawyerPrincipal.getId())
          .orElseThrow(() -> new UsernameNotFoundException("변호사 없음: " + lawyerPrincipal.getId()));
      appts = appointmentRepo.findByLawyer(lawyer);

    } else if (principal instanceof ClientPrincipal clientPrincipal) {
      // 의뢰인으로 로그인 됐으면
      Client client = clientRepo.findById(clientPrincipal.getId())
          .orElseThrow(() -> new UsernameNotFoundException("의뢰인 없음: " + clientPrincipal.getId()));
      appts = appointmentRepo.findByClient(client);

    } else {
      throw new AccessDeniedException("올바르지 않은 사용자 타입입니다.");
    }

    if (status != null) {
      appts = appts.stream()
          .filter(a -> a.getAppointmentStatus() == status)
          .toList();
    }

    if (appts.isEmpty()) {
      return ResponseEntity.ok(Collections.emptyList());
    }

    List<MyAppointmentDto> dtoList = appts.stream()
        .map(MyAppointmentDto::from)
        .toList();
    return ResponseEntity.ok(dtoList);
  }

  @PostMapping
  public ResponseEntity<AppointmentResponseDto> createAppointment(
      Authentication authentication,
      @Valid @RequestBody AppointmentRequestDto req
  ){

    Long clientId;
    if (authentication.getPrincipal() instanceof LawyerPrincipal) {
      throw new ResponseStatusException(HttpStatus.FORBIDDEN, "변호사는 상담 예약을 할 수 없습니다.");
    } else if (authentication.getPrincipal() instanceof ClientPrincipal cp) {
      clientId = cp.getId();
    } else {
      throw new ResponseStatusException(HttpStatus.FORBIDDEN, "알 수 없는 사용자 타입입니다.");
    }

    Appointment appt = appointmentService.create(
        clientId,
        req.getLawyerId(),
        req.getApplicationId(),
        req.getStartTime(),
        req.getEndTime()
    );

    AppointmentResponseDto body = AppointmentResponseDto.from(appt);
    // Location header: /api/appointments/{id}
    return ResponseEntity
        .created(URI.create("/api/appointments/" + appt.getId()))
        .body(body);
  }

  /**
    변호사가 자신에게 온 상담을 승인 / 거절
   */
  @PatchMapping("/{appointmentId}/status")
  public ResponseEntity<Void> updateAppointmentStatus(
      @PathVariable Long appointmentId,
      @Valid @RequestBody AppointmentStatusRequestDto dto,
      Authentication authentication
  ) {

    if (!(authentication.getPrincipal() instanceof LawyerPrincipal lp)) {
      throw new ResponseStatusException(HttpStatus.FORBIDDEN, "권한이 없습니다.");
    }
    Long lawyerId = lp.getId();

    // 2) 서비스 호출 (내부에서 권한·상태 전환 검증)
    appointmentService.updateStatus(appointmentId, lawyerId, dto.getAppointmentStatus());

    return ResponseEntity.ok().build();
  }

  @PatchMapping("/{appointmentId}/cancel")
  public ResponseEntity<Void> cancelAppointment(
    @PathVariable Long appointmentId,
    Authentication authentication
  ){
    if(!(authentication.getPrincipal() instanceof ClientPrincipal cp)){
      throw new ResponseStatusException(HttpStatus.FORBIDDEN, "취소할 권한이 없습니다.");
    }

    Long clientId = cp.getId();
    appointmentService.cancel(appointmentId, clientId);

    return ResponseEntity.ok().build();
  }
}
