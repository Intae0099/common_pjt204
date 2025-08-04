package com.B204.lawvatar_backend.user.lawyer.dto;

public record LoginResult(
    String accessToken,
    String refreshCookie,
    String name
) {

  public String getRefreshCooktie() {
    return refreshCookie;
  }

  public String getAccessToken() {
    return accessToken;
  }

  public String getName() {
    return name;
  }
}
