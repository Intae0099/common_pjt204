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
import org.springframework.security.access.prepost.PreAuthorize;
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
      @AuthenticationPrincipal Object principal,
      @RequestParam(value = "status", required = false) AppointmentStatus status
  ) {
    List<Appointment> appts = List.of();

    if (principal instanceof LawyerPrincipal lawyerPrincipal) {       // 변호사로 로그인 됐으면
      Lawyer lawyer = lawyerRepo.findById(lawyerPrincipal.getId())
          .orElseThrow(() -> new UsernameNotFoundException("변호사 없음: " + lawyerPrincipal.getId()));

      appts = appointmentRepo.findByLawyer(lawyer);

    } else if (principal instanceof ClientPrincipal clientPrincipal) {        // 의뢰인으로 로그인 됐으면
      Client client = clientRepo.findById(clientPrincipal.getId())
          .orElseThrow(() -> new UsernameNotFoundException("의뢰인 없음: " + clientPrincipal.getId()));

      appts = appointmentRepo.findByClient(client);

    }

    if (status != null) {
      appts = appts.stream()
          .filter(a -> a.getAppointmentStatus() == status)
          .toList();
    }

    List<MyAppointmentDto> dtoList = appts.stream()
        .map(MyAppointmentDto::from)
        .toList();
    return ResponseEntity.ok(dtoList);
  }

  @PostMapping
  @PreAuthorize("hasRole('CLIENT')")
  public ResponseEntity<AppointmentResponseDto> createAppointment(
      @AuthenticationPrincipal ClientPrincipal client,
      @Valid @RequestBody AppointmentRequestDto req
  ){

    Appointment appt = appointmentService.create(
        client.getId(),
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
  @PreAuthorize("hasRole('LAWYER')")
  public ResponseEntity<Void> updateAppointmentStatus(
      @PathVariable Long appointmentId,
      @Valid @RequestBody AppointmentStatusRequestDto dto,
      @AuthenticationPrincipal LawyerPrincipal lawyer
  ) {
    Long lawyerId = lawyer.getId();
    appointmentService.updateStatus(appointmentId, lawyerId, dto.getAppointmentStatus());

    return ResponseEntity.ok().build();
  }

  @PatchMapping("/{appointmentId}/cancel")
  @PreAuthorize("hasRole('LAWYER')")
  public ResponseEntity<Void> cancelAppointment(
    @PathVariable Long appointmentId,
      @AuthenticationPrincipal LawyerPrincipal lawyer
  ){
    Long clientId = lawyer.getId();
    appointmentService.cancel(appointmentId, clientId);

    return ResponseEntity.ok().build();
  }

}
