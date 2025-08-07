package com.B204.ALaw.user.lawyer.dto;

import com.B204.ALaw.user.lawyer.entity.CertificationStatus;
import com.B204.ALaw.user.lawyer.entity.Lawyer;
import java.util.List;
import java.util.stream.Collectors;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class LawyerAdminDto {   // admin이 lawyer를 cetification_status에 따라 search 시에 사용
  private Long lawyerId;
  private String loginEmail;
  private String name;
  private String introduction;
  private String exam;
  private String registrationNumber;
  private CertificationStatus certificationStatus;
  private int consultationCount;
  private List<String> tags;

  public static LawyerAdminDto from(Lawyer l) {
    return new LawyerAdminDto(
        l.getId(),
        l.getLoginEmail(),
        l.getName(),
        l.getIntroduction(),
        l.getExam(),
        l.getRegistrationNumber(),
        l.getCertificationStatus(),
        l.getConsultationCount(),
        l.getTags().stream()
            .map(lt -> lt.getTag().getName())
            .collect(Collectors.toList())
    );
  }
}