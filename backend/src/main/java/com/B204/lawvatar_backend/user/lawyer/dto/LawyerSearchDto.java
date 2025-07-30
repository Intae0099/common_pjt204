package com.B204.lawvatar_backend.user.lawyer.dto;


import com.B204.lawvatar_backend.user.lawyer.entity.Lawyer;
import java.util.List;
import java.util.stream.Collectors;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class LawyerSearchDto {

  /** 변호사 고유 ID */
  private Long lawyerId;

  /** 로그인 이메일 */
  private String loginEmail;

  /** 이름 */
  private String name;

  /** 소개 글 */
  private String introduction;

  /** 전문 분야 태그 ID 목록 */
  private List<Long> tags;

  /**
   * Entity → DTO 변환
   */
  public static LawyerSearchDto from(Lawyer lawyer) {
    return new LawyerSearchDto(
        lawyer.getId(),
        lawyer.getLoginEmail(),
        lawyer.getName(),
        lawyer.getIntroduction(),
        lawyer.getTags().stream()
            .map(lt -> lt.getTag().getId())
            .collect(Collectors.toList())
    );
  }
}