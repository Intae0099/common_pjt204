package com.B204.lawvatar_backend.common.filter;

import com.B204.lawvatar_backend.common.principal.ClientPrincipal;
import com.B204.lawvatar_backend.common.principal.LawyerPrincipal;
import com.B204.lawvatar_backend.common.util.JwtUtil;
import com.B204.lawvatar_backend.user.client.repository.ClientRepository;
import com.B204.lawvatar_backend.user.lawyer.repository.LawyerRepository;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.JwtException;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.List;
import java.util.stream.Collectors;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.web.filter.OncePerRequestFilter;

public class JwtAuthenticationFilter extends OncePerRequestFilter {
  private final JwtUtil jwtUtil;
  private final LawyerRepository lawyerRepo;
  private final ClientRepository clientRepo;

  public JwtAuthenticationFilter(JwtUtil jwtUtil, LawyerRepository lawyerRepo,
      ClientRepository clientRepo) { this.jwtUtil = jwtUtil;
    this.lawyerRepo = lawyerRepo;
    this.clientRepo = clientRepo;
  }

  @Override
  protected void doFilterInternal(HttpServletRequest req,
      HttpServletResponse res,
      FilterChain chain) throws ServletException, IOException {
    String path = req.getServletPath();
    if (path.startsWith("/auth") ||
        path.startsWith("/oauth2") ||
        path.startsWith("/login/oauth2")) {
      chain.doFilter(req, res);
      return;
    }

    String header = req.getHeader("Authorization");
    if (header == null || !header.startsWith("Bearer ")) {
      res.sendError(HttpServletResponse.SC_UNAUTHORIZED);
      return;
    }

    String token = header.substring(7);
    try {
      Claims claims = jwtUtil.validateAndGetClaims(token);

      // 1) roles 클레임에서 GrantedAuthority 리스트 생성
      List<GrantedAuthority> authorities = (List<GrantedAuthority>) claims.get("roles", List.class).stream()
          .map(r -> new SimpleGrantedAuthority((String) r))
          .collect(Collectors.toList());

      // 2) userType 클레임으로 분기
      String userType = claims.get("userType", String.class);
      Long id = Long.valueOf(claims.getSubject());

      Object principal;
      if ("LAWYER".equalsIgnoreCase(userType)) {
        // 변호사 테이블에서 로드 (예: lawyerRepo)
        var lawyer = lawyerRepo.findById(id)
            .orElseThrow(() -> new UsernameNotFoundException("No lawyer " + id));
        principal = new LawyerPrincipal(lawyer);
      } else {
        // 일반 유저 테이블에서 로드 (예: userRepo)
        var client = clientRepo.findById(id)
            .orElseThrow(() -> new UsernameNotFoundException("No user " + id));
        principal = new ClientPrincipal(client);
      }

      // 3) Authentication 토큰 생성
      Authentication authToken =
          new UsernamePasswordAuthenticationToken(principal, null, authorities);

      SecurityContextHolder.getContext().setAuthentication(authToken);
    } catch (JwtException ex) {
      // 토큰이 유효하지 않거나 파싱 실패 시
      res.sendError(HttpServletResponse.SC_UNAUTHORIZED);
      return;
    }

    chain.doFilter(req, res);
  }

}
