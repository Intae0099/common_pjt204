package com.B204.lawvatar_backend.application.dto;

import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter @Setter
@NoArgsConstructor
public class AddApplicationRequest {

    // Field
    String fullText;
    String title;
    String summary;
    String content;
    String outcome;
    String disadvantage;

}
