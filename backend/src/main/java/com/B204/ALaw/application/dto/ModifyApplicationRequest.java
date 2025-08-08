package com.B204.ALaw.application.dto;

import lombok.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Getter @Setter
@NoArgsConstructor
@AllArgsConstructor
public class ModifyApplicationRequest {

    // Field
    private String title;
    private String summary;
    private String content;
    private String outcome;
    private String disadvantage;
    private Map<String, String> recommendedQuestion = new HashMap<>();
    private List<Long> tags;
}
