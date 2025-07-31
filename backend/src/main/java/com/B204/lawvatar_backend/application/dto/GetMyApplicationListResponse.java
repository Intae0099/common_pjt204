package com.B204.lawvatar_backend.application.dto;

import lombok.*;

import java.time.LocalDateTime;
import java.util.List;

@Getter @Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class GetMyApplicationListResponse {

    // Field
    Long applicationId;
    Long clientId;
    String title;
    String summary;
    String content;
    String outcome;
    String disadvantage;
    String recommendedQuestions;
    boolean isCompleted;
    LocalDateTime createdAt;
    List<Long> tags;

}
