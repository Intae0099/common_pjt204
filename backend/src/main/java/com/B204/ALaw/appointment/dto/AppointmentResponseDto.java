package com.B204.ALaw.appointment.dto;


import com.B204.ALaw.appointment.entity.Appointment;
import com.B204.ALaw.appointment.entity.AppointmentStatus;
import com.fasterxml.jackson.annotation.JsonFormat;
import java.time.LocalDateTime;
import lombok.AccessLevel;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
@AllArgsConstructor(access = AccessLevel.PRIVATE)
public class AppointmentResponseDto {

  private Long appointmentId;
  private Long clientId;
  private Long lawyerId;
  private Long applicationId;
  private AppointmentStatus appointmentStatus;

  @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
  private LocalDateTime startTime;

  @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
  private LocalDateTime endTime;

  @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
  private LocalDateTime createdAt;

  public static AppointmentResponseDto from(Appointment appt) {
    return new AppointmentResponseDto(
        appt.getId(),
        appt.getClient().getId(),
        appt.getLawyer().getId(),
        appt.getApplication().getId(),
        appt.getAppointmentStatus(),
        appt.getStartTime(),
        appt.getEndTime(),
        appt.getCreatedAt()
    );
  }
}