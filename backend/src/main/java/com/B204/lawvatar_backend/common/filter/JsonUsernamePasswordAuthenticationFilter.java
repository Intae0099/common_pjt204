package com.B204.lawvatar_backend.common.filter;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import org.springframework.http.MediaType;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.AuthenticationServiceException;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;

public class JsonUsernamePasswordAuthenticationFilter
    extends UsernamePasswordAuthenticationFilter {

  private final ObjectMapper objectMapper = new ObjectMapper();

  public JsonUsernamePasswordAuthenticationFilter(AuthenticationManager authManager) {
    super.setAuthenticationManager(authManager);
    // JSON 로그인 엔드포인트 맞춰서 처리
    super.setFilterProcessesUrl("/api/lawyers/login");
  }

  @Override
  public Authentication attemptAuthentication(HttpServletRequest request,
      HttpServletResponse response)
      throws AuthenticationException {

    if (!request.getContentType().startsWith(MediaType.APPLICATION_JSON_VALUE)) {
      return super.attemptAuthentication(request, response);
    }

    try {
      // { "loginEmail": "...", "password": "..." }
      Map<String, String> creds = objectMapper.readValue(
          request.getInputStream(),
          new TypeReference<HashMap<String, String>>() {}
      );
      UsernamePasswordAuthenticationToken token =
          new UsernamePasswordAuthenticationToken(
              creds.get("loginEmail"),
              creds.get("password")
          );
      setDetails(request, token);
      return this.getAuthenticationManager().authenticate(token);
    } catch (IOException e) {
      throw new AuthenticationServiceException("Invalid JSON", e);
    }
  }
}
