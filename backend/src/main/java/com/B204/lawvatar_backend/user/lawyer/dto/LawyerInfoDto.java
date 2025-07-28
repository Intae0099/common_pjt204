package com.B204.lawvatar_backend.user.lawyer.dto;

import com.B204.lawvatar_backend.user.lawyer.entity.Lawyer;
import java.util.List;
import lombok.Data;

@Data
public class LawyerInfoDto {
  private String loginEmail;
  private String name;
  private String introduction;
  private String exam;
  private String registrationNumber;
  private int consultationCount;
  private List<Long> tags;

  public LawyerInfoDto(
      String loginEmail,
      String name,
      String introduction,
      String exam,
      String registrationNumber,
      int consultationCount,
      List<Long> tags
  ) {
    this.loginEmail = loginEmail;
    this.name = name;
    this.introduction = introduction;
    this.exam = exam;
    this.registrationNumber = registrationNumber;
    this.consultationCount = consultationCount;
    this.tags = tags;
  }

  public static LawyerInfoDto from(Lawyer lawyer) {
    return new LawyerInfoDto(
        lawyer.getLoginEmail(),
        lawyer.getName(),
        lawyer.getIntroduction(),
        lawyer.getExam(),
        lawyer.getRegistrationNumber(),
        lawyer.getConsultationCount(),
        lawyer.getTags().stream()
            .map(lawyerTag -> lawyerTag.getTag().getId())
            .toList()
    );
  }

}
