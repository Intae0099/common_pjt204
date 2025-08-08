package com.B204.ALaw.appointment.dto;

import com.B204.ALaw.appointment.entity.AppointmentStatus;
import jakarta.validation.constraints.NotNull;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
public class AppointmentStatusRequestDto {

  @NotNull
  AppointmentStatus appointmentStatus;

}
