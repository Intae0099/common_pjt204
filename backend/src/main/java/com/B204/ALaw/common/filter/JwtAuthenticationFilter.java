package com.B204.ALaw.common.filter;

import com.B204.ALaw.common.principal.AdminPrincipal;
import com.B204.ALaw.common.principal.ClientPrincipal;
import com.B204.ALaw.common.principal.LawyerPrincipal;
import com.B204.ALaw.common.util.JwtUtil;
import com.B204.ALaw.user.admin.entity.Admin;
import com.B204.ALaw.user.admin.repository.AdminRepository;
import com.B204.ALaw.user.client.entity.Client;
import com.B204.ALaw.user.client.repository.ClientRepository;
import com.B204.ALaw.user.lawyer.entity.Lawyer;
import com.B204.ALaw.user.lawyer.repository.LawyerRepository;
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
  private final AdminRepository adminRepo;

  public JwtAuthenticationFilter(
      JwtUtil jwtUtil,
      LawyerRepository lawyerRepo,
      ClientRepository clientRepo,
      AdminRepository adminRepo) { this.jwtUtil = jwtUtil;
    this.lawyerRepo = lawyerRepo;
    this.clientRepo = clientRepo;
    this.adminRepo = adminRepo;
  }

  @Override
  protected boolean shouldNotFilter(HttpServletRequest request) throws ServletException {
    String path = request.getRequestURI();
    // 회원가입, 로그인 등 공개 엔드포인트
    return
        // 변호사 회원가입 / 로그인
        path.startsWith("/api/lawyers/signup")
        || path.startsWith("/api/lawyers/emails/check")
        || path.startsWith("/api/lawyers/login")
        || path.startsWith("/api/lawyers/list")
        || path.startsWith("/auth/login")

            // 의뢰인 회원가입 / 로그인
        || path.startsWith("/login/oauth2/")
        || path.startsWith("/oauth2/authorization/")
        || path.startsWith("/oauth2/callback/")

        // refreshToken 발급
        || path.startsWith("/api/auth/")

        // 관리자 기능 Test용
        || path.startsWith("/api/admin/login")
        || path.startsWith("/api/tag")

        // Swagger/OpenAPI
        || path.startsWith("/v3/api-docs")
        || path.startsWith("/swagger-ui")
        || path.startsWith("/swagger-ui.html")
        || path.startsWith("/webjars")
        || HttpMethod.OPTIONS.matches(request.getMethod());
  }

  @Override
  protected void doFilterInternal(
      HttpServletRequest req,
      HttpServletResponse res,
      FilterChain chain) throws ServletException, IOException {

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
      }  else if ("ADMIN".equalsIgnoreCase(userType)) {
        String email = subject.startsWith("ADMIN:")
            ? subject.substring("ADMIN:".length())
            : subject;
        Admin admin = adminRepo.findByLoginEmail(email)
            .orElseThrow(() ->
                new UsernameNotFoundException("No admin with email: " + email));
        principal = new AdminPrincipal(admin);

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
