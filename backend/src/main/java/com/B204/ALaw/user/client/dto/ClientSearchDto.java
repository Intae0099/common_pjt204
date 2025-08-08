package com.B204.ALaw.user.client.dto;

import com.B204.ALaw.user.client.entity.Client;
import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class ClientSearchDto {
  private Long clientId;
  private String loginEmail;
  private String name;
  private String oauthProvider;

  public static ClientSearchDto from(Client client) {
    return new ClientSearchDto(
        client.getId(),
        client.getEmail(),
        client.getOauthName(),
        client.getOauthProvider()
    );
  }
}
