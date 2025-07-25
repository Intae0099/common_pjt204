package com.B204.lawvatar_backend.common.util;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import java.security.Key;
import java.util.Date;
import java.util.List;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

@Component
public class JwtUtil {
  private final Key key;
  private final long expMs;
  public JwtUtil(@Value("${jwt.secret}") String secret,
      @Value("${jwt.expiration}") long expMs) {
    this.key = Keys.hmacShaKeyFor(secret.getBytes());
    this.expMs = expMs;
  }
  public String generateToken(String subject, List<String> roles, String userType) {

    return Jwts.builder()
        .setSubject(subject)
        .claim("roles", roles)
        .claim("userType", userType)
        .setIssuedAt(new Date())
        .setExpiration(new Date(System.currentTimeMillis() + expMs))
        .signWith(key).compact();
  }
  public Claims validateAndGetClaims(String token) {
    return Jwts.parserBuilder().setSigningKey(key).build()
        .parseClaimsJws(token).getBody();
  }
}
