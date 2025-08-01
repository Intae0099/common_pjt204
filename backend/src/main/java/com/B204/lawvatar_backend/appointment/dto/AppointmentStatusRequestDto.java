package com.B204.lawvatar_backend.appointment.dto;

import com.B204.lawvatar_backend.appointment.entity.Appointment;
import com.B204.lawvatar_backend.appointment.entity.AppointmentStatus;
import jakarta.validation.constraints.NotNull;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
public class AppointmentStatusRequestDto {

  @NotNull
  AppointmentStatus appointmentStatus;

}
