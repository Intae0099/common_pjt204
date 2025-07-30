package com.B204.lawvatar_backend.common.filter;

import com.B204.lawvatar_backend.common.principal.ClientPrincipal;
import com.B204.lawvatar_backend.common.principal.LawyerPrincipal;
import com.B204.lawvatar_backend.common.util.JwtUtil;
import com.B204.lawvatar_backend.user.client.entity.Client;
import com.B204.lawvatar_backend.user.client.repository.ClientRepository;
import com.B204.lawvatar_backend.user.lawyer.entity.Lawyer;
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
import org.springframework.http.HttpMethod;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

@Component
public class JwtAuthenticationFilter extends OncePerRequestFilter {
  private final JwtUtil jwtUtil;
  private final LawyerRepository lawyerRepo;
  private final ClientRepository clientRepo;

  public JwtAuthenticationFilter(
      JwtUtil jwtUtil,
      LawyerRepository lawyerRepo,
      ClientRepository clientRepo) { this.jwtUtil = jwtUtil;
    this.lawyerRepo = lawyerRepo;
    this.clientRepo = clientRepo;
  }

  @Override
  protected boolean shouldNotFilter(HttpServletRequest request) throws ServletException {
    String path = request.getRequestURI();
    // 사전 검사, 회원가입, 로그인 등 공개 엔드포인트
    return path.startsWith("/api/lawyers/signup")
        || path.startsWith("/api/lawyers/emails/check")
        || path.startsWith("/api/lawyers/login")
        || path.startsWith("/login/oauth2/")
        || HttpMethod.OPTIONS.matches(request.getMethod());
  }

  @Override
  protected void doFilterInternal(HttpServletRequest req,
      HttpServletResponse res,
      FilterChain chain) throws ServletException, IOException {

    String path = req.getServletPath();
    if (path.startsWith("/auth") ||
        path.startsWith("/oauth2") ||
        path.startsWith("/login/oauth2") ||
        path.startsWith("/api/lawyers/signup") ||
        path.startsWith("/api/lawyers/login")
//        || path.startsWith("/api")                         // 일단 다 열어둠 . 추후 수정 필요 / must be fixed
    ) {
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

      // 2) userType 및 subject 분기
      String userType = claims.get("userType", String.class);
      String subject = claims.getSubject();

      Object principal;

      if ("LAWYER".equalsIgnoreCase(userType)) {
        // 방어 로직 추가
        try {
          Long id = Long.valueOf(subject);
          Lawyer lawyer = lawyerRepo.findById(id)
              .orElseThrow(() -> new UsernameNotFoundException("No lawyer with id: " + id));
          principal = new LawyerPrincipal(lawyer);
        } catch (NumberFormatException e) {
          res.sendError(HttpServletResponse.SC_UNAUTHORIZED, "Invalid subject for LAWYER token");
          return;
        }

      } else if ("CLIENT".equalsIgnoreCase(userType)) {
        Client client = clientRepo.findByOauthIdentifier(subject)
            .orElseThrow(() -> new UsernameNotFoundException("No client with oauthIdentifier: " + subject));
        principal = new ClientPrincipal(client);
      } else {
        res.sendError(HttpServletResponse.SC_UNAUTHORIZED, "Invalid userType");
        return;
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
