package com.B204.ALaw.user.lawyer.dto;

import com.B204.ALaw.user.lawyer.entity.Lawyer;
import java.util.Base64;
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
  private String photoBase64;

  public LawyerInfoDto(
      String loginEmail,
      String name,
      String introduction,
      String exam,
      String registrationNumber,
      int consultationCount,
      List<Long> tags,
      String photoBase64
  ) {
    this.loginEmail = loginEmail;
    this.name = name;
    this.introduction = introduction;
    this.exam = exam;
    this.registrationNumber = registrationNumber;
    this.consultationCount = consultationCount;
    this.tags = tags;
    this.photoBase64 = photoBase64;
  }

  public static LawyerInfoDto from(Lawyer lawyer) {
    // photo가 null이 아니면 Base64로 인코딩, null이면 그대로 null
    String encodedPhoto = null;
    if (lawyer.getPhoto() != null) {
      encodedPhoto = Base64.getEncoder().encodeToString(lawyer.getPhoto());
    }


    return new LawyerInfoDto(
        lawyer.getLoginEmail(),
        lawyer.getName(),
        lawyer.getIntroduction(),
        lawyer.getExam(),
        lawyer.getRegistrationNumber(),
        lawyer.getConsultationCount(),
        lawyer.getTags().stream()
            .map(lawyerTag -> lawyerTag.getTag().getId())
            .toList(),
        encodedPhoto
    );
  }

}
