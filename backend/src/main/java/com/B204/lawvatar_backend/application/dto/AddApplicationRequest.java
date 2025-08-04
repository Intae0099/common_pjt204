package com.B204.lawvatar_backend.application.dto;

import lombok.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Getter @Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class AddApplicationRequest {

    // Field
    private String title;
    private String summary;
    private String content;
    private String outcome;
    private String disadvantage;
    private Map<String, String> recommendedQuestion = new HashMap<>();
    private List<Long> tags;
}
