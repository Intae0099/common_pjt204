package com.B204.lawvatar_backend.user.auth.controller;

import com.B204.lawvatar_backend.common.util.JwtUtil;
import com.B204.lawvatar_backend.user.auth.entity.RefreshToken;
import com.B204.lawvatar_backend.user.auth.repository.RefreshTokenRepository;
import com.B204.lawvatar_backend.user.auth.service.RefreshTokenService;
import io.jsonwebtoken.Claims;
import java.util.List;
import java.util.Map;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequestMapping("/auth")
@RequiredArgsConstructor
public class AuthController {
  private final RefreshTokenService rtService;
  private final JwtUtil jwtUtil;
  private final RefreshTokenRepository rtRepo;

  @PostMapping("/refresh")
  public ResponseEntity<Map<String,String>> refresh(@RequestBody Map<String,String> req) {
    String raw = req.get("refreshToken");
    Claims claims = jwtUtil.validateAndGetClaims(raw);
    String username = claims.getSubject();

    // DB에서 토큰 검증
    RefreshToken rt = rtRepo.findByRefreshToken(raw)
        .filter(r->r.getRevokedAt()==null)
        .orElseThrow(() -> new ResponseStatusException(HttpStatus.UNAUTHORIZED));

    // 새 Access Token
    String newAccess = jwtUtil.generateAccessToken(username, List.of(/*roles 재조회 or 클레임*/), claims.get("userType", String.class));

    return ResponseEntity.ok(Map.of("accessToken", newAccess));
  }
}