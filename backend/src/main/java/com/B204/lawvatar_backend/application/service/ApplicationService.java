package com.B204.lawvatar_backend.application.service;

import com.B204.lawvatar_backend.application.dto.AddApplicationRequest;
import com.B204.lawvatar_backend.application.dto.ModifyApplicationRequest;
import com.B204.lawvatar_backend.application.entity.Application;
import com.B204.lawvatar_backend.application.repository.ApplicationRepository;
import com.B204.lawvatar_backend.common.dto.ApplicationRequest;
import com.B204.lawvatar_backend.common.dto.ApplicationResponse;
import com.B204.lawvatar_backend.common.dto.StructuringRequest;
import com.B204.lawvatar_backend.common.dto.StructuringResponse;
import com.B204.lawvatar_backend.user.client.entity.Client;

import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.time.LocalDateTime;
import java.util.List;

@Service
@RequiredArgsConstructor
@Transactional
public class ApplicationService {

    // Field
    private final ApplicationRepository applicationRepository;
    private final RestTemplate restTemplate;

    private final String AIBaseUrl = "https://api.legal.ai/v1";

    // Method
    /**
     * 상담신청서 또는 상담경위서 생성 및 저장
     * @param clientId
     * @param isCompleted
     * @param request
     * @return
     */
    public Long addApplication(Long clientId, boolean isCompleted, AddApplicationRequest request) {

        // 하드코딩
        Client client = new Client(1L, "김싸피", "ssafy123@naver.com", "kakao", "kakao_dfdf522");

        if(isCompleted) {
            // [AI] 3-3. 상담신청서 생성 요청보내기
            // 요청 url 만들기
            String url = AIBaseUrl + "/api/consult/application";

            // 헤더 만들기
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);

            // 본문 만들기
            ApplicationRequest requestBody = ApplicationRequest.builder()
                    .caseDto(ApplicationRequest.CaseDto.builder().title(request.getTitle()).summary(request.getSummary()).fullText(request.getContent()).build())
                    .desiredOutcome(request.getOutcome())
                    .weakPoints(request.getDisadvantage())
                    .build();

            // HttpEntity 만들기
            HttpEntity<ApplicationRequest> requestEntity = new HttpEntity<>(requestBody, headers);

            // 요청 보내기
            ResponseEntity<ApplicationResponse> responseEntity = restTemplate.postForEntity(url, requestEntity, ApplicationResponse.class);
            ApplicationResponse applicationResponse = responseEntity.getBody();

            // Application 객체 만들기
            Application application = Application.builder()
                    .client(client)
                    .title(applicationResponse.getData().getApplication().getData().getCaseDto().getTitle())
                    .summary(applicationResponse.getData().getApplication().getData().getCaseDto().getSummary())
                    .content(applicationResponse.getData().getApplication().getData().getCaseDto().getFullText())
                    .outcome(applicationResponse.getData().getApplication().getDesiredOutcome())
                    .disadvantage(applicationResponse.getData().getApplication().getWeakPoints())
                    .recommendedQuestion((applicationResponse.getData().getQuestions()))
                    .isCompleted(true)
                    .createdAt(LocalDateTime.now())
                    // AI api 명세서 상담 신청서 api에서 태그 바로 주는걸로 수정되면 여기서 태그도 필드에 넣어야 함
                    .build();

            // Application 객체 DB에 저장하기
            applicationRepository.save(application);

            // applicationId 리턴
            return application.getId();

        } else {
            // [AI] 3-1. 사건 내용 구조화 요청 보내기
            // 요청 url 만들기
            String url = AIBaseUrl + "api/cases/structuring";

            // 헤더 만들기
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);

            // 본문 만들기
            StructuringRequest requestBody = StructuringRequest.builder()
                    .freeText(request.getFullText())
                    .build();

            // HttpEntity 만들기
            HttpEntity<StructuringRequest> requestEntity = new HttpEntity<>(requestBody, headers);

            // 요청 보내기
            ResponseEntity<StructuringResponse> responseEntity = restTemplate.postForEntity(url, requestEntity, StructuringResponse.class);
            StructuringResponse structuringResponse = responseEntity.getBody();

            // Application 객체 만들기
            Application application = Application.builder()
                    .client(client)
                    .title(structuringResponse.getData().getCaseDto().getTitle())
                    .summary(structuringResponse.getData().getCaseDto().getSummary())
                    .content(structuringResponse.getData().getCaseDto().getFullText())
                    .createdAt(LocalDateTime.now())
                    .build();

            // Application 객체 DB에 저장하기
            applicationRepository.save(application);

            // applicationId 리턴
            return application.getId();
        }
    }

    /**
     * 상담신청서 목록 전체조회
     * @param clientId
     * @param isCompleted
     * @return
     */
    public List<Application> getMyApplicationList(Long clientId, Boolean isCompleted) {
        if(isCompleted == null) {
            return applicationRepository.findByClientId(clientId);
        } else if(isCompleted) {
            return applicationRepository.findByClientIdAndIsCompletedTrue(clientId);
        } else {
            return applicationRepository.findByClientIdAndIsCompletedFalse(clientId);
        }
    }

    /**
     * 상담신청서 상세조회
     * @param applicationId
     * @return
     */
    public Application getApplication(Long applicationId) {
        // null 처리 필요
        return applicationRepository.findById(applicationId).orElse(null);
    }

    /**
     * 상담신청서 이어서 작성 및 저장
     * @param applicationId
     * @param request
     */
    public void modifyApplication(Long applicationId, ModifyApplicationRequest request) {

        // 하드코딩
        Client client = new Client(1L, "김싸피", "ssafy123@naver.com", "kakao", "kakao_dfdf522");

        // 수정할 Application 데이터 찾기
        // null 처리 필요
        Application application = applicationRepository.findById(applicationId).orElse(null);

        // outcome 키값이 채워져 왔다면 set
        if(request.getOutcome() != null) {
            application.setOutcome(request.getOutcome());
        }

        // disadvantage 키값이 채워져 왔다면 set
        if(request.getDisadvantage() != null) {
            application.setDisadvantage(request.getDisadvantage());
        }

        // [AI] 3-3. 상담신청서 생성 요청보내기
        // 요청 url 만들기
        String url = AIBaseUrl + "/api/consult/application";

        // 헤더 만들기
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        // 본문 만들기
        ApplicationRequest requestBody = ApplicationRequest.builder()
                .caseDto(ApplicationRequest.CaseDto.builder().title(application.getTitle()).summary(application.getSummary()).fullText(application.getContent()).build())
                .desiredOutcome(application.getOutcome())
                .weakPoints(application.getDisadvantage())
                .build();

        // HttpEntity 만들기
        HttpEntity<ApplicationRequest> requestEntity = new HttpEntity<>(requestBody, headers);

        // 요청 보내기
        ResponseEntity<ApplicationResponse> responseEntity = restTemplate.postForEntity(url, requestEntity, ApplicationResponse.class);
        ApplicationResponse applicationResponse = responseEntity.getBody();

        // Application 객체 수정하기
        application.setOutcome(applicationResponse.getData().getApplication().getDesiredOutcome());
        application.setDisadvantage(applicationResponse.getData().getApplication().getWeakPoints());
        application.setRecommendedQuestion(applicationResponse.getData().getQuestions());
        application.setCompleted(true);
        application.setCreatedAt(LocalDateTime.now());

    }
}
