package com.B204.lawvatar_backend.application.dto;

import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.util.List;

@Getter @Setter
@NoArgsConstructor
public class AddApplicationRequest {

    // Field
    private String title;
    private String summary;
    private String content;
    private String outcome;
    private String disadvantage;
    private String recommendedQuestion;
    private List<Long> tags;

}
