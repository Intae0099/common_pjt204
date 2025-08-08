package com.B204.ALaw.user.client.dto;

import com.B204.ALaw.user.client.entity.Client;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ClientAdminDto {
  private Long clientId;
  private String oauthName;
  private String email;
  private String oauthProvider;
  private String oauthIdenifier;

  public static ClientAdminDto from(Client c){
    return new ClientAdminDto(
        c.getId(),
        c.getOauthName(),
        c.getEmail(),
        c.getOauthProvider(),
        c.getOauthIdentifier()
    );
  }

}
