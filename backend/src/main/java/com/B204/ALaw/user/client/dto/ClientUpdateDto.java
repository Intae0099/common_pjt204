package com.B204.ALaw.user.client.dto;

import jakarta.validation.constraints.Size;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
public class ClientUpdateDto {

  @Size(max = 20)
  private String oauthName;

  @Size(max = 30)
  private String email;
}