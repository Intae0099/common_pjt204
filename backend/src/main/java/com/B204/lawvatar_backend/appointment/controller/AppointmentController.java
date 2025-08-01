package com.B204.lawvatar_backend.appointment.controller;

import com.B204.lawvatar_backend.application.entity.Application;
import com.B204.lawvatar_backend.application.entity.ApplicationTag;
import com.B204.lawvatar_backend.appointment.dto.GetMyAppointmentApplicationListResponse;
import com.B204.lawvatar_backend.appointment.service.AppointmentService;
import com.B204.lawvatar_backend.common.principal.LawyerPrincipal;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

import java.util.ArrayList;
import java.util.List;

@RestController
@RequestMapping("/api/appointments")
@RequiredArgsConstructor
public class AppointmentController {

    // Field
    private final AppointmentService appointmentService;

    // Method
    /**
     * 변호사가 자신의 상담에 대한 상담신청서 목록을 전체조회하는 메서드
     * @param authentication
     * @return
     */
    @GetMapping("/applications")
    public ResponseEntity<List<GetMyAppointmentApplicationListResponse>> getMyAppointmentApplicationList(Authentication authentication) {

        // Principal 객체 얻기
        Object principal = authentication.getPrincipal();

        // 변호사 맞는지 검사하고 맞으면 비즈니스 로직 진행, 아니면 에러 응답
        if(principal instanceof LawyerPrincipal lawyerPrincipal) {

            List<Application> applicationList = appointmentService.getMyAppointmentApplicationList(lawyerPrincipal.getId());

            // dto 만들고 응답
            // 서비스에서 응답받은 상담신청서 목록을 DTO 배열로 변환해서 저장할 List 객체 선언
            List<GetMyAppointmentApplicationListResponse> result = new ArrayList<>();

            // application 목록 dto로 변환하고 응답
            // 태그 리스트는 따로 만들기
            List<Long> tags = new ArrayList<>();
            for(Application application : applicationList) {
                for(ApplicationTag applicationTag : application.getTags()) {
                    tags.add(applicationTag.getTag().getId());
                }
            }

            // dto 만들기
            for(Application application : applicationList) {
                GetMyAppointmentApplicationListResponse getMyAppointmentApplicationListResponse = GetMyAppointmentApplicationListResponse.builder()
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

                result.add(getMyAppointmentApplicationListResponse);
            }

            return ResponseEntity.status(HttpStatus.OK).body(result);

        } else {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "변호사만 이용할 수 있는 기능입니다.");
        }
    }
}
