package com.B204.lawvatar_backend.application.dto;

import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Getter @Setter
@NoArgsConstructor
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
