package com.B204.lawvatar_backend.appointment.dto;

import lombok.*;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Getter @Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class GetMyAppointmentApplicationListResponse {

    // Field
    private Long applicationId;
    private Long clientId;
    private String title;
    private String summary;
    private String content;
    private String outcome;
    private String disadvantage;
    private Map<String, String> recommendedQuestions = new HashMap<>();
    private boolean isCompleted;
    private LocalDateTime createdAt;
    private List<Long> tags;

}
