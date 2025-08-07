package com.B204.ALaw.appointment.controller;

import com.B204.ALaw.application.entity.Application;
import com.B204.ALaw.application.entity.ApplicationTag;
import com.B204.ALaw.appointment.dto.AppointmentRequestDto;
import com.B204.ALaw.appointment.dto.AppointmentResponseDto;
import com.B204.ALaw.appointment.dto.AppointmentStatusRequestDto;
import com.B204.ALaw.appointment.dto.GetMyAppointmentApplicationListResponse;
import com.B204.ALaw.appointment.dto.MyAppointmentDto;
import com.B204.ALaw.appointment.entity.Appointment;
import com.B204.ALaw.appointment.entity.AppointmentStatus;
import com.B204.ALaw.appointment.repository.AppointmentRepository;
import com.B204.ALaw.appointment.service.AppointmentService;
import com.B204.ALaw.common.principal.ClientPrincipal;
import com.B204.ALaw.common.principal.LawyerPrincipal;
import com.B204.ALaw.common.util.JwtUtil;
import com.B204.ALaw.user.client.repository.ClientRepository;
import com.B204.ALaw.user.lawyer.repository.LawyerRepository;
import jakarta.validation.Valid;
import java.net.URI;
import java.util.ArrayList;
import java.util.List;
import java.util.function.Function;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

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
    // 1. 사용자 타입 판별
    final boolean isLawyer = principal instanceof LawyerPrincipal;

    // 2. 약간의 캐스팅 로직
    List<Appointment> appts;
    if (isLawyer) {
      Long id = ((LawyerPrincipal) principal).getId();
      appts = appointmentRepo.findByLawyer(
          lawyerRepo.findById(id)
              .orElseThrow(() -> new UsernameNotFoundException("변호사 없음: " + id))
      );
    } else {
      Long id = ((ClientPrincipal) principal).getId();
      appts = appointmentRepo.findByClient(
          clientRepo.findById(id)
              .orElseThrow(() -> new UsernameNotFoundException("의뢰인 없음: " + id))
      );
    }

    // 3. 상태 필터링(Optional)
    if (status != null) {
      appts = appts.stream()
          .filter(a -> a.getAppointmentStatus() == status)
          .toList();
    }

    // 4. 사용할 팩토리 메서드 한 번만 결정
    Function<Appointment, MyAppointmentDto> mapper =
        isLawyer
            ? MyAppointmentDto::fromLawyer
            : MyAppointmentDto::fromClient;

    // 5. 매핑
    List<MyAppointmentDto> dtoList = appts.stream()
        .map(mapper)
        .toList();

    return ResponseEntity.ok(dtoList);
  }

  @PostMapping
  @PreAuthorize("hasRole('CLIENT')")
  public ResponseEntity<AppointmentResponseDto> createAppointment(
      @AuthenticationPrincipal ClientPrincipal client,
      @Valid @RequestBody AppointmentRequestDto req
  ){
    System.out.println(req);

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
  @PreAuthorize("hasRole('CLIENT')")
  public ResponseEntity<Void> cancelAppointment(
    @PathVariable Long appointmentId,
      @AuthenticationPrincipal ClientPrincipal client
  ){
    Long clientId = client.getId();
    appointmentService.cancel(appointmentId, clientId);

    return ResponseEntity.ok().build();
  }

    /**
     * 변호사가 자신의 상담에 대한 상담신청서 목록을 전체조회하는 메서드
     * @param authentication
     * @return
     */
    @GetMapping("/me/applications")
    public ResponseEntity<GetMyAppointmentApplicationListResponse> getMyAppointmentApplicationList(
        Authentication authentication
    ) {
        // Principal 객체 얻기
        Object principal = authentication.getPrincipal();

        // 변호사 맞는지 검사하고 맞으면 비즈니스 로직 진행, 아니면 에러 응답
        if(principal instanceof LawyerPrincipal lawyerPrincipal) {

            List<Application> applicationList = appointmentService.getMyAppointmentApplicationList(lawyerPrincipal.getId());

            // dto 만들고 응답하기
            List<GetMyAppointmentApplicationListResponse.Data.ApplicationDto> applicationDtoList = new ArrayList<>();
            for(Application application : applicationList) {
                // 태그 리스트는 따로 만들기
                List<Long> tags = new ArrayList<>();
                for(ApplicationTag applicationTag : application.getTags()) {
                    tags.add(applicationTag.getTag().getId());
                }

                GetMyAppointmentApplicationListResponse.Data.ApplicationDto applicationDto = GetMyAppointmentApplicationListResponse.Data.ApplicationDto.builder()
                        .applicationId(application.getId())
                        .clientId(application.getClient().getId())
                        .title(application.getTitle())
                        .summary(application.getSummary())
                        .content(application.getContent())
                        .outcome(application.getOutcome())
                        .disadvantage(application.getDisadvantage())
                        .recommendedQuestions(application.getRecommendedQuestion())
                        .isCompleted(application.isCompleted())
                        .createdAt(application.getCreatedAt())
                        .tags(tags)
                        .build();

                applicationDtoList.add(applicationDto);
            }

            // 응답하기
            GetMyAppointmentApplicationListResponse getMyAppointmentApplicationListResponse = GetMyAppointmentApplicationListResponse.builder()
                    .success(true)
                    .message("[AppointmentController - 001] 내 상담 내역에 대한 상담신청서 목록 전체조회 성공")
                    .data(GetMyAppointmentApplicationListResponse.Data.builder().applicationList(applicationDtoList).build())
                    .build();

            return ResponseEntity.status(HttpStatus.OK).body(getMyAppointmentApplicationListResponse);

        } else {
            GetMyAppointmentApplicationListResponse getMyAppointmentApplicationListResponse = GetMyAppointmentApplicationListResponse.builder()
                    .success(false)
                    .message("[AppointmentController - 002] 변호사만 이용할 수 있는 기능입니다.")
                    .build();

            return ResponseEntity.status(HttpStatus.FORBIDDEN).body(getMyAppointmentApplicationListResponse);
        }
    }
}
