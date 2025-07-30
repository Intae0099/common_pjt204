package com.B204.lawvatar_backend.application.dto;

import lombok.*;

@Getter @Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ModifyApplicationRequest {

    // Field
    // 수정될 가능성이 있는 필드가 아래 두개 뿐이다.
    private String outcome;
    private String disadvantage;

}
