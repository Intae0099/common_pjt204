package com.B204.ALaw.user.lawyer.dto;

import jakarta.validation.constraints.Size;
import java.util.List;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
public class LawyerUpdateDto {

  /** 값이 있으면 최대 10자까지만 허용 */
  @Size(max = 10)
  private String name;

  /** 최대 500자 */
  @Size(max = 500)
  private String introduction;

  /** 최대 20자 */
  @Size(max = 20)
  private String exam;

  /** 최대 20자 */
  @Size(max = 20)
  private String registrationNumber;

  /** 태그 ID 리스트 (null이면 변경 안 함) */
  private List<Long> tags;

  /** Base64로 인코딩된 이미지 (prefix 제외) */
  private String photoBase64;
}