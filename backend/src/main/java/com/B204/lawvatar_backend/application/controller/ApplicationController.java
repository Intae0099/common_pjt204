package com.B204.lawvatar_backend.application.controller;

import com.B204.lawvatar_backend.application.dto.*;
import com.B204.lawvatar_backend.application.entity.Application;
import com.B204.lawvatar_backend.application.service.ApplicationService;
import com.B204.lawvatar_backend.user.client.entity.Client;
import lombok.RequiredArgsConstructor;
import org.apache.coyote.Response;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@RestController
@RequestMapping("/api/applications")
@RequiredArgsConstructor
public class ApplicationController {

    // Field
    private final ApplicationService applicationService;

    // Method
    /**
     * 의뢰인이 상담경위서나 상담신청서를 저장할 때 호출되는 메서드
     * @param isCompleted true면 상담신청서 생성, false면 상담경위서 생성
     * @param request 상담신청서 내용이 담긴 요청 json
     * @return 상담신청서 저장 결과를 응답
     */
    @PostMapping
    // 이 메서드의 isCompleted 쿼리 스트링은 true/false로만 분기처리할 거라서 그냥 boolean으로 받음
    public ResponseEntity<AddApplicationResponse> addApplicaiton(@RequestParam boolean isCompleted, @RequestBody AddApplicationRequest request) {

        Long applicationId = applicationService.addApplication(1L, isCompleted, request); // 하드코딩

        AddApplicationResponse addApplicationResponse = AddApplicationResponse.builder().applicationId(applicationId).build();

        return ResponseEntity.status(HttpStatus.OK).body(addApplicationResponse);
    }

    /**
     * 의뢰인이 자신의 상담신청서 목록을 조회할 때 호출되는 메서드
     * @param isCompleted false면 상담경위서만, true면 상담신청서만, null이면 전부 조회
     * @return 상담신청서 목록조회 결과를 응답
     */
    @GetMapping("/me")
    public ResponseEntity<List<GetMyApplicationListResponse>> getMyApplicationList(@RequestParam(required = false) Boolean isCompleted) {

        // 하드코딩
        Client client = new Client(1L, "김싸피", "ssafy123@naver.com", "kakao", "kakao_dfdf522");

        List<Application> applicationList = applicationService.getMyApplicationList(client.getId(), isCompleted);
        List<GetMyApplicationListResponse> result = new ArrayList<>();

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
                    .tags(application.getTags())
                    .build();

            result.add(getMyApplicationResponse);
        }

        return ResponseEntity.status(HttpStatus.OK).body(result);
    }

    /**
     * 의뢰인이 상담신청서를 상세조회할 때 호출되는 메서드
     * @param applicationId 상세조회할 상담신청서의 고유번호
     * @return 상담신청서 상세조회 결과를 응답
     */
    @GetMapping("/{applicationId}")
    public ResponseEntity<GetApplicationResponse> getApplication(@PathVariable Long applicationId) {

        Application application = applicationService.getApplication(applicationId);
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
                .tags(application.getTags())
                .build();

        return ResponseEntity.status(HttpStatus.OK).body(applicationResponse);
    }

    /**
     * 의뢰인이 상담신청서를 마저 작성할 때 보내는 요청
     * @param applicationId 마저 작성할 상담신청서의 고유번호
     * @param request 수정할 내역이 담긴 요청 json
     * @return 수정 결과를 응답
     */
    @PatchMapping("/{applicationId}")
    public ResponseEntity<Void> modifyApplication(@PathVariable Long applicationId, @RequestBody ModifyApplicationRequest request) {

        applicationService.modifyApplication(applicationId, request);

        return ResponseEntity.status(HttpStatus.OK).build();
    }

    // 상담신청서 다운로드 api는 개발 후순위여서 나중에 만들겠습니다.
}
