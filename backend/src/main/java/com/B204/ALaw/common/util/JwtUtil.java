package com.B204.ALaw.common.util;

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
  private final long accessTokenValidMs  = 60 * 60 * 1000;     // 1시간
  private final long refreshTokenValidMs = 7L * 24 * 60 * 60 * 1000; // 7일

  public JwtUtil(@Value("${jwt.secret}") String secret) {
    this.key = Keys.hmacShaKeyFor(secret.getBytes());
  }

  public String generateAccessToken(String subject, List<String> roles, String userType) {
    return Jwts.builder()
        .setSubject(subject)
        .claim("roles", roles)
        .claim("userType", userType)
        .setIssuedAt(new Date())
        .setExpiration(new Date(System.currentTimeMillis() + accessTokenValidMs))
        .signWith(key).compact();
  }

  public String generateRefreshToken(String subject, String userType){
    Date now = new Date();
    Date exp = new Date(now.getTime() + refreshTokenValidMs);

    return Jwts.builder()
        .setSubject(subject)
        .claim("userType", userType)
        .setIssuedAt(now)
        .setExpiration(exp)
        .signWith(key)
        .compact();
  }

  public Claims validateAndGetClaims(String token) {
    return Jwts.
        parserBuilder().
        setSigningKey(key).
        build().
        parseClaimsJws(token).
        getBody();
  }

  public String extractSubject(String token) {
    return validateAndGetClaims(token).getSubject();
  }
}
