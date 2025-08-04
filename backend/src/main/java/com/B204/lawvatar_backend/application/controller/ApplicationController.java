package com.B204.lawvatar_backend.application.controller;

import com.B204.lawvatar_backend.application.dto.*;
import com.B204.lawvatar_backend.application.entity.Application;
import com.B204.lawvatar_backend.application.entity.ApplicationTag;
import com.B204.lawvatar_backend.application.repository.ApplicationRepository;
import com.B204.lawvatar_backend.application.service.ApplicationService;
import com.B204.lawvatar_backend.appointment.entity.Appointment;
import com.B204.lawvatar_backend.appointment.repository.AppointmentRepository;
import com.B204.lawvatar_backend.common.principal.ClientPrincipal;
import com.B204.lawvatar_backend.common.principal.LawyerPrincipal;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

import java.util.ArrayList;
import java.util.List;
import java.util.NoSuchElementException;

@RestController
@RequestMapping("/api/applications")
@RequiredArgsConstructor
public class ApplicationController {

    // Field
    private final ApplicationService applicationService;

    // Method
    /**
     * 의뢰인이 AI 파트를 통해서 상담경위서나 상담신청서를 작성한 후 DB에 저장할 때 호출되는 메서드
     * @param isCompleted   true=상담신청서 생성, false=상담경위서 생성
     * @param request 상담신청서 내용이 담긴 요청 json
     * @return 상담신청서 저장 결과를 응답
     */
    @PostMapping
    // 이 메서드의 isCompleted 쿼리 스트링은 true/false로만 분기처리할 거라서 그냥 boolean으로 받음
    public ResponseEntity<AddApplicationResponse> addApplicaiton (
            Authentication authentication,
            @RequestParam boolean isCompleted,
            @RequestBody AddApplicationRequest request) throws Exception {

        // Principal 객체 얻기
        Object principal = authentication.getPrincipal();

        // Principal 객체 의뢰인인지 검사하고 맞으면 비즈니스 로직 진행, 아니면 에러 응답
        if(principal instanceof ClientPrincipal clientPrincipal) {
            // 상담신청서 Service에 가서 상담신청서 DB에 저장하고 id값 리턴받기
            Long applicationId = null;
            try {
                applicationId = applicationService.addApplication(clientPrincipal.getId(), isCompleted, request);
            } catch (NoSuchElementException e) {
                AddApplicationResponse addApplicationResponse = AddApplicationResponse.builder()
                        .success(false)
                        .message(e.getMessage())
                        .build();

                return ResponseEntity.status(HttpStatus.NOT_FOUND).body(addApplicationResponse);
            }

            // 응답 dto 만들고 응답
            AddApplicationResponse addApplicationResponse = AddApplicationResponse.builder()
                    .success(true)
                    .message("[ApplicationController - 001] 상담경위서(신청서) 저장 성공")
                    .data(AddApplicationResponse.Data.builder().applicationId(applicationId).build())
                    .build();

            return ResponseEntity.status(HttpStatus.OK).body(addApplicationResponse);

        } else {
            AddApplicationResponse addApplicationResponse = AddApplicationResponse.builder()
                    .success(false)
                    .message("[ApplicationController - 002] 변호사는 이용할 수 없는 기능입니다.")
                    .build();

            return ResponseEntity.status(HttpStatus.FORBIDDEN).body(addApplicationResponse);
        }
    }

    /**
     * 의뢰인이 자신의 상담신청서 목록을 전체조회할 때 호출되는 메서드
     * @param isCompleted   false=상담경위서만 조회, true=상담신청서만 조회, null=전부 조회
     * @return  상담신청서 목록조회 결과를 응답
     */
    @GetMapping("/me")
    // isCompleted를 아예 붙이지 않는 경우까지 고려하기 때문에, required 속성값 false로 주고, Boolean 래퍼 객체로 받음
    public ResponseEntity<GetMyApplicationListResponse> getMyApplicationList(Authentication authentication, @RequestParam(required = false) Boolean isCompleted) throws Exception {

        // Principal 객체얻기
        Object principal = authentication.getPrincipal();

        // 요청한 사용자가 의뢰인인지 검사하고 맞다면 비즈니스 로직 진행, 아니면 에러 응답
        if (principal instanceof ClientPrincipal clientPrincipal) {

            // 의뢰인이 맞다면 자신의 상담경위서 or 신청서 전체조회
            List<Application> applicationList = applicationService.getMyApplicationList(clientPrincipal.getId(), isCompleted);

            // 반환할 DTO 만들고 응답
            // 태그 목록은 따로 만들기
            List<Long> tags = new ArrayList<>();
            for(Application application : applicationList) {
                for(ApplicationTag applicationTag : application.getTags()) {
                    tags.add(applicationTag.getTag().getId());
                }
            }

            // application 목록 dto로 변환하고 응답
            List<GetMyApplicationListResponse.Data.ApplicationDto> result = new ArrayList<>();

            for(Application application : applicationList) {
                GetMyApplicationListResponse.Data.ApplicationDto applicationDto = GetMyApplicationListResponse.Data.ApplicationDto.builder()
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

                result.add(applicationDto);
            }

            GetMyApplicationListResponse getMyApplicationResponse = GetMyApplicationListResponse.builder()
                    .success(true)
                    .message("[ApplicationController - 003] 의뢰인 상담경위서(신청서) 목록 전체조회 성공")
                    .data(GetMyApplicationListResponse.Data.builder()
                            .applicationList(result)
                            .build())
                    .build();

            return ResponseEntity.status(HttpStatus.OK).body(getMyApplicationResponse);
        } else {
            GetMyApplicationListResponse getMyApplicationListResponse = GetMyApplicationListResponse.builder()
                    .success(false)
                    .message("[ApplicationController - 004] 의뢰인만 사용 가능한 기능입니다.")
                    .build();

            return ResponseEntity.status(HttpStatus.FORBIDDEN).body(getMyApplicationListResponse);
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

            try{
                Application application = applicationService.getApplication(applicationId, "CLIENT", clientPrincipal.getId());

                // 응답 dto 만들고 응답하기
                // 태그 리스트는 따로 만들기
                List<Long> tags = new ArrayList<>();
                List<ApplicationTag> applicationTagList = application.getTags();
                for(ApplicationTag applicationTag : applicationTagList) {
                    tags.add(applicationTag.getTag().getId());
                }

                // Application 내용 dto 만들기
                GetApplicationResponse.Data.ApplicationDto applicationDto = GetApplicationResponse.Data.ApplicationDto.builder()
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

                // 표준 응답 dto 만들어서 응답
                GetApplicationResponse applicationResponse = GetApplicationResponse.builder()
                        .success(true)
                        .message("[ApplicationController - 005] 상담경위서(신청서) 조회 성공")
                        .data(GetApplicationResponse.Data.builder().applicationDto(applicationDto).build())
                        .build();

                return ResponseEntity.status(HttpStatus.OK).body(applicationResponse);
            } catch(SecurityException e) {
                GetApplicationResponse getApplicationResponse = GetApplicationResponse.builder()
                        .success(false)
                        .message(e.getMessage())
                        .build();

                return ResponseEntity.status(HttpStatus.FORBIDDEN).body(getApplicationResponse);
            } catch(NoSuchElementException e) {
                GetApplicationResponse getApplicationResponse = GetApplicationResponse.builder()
                        .success(false)
                        .message(e.getMessage())
                        .build();

                return ResponseEntity.status(HttpStatus.NOT_FOUND).body(getApplicationResponse);
            } catch(IllegalStateException e) {
                GetApplicationResponse getApplicationResponse = GetApplicationResponse.builder()
                        .success(false)
                        .message(e.getMessage())
                        .build();

                return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(getApplicationResponse);
            }

        } else if(principal instanceof LawyerPrincipal lawyerPrincipal){ // 요청한 사용자가 변호사이면 본인이 담당한 상담에 대한 상담신청서일 때만 조회 가능하도록 하기

            try {
                Application application = applicationService.getApplication(applicationId, "LAWYER", lawyerPrincipal.getId());

                // 응답 dto 만들고 응답하기
                // 태그 리스트는 따로 만들기
                List<Long> tags = new ArrayList<>();
                List<ApplicationTag> applicationTagList = application.getTags();
                for(ApplicationTag applicationTag : applicationTagList) {
                    tags.add(applicationTag.getTag().getId());
                }

                // Application 내용 dto 만들기
                GetApplicationResponse.Data.ApplicationDto applicationDto = GetApplicationResponse.Data.ApplicationDto.builder()
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
                
                // 표준 응답 dto 만들어서 응답
                GetApplicationResponse applicationResponse = GetApplicationResponse.builder()
                        .success(true)
                        .message("[ApplicationController - 006] 상담경위서(신청서) 조회 성공")
                        .data(GetApplicationResponse.Data.builder().applicationDto(applicationDto).build())
                        .build();

                return ResponseEntity.status(HttpStatus.OK).body(applicationResponse);
            } catch (SecurityException e) {
                GetApplicationResponse getApplicationResponse = GetApplicationResponse.builder()
                        .success(false)
                        .message(e.getMessage())
                        .build();

                return ResponseEntity.status(HttpStatus.FORBIDDEN).body(getApplicationResponse);
            } catch(NoSuchElementException e) {
                GetApplicationResponse getApplicationResponse = GetApplicationResponse.builder()
                        .success(false)
                        .message(e.getMessage())
                        .build();

                return ResponseEntity.status(HttpStatus.NOT_FOUND).body(getApplicationResponse);
            } catch(IllegalStateException e) {
                GetApplicationResponse getApplicationResponse = GetApplicationResponse.builder()
                        .success(false)
                        .message(e.getMessage())
                        .build();

                return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(getApplicationResponse);
            }
        } else {
            GetApplicationResponse getApplicationResponse = GetApplicationResponse.builder()
                    .success(false)
                    .message("[ApplicationController - 007] 유효하지 않은 사용자입니다.")
                    .build();

            return ResponseEntity.status(HttpStatus.FORBIDDEN).body(getApplicationResponse);
        }
    }

    @PatchMapping("/{applicationId}")
    public ResponseEntity<ModifyApplicationResponse> modifyApplication(Authentication authentication, @PathVariable Long applicationId, ModifyApplicationRequest request) {

        // Principal 객체 얻기
        Object principal = authentication.getPrincipal();
        
        // 의뢰인이면 그대로 비즈니스 로직 진행, 아니면 에러 응답
        if(principal instanceof ClientPrincipal clientPrincipal) {
            try {
                applicationService.modifyApplication(applicationId, request);
            } catch(NoSuchElementException e) {
                ModifyApplicationResponse modifyApplicationResponse = ModifyApplicationResponse.builder()
                        .success(false)
                        .message(e.getMessage())
                        .build();

                return ResponseEntity.status(HttpStatus.NOT_FOUND).body(modifyApplicationResponse);
            } catch(SecurityException e) {
                ModifyApplicationResponse modifyApplicationResponse = ModifyApplicationResponse.builder()
                        .success(false)
                        .message(e.getMessage())
                        .build();

                return ResponseEntity.status(HttpStatus.FORBIDDEN).body(modifyApplicationResponse);
            }

            ModifyApplicationResponse modifyApplicationResponse = ModifyApplicationResponse.builder()
                    .success(true)
                    .message("[ApplicationController - 008] 상담신청서 수정 성공")
                    .data(ModifyApplicationResponse.Data.builder().applicationId(applicationId).build())
                    .build();

            return ResponseEntity.status(HttpStatus.OK).body(modifyApplicationResponse);
        } else if(principal instanceof LawyerPrincipal lawyerPrincipal){
            ModifyApplicationResponse modifyApplicationResponse = ModifyApplicationResponse.builder()
                    .success(false)
                    .message("[ApplicationController - 009] 의뢰인만 사용 가능한 기능입니다.")
                    .build();

            return ResponseEntity.status(HttpStatus.FORBIDDEN).body(modifyApplicationResponse);
        } else {
            ModifyApplicationResponse modifyApplicationResponse = ModifyApplicationResponse.builder()
                    .success(false)
                    .message("[ApplicationController - 010] 유효하지 않은 사용자입니다.")
                    .build();

            return ResponseEntity.status(HttpStatus.FORBIDDEN).body(modifyApplicationResponse);
        }
    }

    // 상담신청서 다운로드 api는 개발 후순위여서 나중에 만들겠습니다.
}
