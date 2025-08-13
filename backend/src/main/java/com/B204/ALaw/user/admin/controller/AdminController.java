package com.B204.ALaw.user.admin.controller;

import com.B204.ALaw.appointment.dto.AppointmentResponseDto;
import com.B204.ALaw.appointment.entity.Appointment;
import com.B204.ALaw.appointment.repository.AppointmentRepository;
import com.B204.ALaw.common.principal.LawyerPrincipal;
import com.B204.ALaw.common.util.JwtUtil;
import com.B204.ALaw.openvidu.room.service.RoomService;
import com.B204.ALaw.user.admin.dto.LoginDto;
import com.B204.ALaw.user.admin.entity.Admin;
import com.B204.ALaw.user.admin.service.AdminService;
import com.B204.ALaw.user.auth.service.RefreshTokenService;
import com.B204.ALaw.user.client.dto.ClientAdminDto;
import com.B204.ALaw.user.client.entity.Client;
import com.B204.ALaw.user.client.repository.ClientRepository;
import com.B204.ALaw.user.lawyer.dto.LawyerAdminDto;
import com.B204.ALaw.user.lawyer.entity.CertificationStatus;
import com.B204.ALaw.user.lawyer.entity.Lawyer;
import com.B204.ALaw.user.lawyer.service.LawyerService;
import jakarta.persistence.EntityNotFoundException;
import jakarta.servlet.http.HttpServletResponse;
import java.time.Duration;
import java.util.List;
import java.util.Map;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.HttpStatusCode;
import org.springframework.http.ResponseCookie;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequestMapping("/api/admin")
public class AdminController {

  private final LawyerService lawyerService;
  private final RoomService roomService;
  private final RefreshTokenService refreshTokenService;

  private final ClientRepository clientRepo;
  private final AdminService adminService;
  private final AppointmentRepository appointmentRepo;

  private final AuthenticationManager adminAuthenticationManager;
  private final JwtUtil jwtUtil;

  public AdminController(LawyerService lawyerService,
      RoomService roomService,
      RefreshTokenService refreshTokenService,
      ClientRepository clientRepo,
      AdminService adminService,
      AppointmentRepository appointmentRepo,
      @Qualifier("adminAuthenticationManager")
      AuthenticationManager adminAuthenticationManager,
      JwtUtil jwtUtil
  ) {
    this.lawyerService = lawyerService;
    this.roomService = roomService;
    this.refreshTokenService = refreshTokenService;
    this.clientRepo = clientRepo;
    this.adminService = adminService;
    this.appointmentRepo = appointmentRepo;
    this.adminAuthenticationManager = adminAuthenticationManager;
    this.jwtUtil = jwtUtil;
  }

  @PostMapping("/login")
  public ResponseEntity<Map<String,String>> login(
      @RequestBody LoginDto dto,
      HttpServletResponse response
  ) {
    try {
      // 관리 전용 매니저로 인증 시도 (더 이상 순환 없음)
      Authentication auth = adminAuthenticationManager.authenticate(
          new UsernamePasswordAuthenticationToken(dto.getLoginEmail(), dto.getPassword())
      );

      System.out.println("관리자 ^^  :  " + auth.getPrincipal());

      String email = auth.getName();
      Admin admin = adminService.findByLoginEmail(email);
      String subject = "ADMIN:" + admin.getLoginEmail();

      // 리프레시 토큰 생성·저장
      String refreshToken = jwtUtil.generateRefreshToken(subject, "ADMIN");
      refreshTokenService.createForAdmin(admin, refreshToken);

      // 쿠키 세팅
      ResponseCookie cookie = ResponseCookie.from("refresh_token", refreshToken)
          .httpOnly(true).secure(true).sameSite("None")
          .path("/").maxAge(Duration.ofDays(7)).build();
      response.setHeader(HttpHeaders.SET_COOKIE, cookie.toString());
      // 액세스 토큰 발급
      List<String> roles = auth.getAuthorities().stream()
          .map(GrantedAuthority::getAuthority).toList();
      String accessToken = jwtUtil.generateAccessToken(subject, roles, "ADMIN");
      return ResponseEntity.ok(Map.of("accessToken", accessToken));
    } catch (AuthenticationException ex) {
      return ResponseEntity
          .status(HttpStatus.UNAUTHORIZED)
          .body(Map.of("error", "Admin Login Failed"));
    }
  }

  @GetMapping("/lawyers/certifications")
  @PreAuthorize("hasRole('ADMIN')")
  public ResponseEntity<List<LawyerAdminDto>> getLawyersByCertificationStatus(
      @RequestParam CertificationStatus status
  ){

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
  @PreAuthorize("hasRole('ADMIN')")
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
  @PreAuthorize("hasRole('ADMIN')")
  public ResponseEntity<?> approveLawyer(
      @PathVariable("id") Long id
  ) {
    try{
      System.out.println("승인");
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
  @PreAuthorize("hasRole('ADMIN')")
  public ResponseEntity<?> rejectLawyer(
      @PathVariable("id") Long id
  ) {
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
  @PreAuthorize("hasRole('ADMIN')")
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

  @DeleteMapping("/rooms/{appointmentId}")
  @PreAuthorize("hasRole('ADMIN')")
  public ResponseEntity<Void> removeRoom(
      Authentication authentication,
      @PathVariable Long appointmentId
  ) {

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
