package com.B204.ALaw.common.exception.dto;

import lombok.*;

import java.util.ArrayList;
import java.util.List;

@Getter @Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ErrorResponse {

    // Field
    private boolean success;
    private List<String> messages = new ArrayList<>();
}
