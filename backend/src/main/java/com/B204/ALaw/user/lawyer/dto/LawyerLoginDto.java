package com.B204.ALaw.user.lawyer.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class LawyerLoginDto {
  @NotBlank(message="이메일은 필수입니다.")
  private String loginEmail;

  @NotBlank(message="비밀번호는 필수입니다.")
  private String password;
}
