package com.B204.ALaw.application.service;

import com.B204.ALaw.application.dto.AddApplicationRequest;
import com.B204.ALaw.application.dto.ModifyApplicationRequest;
import com.B204.ALaw.application.entity.Application;
import com.B204.ALaw.application.entity.ApplicationTag;
import com.B204.ALaw.application.repository.ApplicationRepository;
import com.B204.ALaw.application.repository.ApplicationTagRepository;
import com.B204.ALaw.appointment.entity.Appointment;
import com.B204.ALaw.appointment.repository.AppointmentRepository;
import com.B204.ALaw.common.tag.entity.Tag;
import com.B204.ALaw.common.tag.repository.TagRepository;
import com.B204.ALaw.user.client.entity.Client;

import com.B204.ALaw.user.client.repository.ClientRepository;
import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.NoSuchElementException;

@Service
@RequiredArgsConstructor
@Transactional
public class ApplicationService {

    // Field
    private final ApplicationRepository applicationRepository;
    private final ApplicationTagRepository applicationTagRepository;
    private final ClientRepository clientRepository;
    private final AppointmentRepository appointmentRepository;
    private final TagRepository tagRepository;

    // Method
    /**
     * @param clientId  상담신청서를 작성한 의뢰인 DB 고유번호
     * @param isCompleted   false=상담경위서 저장 / true=상담신청서 저장
     * @param request   상담신청서가 담겨져 있는 DTO
     * @return  저장한 상담신청서의 DB 고유번호
     */
    public Long addApplication(Long clientId, boolean isCompleted, AddApplicationRequest request) {

        // Application 객체 만들고 DB에 저장하기 위해 Client 객체 가져오기
        Client client = clientRepository.findById(clientId).orElseThrow(() -> new NoSuchElementException("[ApplicationService - 001] 해당 ID 값을 가지는 Client가 없습니다."));

        if (isCompleted) { // isCompleted가 true이면 Application 필드 꽉 채워서 상담신청서 저장
            // Application 객체 만들고 저장
            Application application = Application.builder()
                    .client(client)
                    .title(request.getTitle())
                    .summary(request.getSummary())
                    .content(request.getContent())
                    .outcome(request.getOutcome())
                    .disadvantage(request.getDisadvantage())
                    .recommendedQuestion(request.getRecommendedQuestion())
                    .isCompleted(true)
                    .createdAt(LocalDateTime.now())
                    .build();

            applicationRepository.save(application);

            // 태그는 별도로 ApplicationTagRepository 사용해서 저장
            List<Long> tags = request.getTags();
            for (Long tagId : tags) {
                // ApplicationTag 객체 만들어서 DB에 저장하기 위해 Tag 객체 가져오기
                Tag tag = tagRepository.findById(tagId).orElseThrow(() -> new NoSuchElementException("[ApplicationService - 002] 해당 ID 값을 가지는 Tag가 없습니다."));

                // ApplicationTag 객체 만들고 저장
                ApplicationTag applicationTag = ApplicationTag.builder().application(application).tag(tag).build();
                applicationTagRepository.save(applicationTag);
            }

            return application.getId();

        } else { // isCompleted가 false이면 Application 필드 상담경위서 부분만 채워서 저장

            // Application 객체 만들고 저장
            Application application = Application.builder()
                    .client(client)
                    .title(request.getTitle())
                    .summary(request.getSummary())
                    .content(request.getContent())
                    .outcome(request.getOutcome())
                    .createdAt(LocalDateTime.now())
                    .build();

            applicationRepository.save(application);

            // 상담경위서에는 아직 태그가 안달려있으므로 태그 저장은 안해도 됨

            return application.getId();
        }
    }

    /**
     * @param clientId 상담신청서 목록 전체조회하려는 의뢰인의 DB 고유번호
     * @param isCompleted true=상담신청서만 전체조회, false=상담경위서만 전체조회, null=상담경위서 or 신청서 모두 전체조회
     * @return 조회한 상담신청서 목록 반환
     */
    public List<Application> getMyApplicationList(Long clientId, Boolean isCompleted) {
        if (isCompleted == null) {
            return applicationRepository.findByClientId(clientId);
        } else if (isCompleted) {
            return applicationRepository.findByClientIdAndIsCompletedTrue(clientId);
        } else {
            return applicationRepository.findByClientIdAndIsCompletedFalse(clientId);
        }
    }

    /**
     * @param applicationId 조회하고자 하는 상담신청서 DB 고유번호
     * @return 조회한 상담신청서 객체 반환
     */
    public Application getApplication(Long applicationId, String userType, Long userId) throws Exception {

        if(userType.equals("CLIENT")) {

            // 일단 상담신청서 조회
            Application application = applicationRepository.findById(applicationId).orElseThrow(() -> new NoSuchElementException("[ApplicationService - 003] 해당 ID 값을 가지는 Application이 없습니다."));

            // 가져온 상담신청서 작성자가 본인이 아니라면 SecurityException 발생
            if(!application.getClient().getId().equals(userId)) {
                throw new SecurityException("[ApplicationService - 004] 자신이 작성한 신청서만 열람할 수 있습니다.");
            }

            // 그게 아니라면 아까 조회한 상담신청서 반환
            return application;

        } else if(userType.equals("LAWYER")) {

            // 이 상담신청서로 이루어진 상담 목록 전체조회
            List<Appointment> appointmentList = appointmentRepository.findByApplicationId(applicationId);

            // 조회한 상담 목록 중 이 변호사가 진행한 상담이 하나라도 있는지 조사해서 없다면 에러 발생
            boolean isThisApplicationAccessibleByLawyer = false; // 플래그 변수: 상담 리스트 중 하나라도 현재 요청보낸 변호사가 맡았다면 true가 됨
            for(Appointment appointment : appointmentList) {
                if(userId.equals(appointment.getLawyer().getId())) {
                    isThisApplicationAccessibleByLawyer = true;
                    break;
                }
            }
            
            if(!isThisApplicationAccessibleByLawyer) {
                throw new SecurityException("[ApplicationController - 005] 자신이 맡아서 진행한 상담의 신청서만 열람할 수 있습니다.");
            }

            // 에러 발생하지 않았다면 Application 조회해서 반환
            Application application = applicationRepository.findById(applicationId).orElseThrow(() -> new NoSuchElementException("[ApplicationService - 006 해당 ID 값을 가지는 Application이 없습니다."));

            return application;
        }

        throw new IllegalStateException("[ApplicationService - 007] 알 수 없는 에러가 발생했습니다. 관리자에게 문의하세요.");
    }

    public void modifyApplication(Long applicationId, ModifyApplicationRequest request, Long clientId, boolean isCompleted) throws Exception {

        // application 객체 얻기
        Application application = applicationRepository.findById(applicationId).orElseThrow(() -> new NoSuchElementException("[ApplicationService - 008] 해당 ID 값을 가지는 Appointment가 없습니다."));

        // 본인이 작성하지 않은 신청서에 대해 수정요청한 경우 에러 응답
        if(!clientId.equals(application.getClient().getId())) {
            throw new SecurityException("[ApplicationService - 00] 본인이 작성한 신청서만 수정할 수 있습니다.");
        }

        application.setCompleted(isCompleted);

        // null이 아닌 필드만 application에 반영
        if(request.getTitle() != null) {
            application.setTitle(request.getTitle());
        }

        if(request.getSummary() != null) {
            application.setSummary(request.getSummary());
        }

        if(request.getContent() != null) {
            application.setContent(request.getContent());
        }

        if(request.getOutcome() != null) {
            application.setOutcome(request.getOutcome());
        }

        if(request.getDisadvantage() != null) {
            application.setDisadvantage(request.getDisadvantage());
        }

        if(request.getRecommendedQuestion() != null) {
            application.setRecommendedQuestion(request.getRecommendedQuestion());
        }

        if(request.getTags() != null) {
            // application_tag 테이블에서 기존 것 전부 삭제
            List<ApplicationTag> applicationTagList = applicationTagRepository.findByApplicationId(applicationId);
            for(ApplicationTag applicationTag : applicationTagList) {
                applicationTagRepository.delete(applicationTag);
            }

            // 새로운 것 전부 insert
            for(Long tagId : request.getTags()) {
                Tag tag = tagRepository.findById(tagId).orElseThrow(() -> new NoSuchElementException("[ApplicationService - 00] 해당 ID 값을 가지는 Tag가 없습니다."));
                ApplicationTag applicationTag = ApplicationTag.builder().application(application).tag(tag).build();
                applicationTagRepository.save(applicationTag);
            }
        }
    }
}
