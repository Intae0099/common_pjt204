package com.B204.ALaw.user.auth.controller;

import com.B204.ALaw.common.util.JwtUtil;
import com.B204.ALaw.user.admin.repository.AdminRepository;
import com.B204.ALaw.user.client.repository.ClientRepository;
import com.B204.ALaw.user.lawyer.repository.LawyerRepository;
import io.jsonwebtoken.Claims;
import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletRequest;
import java.util.Arrays;
import java.util.List;
import java.util.Map;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.web.bind.annotation.CookieValue;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
@Slf4j
public class AuthController {
  private final JwtUtil jwtUtil;
  private final LawyerRepository lawyerRepository;
  private final ClientRepository clientRepository;
  private final AdminRepository adminRepository;

  @PostMapping("/refresh")
  public ResponseEntity<Map<String,String>> refresh(
      @CookieValue(value = "refresh_token", required = false) String refreshToken,
      HttpServletRequest request
  ) {
    Cookie[] cookies = request.getCookies();
    if (cookies != null) {
      for (Cookie c : cookies) {
        System.out.println("쿠키 이름: " + c.getName() + ", 값: " + c.getValue());
      }
    }

    if (refreshToken == null) {
      throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Refresh token missing");
    }

    Claims claims = jwtUtil.validateAndGetClaims(refreshToken);
    String subject = claims.getSubject();
    String userType = claims.get("userType", String.class);

    // 1. 사용자 로드 (선택적 – roles 조회용)
    List<String> roles;
    String newSubject = subject;
    switch (userType.toUpperCase()) {
      case "ADMIN" -> {
        // subject 에서 실제 이메일 부분만 추출
        String email = subject.substring("ADMIN:".length());
        adminRepository.findByLoginEmail(email)
            .orElseThrow(() -> new UsernameNotFoundException("No admin with email: " + email));
        roles = List.of("ROLE_ADMIN");
        // newSubject 는 그대로 "ADMIN:email" 과 같이 유지해도 됩니다.
      }
      case "LAWYER" -> {
        long lawyerId = Long.parseLong(subject);
        lawyerRepository.findById(lawyerId)
            .orElseThrow(() -> new UsernameNotFoundException("No lawyer with id: " + lawyerId));
        roles = List.of("ROLE_LAWYER");
      }
      case "CLIENT" -> {
        clientRepository.findByOauthIdentifier(subject)
            .orElseThrow(() -> new UsernameNotFoundException("No client with oauthIdentifier: " + subject));
        roles = List.of("ROLE_CLIENT");
      }
      default -> throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Unknown userType: " + userType);
    }

    // 2. AccessToken 재발급
    String newAccess = jwtUtil.generateAccessToken(subject, roles, userType);

    return ResponseEntity.ok(Map.of("accessToken", newAccess));
  }
}