package com.B204.ALaw.user.lawyer.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;

import java.util.List;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor       // 기본 생성자
@AllArgsConstructor      // 모든 필드를 인자로 받는 생성자 (선택)
public class LawyerSignupDto {
    @NotBlank(message = "이메일은 필수입니다.")
    @Email(message = "유효한 이메일 주소여야 합니다.")
    private String loginEmail;

    @NotBlank(message = "비밀번호는 필수입니다.")
    private String password;

    @NotBlank(message = "이름은 필수입니다.")
    private String name;

    private String introduction;

    @NotBlank(message = "시험 정보는 필수입니다.")
    private String exam;

    @NotBlank(message = "등록번호는 필수입니다.")
    private String registrationNumber;

    private String photoBase64;

    @NotEmpty(message = "적어도 하나의 태그를 선택해야 합니다.")
    private List<Long> tags;
}
