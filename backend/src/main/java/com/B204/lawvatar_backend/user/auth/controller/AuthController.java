package com.B204.lawvatar_backend.user.auth.controller;

import com.B204.lawvatar_backend.common.util.JwtUtil;
import com.B204.lawvatar_backend.user.auth.entity.RefreshToken;
import com.B204.lawvatar_backend.user.auth.repository.RefreshTokenRepository;
import com.B204.lawvatar_backend.user.auth.service.RefreshTokenService;
import com.B204.lawvatar_backend.user.client.entity.Client;
import com.B204.lawvatar_backend.user.client.repository.ClientRepository;
import com.B204.lawvatar_backend.user.lawyer.entity.Lawyer;
import com.B204.lawvatar_backend.user.lawyer.repository.LawyerRepository;
import io.jsonwebtoken.Claims;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.web.bind.annotation.CookieValue;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthController {
  private final JwtUtil jwtUtil;
  private final LawyerRepository lawyerRepository;
  private final ClientRepository clientRepository;

  @PostMapping("/refresh")
  public ResponseEntity<Map<String,String>> refresh(
      @CookieValue(value = "refresh_token", required = false) String refreshToken
  ) {
    if (refreshToken == null) {
      throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Refresh token missing");
    }

    Claims claims = jwtUtil.validateAndGetClaims(refreshToken);
    String subject = claims.getSubject();
    String userType = claims.get("userType", String.class);

    // 1. 사용자 로드 (선택적 – roles 조회용)
    List<String> roles;
    if ("LAWYER".equalsIgnoreCase(userType)) {
      Long lawyerId = Long.valueOf(subject);
      Lawyer lawyer = lawyerRepository.findById(lawyerId)
          .orElseThrow(() -> new UsernameNotFoundException("No lawyer with id: " + lawyerId));
      roles = List.of("ROLE_LAWYER");
    } else {
      Client client = clientRepository.findByOauthIdentifier(subject)
          .orElseThrow(() -> new UsernameNotFoundException("No client with oauthIdentifier: " + subject));
      roles = List.of("ROLE_CLIENT");
    }

    // 2. AccessToken 재발급
    String newAccess = jwtUtil.generateAccessToken(subject, roles, userType);

    return ResponseEntity.ok(Map.of("accessToken", newAccess));
  }
}