package com.B204.ALaw.appointment.service;

import com.B204.ALaw.application.entity.Application;
import com.B204.ALaw.application.repository.ApplicationRepository;
import com.B204.ALaw.appointment.entity.Appointment;
import com.B204.ALaw.appointment.entity.AppointmentStatus;
import com.B204.ALaw.appointment.repository.AppointmentRepository;
import com.B204.ALaw.user.client.repository.ClientRepository;
import com.B204.ALaw.user.lawyer.entity.UnavailabilitySlot;
import com.B204.ALaw.user.lawyer.repository.LawyerRepository;
import com.B204.ALaw.user.lawyer.repository.UnavailabilitySlotRepository;
import jakarta.validation.constraints.NotNull;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

@Service
@Transactional
public class AppointmentService {

  private final AppointmentRepository appointmentRepo;
  private final ClientRepository clientRepo;
  private final LawyerRepository lawyerRepo;
  private final ApplicationRepository applicationRepo;
  private final UnavailabilitySlotRepository slotRepo;

  public AppointmentService(
      AppointmentRepository appointmentRepo,
      ClientRepository clientRepo,
      LawyerRepository lawyerRepo,
      ApplicationRepository applicationRepo,
      UnavailabilitySlotRepository unavailabilitySlotRepository) {
    this.appointmentRepo = appointmentRepo;
    this.clientRepo = clientRepo;
    this.lawyerRepo = lawyerRepo;
    this.applicationRepo = applicationRepo;
    this.slotRepo = unavailabilitySlotRepository;
  }

  public Appointment create(
      Long clientId,
      @NotNull Long lawyerId,
      @NotNull Long applicationId,
      @NotNull LocalDateTime start,
      @NotNull LocalDateTime end) {

    var client = clientRepo.findById(clientId)
        .orElseThrow(() -> new IllegalArgumentException("Client not found : " + clientId));
    var lawyer = lawyerRepo.findById(lawyerId)
        .orElseThrow(() -> new IllegalArgumentException("Lawyer not found : " + lawyerId));
    var application = applicationRepo.findById(applicationId)
        .orElseThrow(() -> new IllegalArgumentException("Application not Found : " + applicationId));

    Appointment appt = new Appointment();
    appt.setClient(client);
    appt.setLawyer(lawyer);
    appt.setApplication(application);
    appt.setAppointmentStatus(AppointmentStatus.PENDING);
    appt.setStartTime(start);
    appt.setEndTime(end);
    appt.setCreatedAt(LocalDateTime.now());

    return appointmentRepo.save(appt);
  }

  public void updateStatus(Long appointmentId, Long lawyerId, @NotNull AppointmentStatus newStatus) {
    Appointment appt = appointmentRepo.findById(appointmentId)
        .orElseThrow(() ->
            new ResponseStatusException(HttpStatus.NOT_FOUND, "예약을 찾을 수 없습니다. id=" + appointmentId));

    // 1) 변호사 할당 여부 확인
    if (!appt.getLawyer().getId().equals(lawyerId)) {
      throw new ResponseStatusException(HttpStatus.FORBIDDEN, "자신에게 할당된 예약만 처리할 수 있습니다.");
    }

    // 2) 상태 전환 가능성 체크
    if (appt.getAppointmentStatus() != AppointmentStatus.PENDING) {
      throw new ResponseStatusException(HttpStatus.CONFLICT,
          "이미 처리된 예약입니다. 현재 상태=" + appt.getAppointmentStatus());
    }
    if (newStatus != AppointmentStatus.CONFIRMED && newStatus != AppointmentStatus.REJECTED) {
      throw new ResponseStatusException(HttpStatus.BAD_REQUEST,
          "수락 혹은 거절만 선택할 수 있습니다.");
    }

    // 3) 상태 업데이트
    appt.setAppointmentStatus(newStatus);

    if(newStatus == AppointmentStatus.CONFIRMED){
      UnavailabilitySlot slot = new UnavailabilitySlot();
      slot.setLawyer(appt.getLawyer());
      slot.setStartTime(appt.getStartTime());  // Appointment에 startTime 필드가 있다고 가정
      slot.setEndTime(appt.getEndTime());      // Appointment에 endTime 필드가 있다고 가정
      slotRepo.save(slot);
    }
  }

  public void cancel(Long appointmentId, Long clientId) {
    Appointment appt = appointmentRepo.findById(appointmentId)
        .orElseThrow(() ->
            new ResponseStatusException(HttpStatus.NOT_FOUND, "예약을 찾을 수 없습니다. id=" + appointmentId));

    // 1) 본인 신청인지 확인
    if (!appt.getClient().getId().equals(clientId)) {
      throw new ResponseStatusException(HttpStatus.FORBIDDEN, "본인이 신청한 예약만 취소할 수 있습니다.");
    }

    // 2) 승인된 상태인지 확인
    if (appt.getAppointmentStatus() != AppointmentStatus.CONFIRMED) {
      throw new ResponseStatusException(HttpStatus.CONFLICT,
          "승인된 상태에서만 취소할 수 있습니다. 현재 상태=" + appt.getAppointmentStatus());
    }

    // 3) 상태를 CANCELED 로 변경 (AppointmentStatus에 CANCELED 값이 있어야 함)
    appt.setAppointmentStatus(AppointmentStatus.CANCELLED);

    LocalDateTime start = appt.getStartTime();
    LocalDateTime end = appt.getEndTime();
    Long lawyerId = appt.getLawyer().getId();

    // 미리 정의해 둔 메서드 사용 (아래 예시처럼 리포에 추가)
    slotRepo.deleteByLawyerIdAndStartTimeAndEndTime(lawyerId, start, end);
  }

  public List<Application> getMyAppointmentApplicationList(Long lawyerId) {

    List<Appointment> appointmentList = appointmentRepo.findByLawyerId(lawyerId);
    List<Application> applicationList = new ArrayList<>();
    for(Appointment appointment : appointmentList) {
        applicationList.add(appointment.getApplication());
    }
    return applicationList;
  }
}
