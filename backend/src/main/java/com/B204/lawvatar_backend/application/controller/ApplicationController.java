package com.B204.lawvatar_backend.application.controller;

import com.B204.lawvatar_backend.application.dto.*;
import com.B204.lawvatar_backend.application.entity.Application;
import com.B204.lawvatar_backend.application.entity.ApplicationTag;
import com.B204.lawvatar_backend.application.service.ApplicationService;
import com.B204.lawvatar_backend.appointment.entity.Appointment;
import com.B204.lawvatar_backend.appointment.repository.AppointmentRepository;
import com.B204.lawvatar_backend.common.principal.ClientPrincipal;
import com.B204.lawvatar_backend.common.principal.LawyerPrincipal;
import com.B204.lawvatar_backend.user.client.repository.ClientRepository;
import com.B204.lawvatar_backend.user.lawyer.repository.LawyerRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

import java.util.ArrayList;
import java.util.List;

@RestController
@RequestMapping("/api/applications")
@RequiredArgsConstructor
public class ApplicationController {

    // Field
    private final ApplicationService applicationService;
    private final AppointmentRepository appointmentRepository;
    private final LawyerRepository lawyerRepository;
    private final ClientRepository clientRepository;

    // Method
    /**
     * 의뢰인이 AI 파트를 통해서 상담경위서나 상담신청서를 작성한 후 DB에 저장할 때 호출되는 메서드
     * @param isCompleted   true=상담신청서 생성, false=상담경위서 생성
     * @param request 상담신청서 내용이 담긴 요청 json
     * @return 상담신청서 저장 결과를 응답
     */
    @PostMapping
    // 이 메서드의 isCompleted 쿼리 스트링은 true/false로만 분기처리할 거라서 그냥 boolean으로 받음
    public ResponseEntity<AddApplicationResponse> addApplicaiton(
            Authentication authentication,
            @RequestParam boolean isCompleted,
            @RequestBody AddApplicationRequest request) {

        // Principal 객체 얻기
        Object principal = authentication.getPrincipal();

        // Principal 객체 의뢰인인지 검사하고 맞으면 비즈니스 로직 진행, 아니면 에러 응답
        if(principal instanceof ClientPrincipal clientPrincipal) {
            // 상담신청서 Service에 가서 상담신청서 DB에 저장하고 id값 리턴받기
            Long applicationId = applicationService.addApplication(clientPrincipal.getId(), isCompleted, request);

            // 응답 dto 만들고 응답
            AddApplicationResponse addApplicationResponse = AddApplicationResponse.builder().applicationId(applicationId).build();

            return ResponseEntity.status(HttpStatus.OK).body(addApplicationResponse);
        } else {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "변호사는 이용할 수 없는 기능입니다.");
        }
    }

    /**
     * 의뢰인이 자신의 상담신청서 목록을 전체조회할 때 호출되는 메서드
     * @param isCompleted   false=상담경위서만 조회, true=상담신청서만 조회, null=전부 조회
     * @return  상담신청서 목록조회 결과를 응답
     */
    @GetMapping("/me")
    // isCompleted를 아예 붙이지 않는 경우까지 고려하기 때문에, required 속성값 false로 주고, Boolean 래퍼 객체로 받음
    public ResponseEntity<List<GetMyApplicationListResponse>> getMyApplicationList(Authentication authentication, @RequestParam(required = false) Boolean isCompleted) {

        // Principal 객체얻기
        Object principal = authentication.getPrincipal();

        // 요청한 사용자가 의뢰인인지 검사하고 맞다면 비즈니스 로직 진행, 아니면 에러 응답
        if (principal instanceof ClientPrincipal clientPrincipal) {

            // 의뢰인이 맞다면 자신의 상담경위서 or 신청서 전체조회
            List<Application> applicationList = applicationService.getMyApplicationList(clientPrincipal.getId(), isCompleted);

            // 서비스에서 응답받은 상담신청서 목록을 DTO 배열로 변환해서 저장할 List 객체 선언
            List<GetMyApplicationListResponse> result = new ArrayList<>();

            // application 목록 dto로 변환하고 응답
            for(Application application : applicationList) {
                GetMyApplicationListResponse getMyApplicationResponse = GetMyApplicationListResponse.builder()
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

                result.add(getMyApplicationResponse);
            }

            return ResponseEntity.status(HttpStatus.OK).body(result);
        } else {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "의뢰인만 사용 가능한 기능입니다.");
        }
    }

    /**
     * 상담신청서를 상세조회할 때 호출되는 메서드
     * @param applicationId 상세조회할 상담신청서의 고유번호
     * @return 상담신청서 상세조회 결과를 응답
     */
    @GetMapping("/{applicationId}")
    public ResponseEntity<GetApplicationResponse> getApplication(Authentication authentication, @PathVariable Long applicationId) throws Exception {

        // Principal 객체얻기
        Object principal = authentication.getPrincipal();

        // 요청한 사용자가 의뢰인이면 본인이 작성한 상담신청서일 때만 조회 가능하도록 하기
        if (principal instanceof ClientPrincipal clientPrincipal) {

            // Path Variable로 넘어온 applicationId로 상담신청서 객체 조회
            Application application = applicationService.getApplication(applicationId);

            // 조회한 상담신청서의 작성자가 본인이 아니라면 403 Forbidden 에러 발생
            if(!clientPrincipal.getId().equals(application.getClient().getId())) {
                return ResponseEntity.status(HttpStatus.FORBIDDEN).build();
            }

            // 응답 dto 만들고 응답완료
            // 태그 리스트는 따로 만들기
            List<Long> tags = new ArrayList<>();
            List<ApplicationTag> applicationTagList = application.getTags();
            for(ApplicationTag applicationTag : applicationTagList) {
                tags.add(applicationTag.getTag().getId());
            }

            // 응답 dto 만들기
            GetApplicationResponse applicationResponse = GetApplicationResponse.builder()
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

            return ResponseEntity.status(HttpStatus.OK).body(applicationResponse);

        } else if(principal instanceof LawyerPrincipal lawyerPrincipal){ // 요청한 사용자가 변호사이면 본인이 담당한 상담에 대한 상담신청서일 때만 조회 가능하도록 하기

            // Path Variable로 넘어온 applicationId로 상담신청서 객체 조회
            Application application = applicationService.getApplication(applicationId);

            // 조회한 상담신청서로 이루어진 상담 중 단 하나라도 자신이 담당 변호사가 아니라면 403 Forbidden 에러 발생
            List<Appointment> appointmentList = appointmentRepository.findByApplicationId(applicationId);
            for(Appointment appointment : appointmentList) {
                if(lawyerPrincipal.getId().equals(appointment.getLawyer().getId())) {
                    break;
                }
                throw new ResponseStatusException(HttpStatus.FORBIDDEN, "[ApplicationController - 001] 맡아서 진행한 상담의 신청서만 열람할 수 있습니다.");
            }

            // 응답 dto 만들고 응답완료
            // 태그 리스트는 따로 만들기
            List<Long> tags = new ArrayList<>();
            List<ApplicationTag> applicationTagList = application.getTags();
            for(ApplicationTag applicationTag : applicationTagList) {
                tags.add(applicationTag.getTag().getId());
            }

            //응답 dto 만들기
            GetApplicationResponse applicationResponse = GetApplicationResponse.builder()
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

            return ResponseEntity.status(HttpStatus.OK).body(applicationResponse);

        } else {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "[ApplicationController - 002] 유효하지 않은 Principal 입니다.");
        }
    }

    // 프론트가 AI 파트와 직접 소통한다면 4-1-4 요청은 필요없는 것으로 판단되어서 로직 삭제하였습니다.
    // 상담신청서 다운로드 api는 개발 후순위여서 나중에 만들겠습니다.
}
