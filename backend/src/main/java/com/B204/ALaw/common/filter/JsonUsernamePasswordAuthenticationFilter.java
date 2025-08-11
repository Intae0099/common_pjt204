package com.B204.ALaw.common.filter;

import com.B204.ALaw.user.lawyer.entity.Lawyer;
import com.B204.ALaw.user.lawyer.service.LawyerService;
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
import org.springframework.security.authentication.DisabledException;
import org.springframework.security.authentication.LockedException;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;

public class JsonUsernamePasswordAuthenticationFilter
    extends UsernamePasswordAuthenticationFilter {

  private final ObjectMapper objectMapper = new ObjectMapper();
  private final LawyerService lawyerService;

  public JsonUsernamePasswordAuthenticationFilter(
      AuthenticationManager authManager,
      LawyerService lawyerService
      ) {
    super.setAuthenticationManager(authManager);
    super.setFilterProcessesUrl("/api/lawyers/login");      // JSON 로그인 엔드포인트 맞춰서 처리
    this.lawyerService  = lawyerService;
  }

  @Override
  public Authentication attemptAuthentication(
      HttpServletRequest request,
      HttpServletResponse response
  ) throws AuthenticationException {

    if (!request.getContentType().startsWith(MediaType.APPLICATION_JSON_VALUE)) {
      return super.attemptAuthentication(request, response);
    }

    try {
      Map<String, String> creds = objectMapper.readValue(
          request.getInputStream(),
          new TypeReference<HashMap<String, String>>() {}
      );
      String loginEmail = creds.get("loginEmail");
      String password   = creds.get("password");

      Lawyer lawyer = lawyerService.findByLoginEmail(loginEmail);
      switch (lawyer.getCertificationStatus()) {
        case PENDING -> throw new DisabledException("계정 승인 대기 중입니다.");
        case REJECTED -> throw new LockedException("승인 거부된 계정입니다.");
      }

      UsernamePasswordAuthenticationToken token =
          new UsernamePasswordAuthenticationToken( loginEmail, password );
      setDetails(request, token);
      return this.getAuthenticationManager().authenticate(token);

    } catch (IOException e) {
      throw new AuthenticationServiceException("Invalid JSON", e);
    }

  }
}
