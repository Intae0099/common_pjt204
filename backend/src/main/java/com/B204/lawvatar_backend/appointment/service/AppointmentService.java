package com.B204.lawvatar_backend.appointment.service;

import com.B204.lawvatar_backend.application.entity.Application;
import com.B204.lawvatar_backend.appointment.entity.Appointment;
import com.B204.lawvatar_backend.appointment.repository.AppointmentRepository;
import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

@Service
@RequiredArgsConstructor
@Transactional
public class AppointmentService {

    // Field
    private final AppointmentRepository appointmentRepository;

    // Method
    public List<Application> getMyAppointmentApplicationList(Long lawyerId) {

        List<Appointment> appointmentList = appointmentRepository.findByLawyerId(lawyerId);
        List<Application> applicationList = new ArrayList<>();
        for(Appointment appointment : appointmentList) {
            applicationList.add(appointment.getApplication());
        }
        return applicationList;
    }
}
