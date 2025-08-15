package com.B204.ALaw.common.config;

import com.B204.ALaw.common.filter.JsonUsernamePasswordAuthenticationFilter;
import com.B204.ALaw.common.filter.JwtAuthenticationFilter;
import com.B204.ALaw.common.util.JwtUtil;
import com.B204.ALaw.user.admin.service.AdminService;
import com.B204.ALaw.user.auth.service.RefreshTokenService;
import com.B204.ALaw.user.client.entity.Client;
import com.B204.ALaw.user.client.repository.ClientRepository;
import com.B204.ALaw.user.client.service.ClientService;
import com.B204.ALaw.user.lawyer.entity.Lawyer;
import com.B204.ALaw.user.lawyer.service.LawyerService;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.time.Duration;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import java.util.Set;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;
import org.springframework.core.annotation.Order;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseCookie;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.DisabledException;
import org.springframework.security.authentication.LockedException;
import org.springframework.security.authentication.ProviderManager;
import org.springframework.security.authentication.dao.DaoAuthenticationProvider;
import org.springframework.security.config.Customizer;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.AuthorityUtils;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.oauth2.client.InMemoryOAuth2AuthorizedClientService;
import org.springframework.security.oauth2.client.OAuth2AuthorizedClientService;
import org.springframework.security.oauth2.client.authentication.OAuth2AuthenticationToken;
import org.springframework.security.oauth2.client.registration.ClientRegistration;
import org.springframework.security.oauth2.client.registration.ClientRegistrationRepository;
import org.springframework.security.oauth2.client.web.OAuth2LoginAuthenticationFilter;
import org.springframework.security.oauth2.core.user.OAuth2User;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.AuthenticationFailureHandler;
import org.springframework.security.web.authentication.AuthenticationSuccessHandler;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.stereotype.Component;
import org.springframework.web.util.UriComponentsBuilder;

@Configuration
@EnableWebSecurity
public class SecurityConfig {

  private final JwtUtil jwtUtil;
  private final JwtAuthenticationFilter jwtAuthenticationFilter;

  private final ClientService clientService;
  private final RefreshTokenService refreshTokenService;

  public SecurityConfig(
      JwtUtil jwtUtil,
      JwtAuthenticationFilter jwtAuthenticationFilter,
      ClientService clientService,
      RefreshTokenService refreshTokenService, AdminService adminService
  ) {
    this.jwtUtil = jwtUtil;
    this.jwtAuthenticationFilter = jwtAuthenticationFilter;
    this.clientService = clientService;
    this.refreshTokenService = refreshTokenService;
  }


  @Component
  public static class OAuth2JwtSuccessHandler implements AuthenticationSuccessHandler {

    private final ClientRepository clientRepository;
    private final JwtUtil jwtUtil;
    private final RefreshTokenService refreshTokenService;
    private final ClientRegistrationRepository clientRegRepo; // UserNameAttributeName 조회용

    public OAuth2JwtSuccessHandler(
        ClientRepository clientRepository,
        JwtUtil jwtUtil,
        RefreshTokenService refreshTokenService, ClientRegistrationRepository clientRegRepo
    ) {
      this.clientRepository = clientRepository;
      this.jwtUtil = jwtUtil;
      this.refreshTokenService = refreshTokenService;
      this.clientRegRepo = clientRegRepo;
    }

    @Override
    public void onAuthenticationSuccess(HttpServletRequest req,
        HttpServletResponse res,
        Authentication authentication) throws IOException {

      OAuth2AuthenticationToken oauthToken = (OAuth2AuthenticationToken) authentication;
      String regId = oauthToken.getAuthorizedClientRegistrationId();

      OAuth2User oauthUser = oauthToken.getPrincipal();
      ClientRegistration reg = clientRegRepo.findByRegistrationId(regId);
      String userNameAttr = reg
          .getProviderDetails()
          .getUserInfoEndpoint()
          .getUserNameAttributeName();

      Object rawId = oauthUser.getAttribute(userNameAttr);
      @SuppressWarnings("unchecked")
      Map<String,Object> kakaoAccount = oauthUser.getAttribute("kakao_account");
      Map<String,Object> profile      = (Map<String,Object>) kakaoAccount.get("profile");
      String nickname                = (String) profile.get("nickname");

      // 3) ClientService.loadUser 와 동일한 조회/생성 로직
      Client client = clientRepository.findByOauthIdentifier(rawId.toString())
          .orElseGet(() -> clientRepository.save(
              new Client(rawId.toString(), nickname, regId)
          ));

      String accessToken = jwtUtil.generateAccessToken(
          client.getOauthIdentifier(),
          List.of("ROLE_CLIENT"),
          "CLIENT"
      );

      String refreshToken = jwtUtil.generateRefreshToken(client.getOauthIdentifier(), "CLIENT");
      refreshTokenService.createForClient(client, refreshToken);

      ResponseCookie refreshCookie = ResponseCookie.from("refresh_token", refreshToken)
          .httpOnly(true)
          .secure(true)
          .sameSite("None")
          .path("/")
          .maxAge(Duration.ofDays(7))
          .build();
      res.setHeader(HttpHeaders.SET_COOKIE, refreshCookie.toString());

      /*
      redirectUrl를 도메인 프론트로 설정
      String frontBase = resolveFrontRedirectBase(req);

      String redirectUrl = UriComponentsBuilder
          .fromUriString(frontBase + "/oauth2/callback/kakao")
          .queryParam("accessToken", accessToken)
          .build().toUriString();

      System.out.println("frontBase={" +  frontBase + "} redirectUrl={"  +  redirectUrl + "}");
      */

      String redirectUrl = UriComponentsBuilder
          .fromUriString("https://i13b204.p.ssafy.io/oauth2/callback/kakao")
          .queryParam("accessToken", accessToken)
          .build().toUriString();

      /*
       redirectUrl을 로컬 프론트로 설정
       */
      /*
      String redirectUrl = UriComponentsBuilder
          .fromUriString("http://localhost:5173/oauth2/callback/kakao")
          .queryParam("accessToken", accessToken)
          .build().toUriString();

       */

      res.sendRedirect(redirectUrl);
    }

    private String resolveFrontRedirectBase(HttpServletRequest req) {
      // 1) 프록시 헤더 우선 (운영)
      String fProto  = header(req, "X-Forwarded-Proto");
      String fHost   = header(req, "X-Forwarded-Host");
      String fPrefix = header(req, "X-Forwarded-Prefix"); // 예: "/api"

      if (fHost != null && fHost.contains(",")) fHost = fHost.split(",")[0].trim();

      // ✅ 화이트리스트
      Set<String> allowHosts = Set.of(
          "i13b204.p.ssafy.io", "localhost:8080", "localhost"
      );

      if (fHost != null && allowHosts.contains(fHost)) {
        String proto = (fProto != null) ? fProto : "https";
        return proto + "://" + fHost;
      }

      // 2) 로컬/그 외 폴백
      String serverName = req.getServerName();
      if ("localhost".equalsIgnoreCase(serverName)) {
        return "http://localhost:5173";
      }
      if ("i13b204.p.ssafy.io".equalsIgnoreCase(serverName)) {
        return "";
      }

      // 마지막 안전 폴백
      return "http://localhost:5173";
    }

    private String header(HttpServletRequest req, String name) {
      String v = req.getHeader(name);
      return (v == null || v.isBlank()) ? null : v;
    }

  }

  @Bean("lawyerAuthenticationManager")
  @Primary
  public AuthenticationManager lawyerAuthenticationManager(
      LawyerService lawyerService,
      PasswordEncoder passwordEncoder
  ) {
    // DaoAuthenticationProvider 구성
    DaoAuthenticationProvider provider = new DaoAuthenticationProvider();

    // UserDetailsService : Lawyer → Spring Security UserDetails 로 변환
    provider.setUserDetailsService(username -> {
      Lawyer lawyer = lawyerService.findByLoginEmail(username);

      // 권한 목록 (ROLE_LAWYER 고정)
      List<GrantedAuthority> authorities =
          AuthorityUtils.createAuthorityList("ROLE_LAWYER");
      // Spring Security User 객체로 변환
      return new org.springframework.security.core.userdetails.User(
          lawyer.getLoginEmail(),
          lawyer.getPasswordHash(),
          authorities
      );
    });

    // BCryptPasswordEncoder 주입
    provider.setPasswordEncoder(passwordEncoder);

    // ProviderManager 에 프로바이더 등록
    return new ProviderManager(List.of(provider));
  }

  @Bean
  @Order(2)
  public SecurityFilterChain lawyerFilterChain(
      HttpSecurity http,
      @Qualifier("lawyerAuthenticationManager") AuthenticationManager authManager,
      OAuth2JwtSuccessHandler oauth2JwtSuccessHandler,
      LawyerService lawyerService
  ) throws Exception {

    // 의뢰인 OAuth2 로그인 실패 핸들러
    AuthenticationFailureHandler oauth2FailureHandler = ( req, res, ex) ->{
      String msg = ex.getMessage();
      if (msg != null && msg.contains("rate limit")) {
        res.setStatus(429);
        res.setContentType("application/json;charset=UTF-8");
        res.getWriter().write("{\"error\":\"kakao_rate_limit\",\"message\":\"잠시 후 다시 시도해주세요.\"}");
        return;
      }
      res.sendError(HttpServletResponse.SC_UNAUTHORIZED, "OAuth2 Login Failed");
    };

    // 변호사 로컬 로그인 성공 핸들러 → JWT 발급
    AuthenticationSuccessHandler lawyerLoginSuccessHandler =
        (req, res, auth) -> {

          String email = auth.getName();
          List<String> roles = List.of("ROLE_LAWYER");

          Lawyer lawyer = lawyerService.findByLoginEmail(email);
          String subject = String.valueOf(lawyer.getId());
          String refreshToken = jwtUtil.generateRefreshToken(subject, "LAWYER");
          refreshTokenService.createForLawyer(lawyer, refreshToken);

          ResponseCookie refreshCookie = ResponseCookie.from("refresh_token", refreshToken)
              .httpOnly(true)
              .secure(true)
              .sameSite("None")
              .path("/")
              .maxAge(Duration.ofDays(7))
              .build();
          res.setHeader(HttpHeaders.SET_COOKIE, refreshCookie.toString());

          String accessToken = jwtUtil.generateAccessToken(subject, roles, "LAWYER");

          Map<String, String> body = new LinkedHashMap<>();
          body.put("accessToken", accessToken);

          res.setStatus(HttpServletResponse.SC_OK);
          res.setContentType(MediaType.APPLICATION_JSON_VALUE);
          res.getWriter().write(new ObjectMapper().writeValueAsString(body));
        };

    // 변호사 로컬 로그인 실패 핸들러
    AuthenticationFailureHandler lawyerLoginFailureHandler =
        (req, res, ex) -> {
      int status = HttpServletResponse.SC_UNAUTHORIZED;
      if(ex instanceof DisabledException || ex instanceof LockedException){
        status = HttpServletResponse.SC_FORBIDDEN;
      }

      res.setStatus(status);
      res.setContentType("application/json");
      res.setCharacterEncoding("UTF-8");

      String message = switch (status) {
        case HttpServletResponse.SC_FORBIDDEN -> "{\"error\":\"승인 대기 중이거나 거부된 계정입니다. \"}";
        default -> "{\"error\":\"아이디 또는 비밀번호가 올바르지 않습니다.\"}";
      };

      res.getWriter().write(message);
      res.getWriter().flush();
    };

    JsonUsernamePasswordAuthenticationFilter jsonLoginFilter =
        new JsonUsernamePasswordAuthenticationFilter(authManager, lawyerService);
    jsonLoginFilter.setFilterProcessesUrl("/api/lawyers/login");
    jsonLoginFilter.setAuthenticationSuccessHandler(lawyerLoginSuccessHandler);
    jsonLoginFilter.setAuthenticationFailureHandler(lawyerLoginFailureHandler);

    http
        // 1) CSRF 비활성화
        .csrf(csrf -> csrf.disable())

        // 2) CORS 활성화 (기본 CorsConfigurationSource 빈을 사용하려면 withDefaults())
        .cors(Customizer.withDefaults())

        .addFilterAt(jsonLoginFilter, UsernamePasswordAuthenticationFilter.class)


        // OAuth2 로그인 설정
        .oauth2Login(oauth -> oauth
            .authorizationEndpoint(authz -> authz.baseUri("/oauth2/authorization"))
            .redirectionEndpoint(redir -> redir.baseUri("/login/oauth2/code/*"))
            .userInfoEndpoint(u -> u.userService(clientService))
            .successHandler(oauth2JwtSuccessHandler)
            .failureHandler(oauth2FailureHandler)
        )

        // 세션 설정 (기존 유지: OAuth2용 state 저장 가능)
        .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.IF_REQUIRED))

        // JWT 필터: OAuth2 로그인 이후에 추가
        .addFilterAfter(jwtAuthenticationFilter, OAuth2LoginAuthenticationFilter.class)

        // URL 접근 제한
        .authorizeHttpRequests(auth -> auth
            // 의뢰인 로그인
            .requestMatchers(HttpMethod.GET, "/auth/login").permitAll()
            .requestMatchers("/login/oauth2/code/*").permitAll()
            .requestMatchers("/oauth2/callback/*").permitAll()

            .requestMatchers(
                "/login/oauth2/**",
                "/oauth2/authorization/**",
                "/oauth2/callback/**"
            ).permitAll()
            // 변호사 로그인
            .requestMatchers(
                "/api/lawyers/signup",
                "/api/lawyers/emails/check",
                "/api/lawyers/login"
            ).permitAll()

            .requestMatchers("/api/admin/login").permitAll()
            .requestMatchers("/api/tag/**").permitAll()
            .requestMatchers("/api/lawyers/list").permitAll()

            // refreshToken 발급
            .requestMatchers(
                "/api/auth/**"
            ).permitAll()

            // swagger
            .requestMatchers(
                "/v3/api-docs/**",
                "/swagger-ui.html",
                "/swagger-ui/**",
                "/swagger-ui/index.html",
                "/webjars/**"
            ).permitAll()

            .requestMatchers(HttpMethod.OPTIONS).permitAll()
            .anyRequest().authenticated()
        )
        .exceptionHandling(ex -> ex.authenticationEntryPoint((req, res, e) -> {
          res.setStatus(401);
          res.setContentType("application/json;charset=UTF-8");
          res.getWriter().write("{\"error\":\"unauthorized\"}");
        }));

    return http.build();
  }

  @Bean
  public OAuth2AuthorizedClientService authorizedClientService(
      ClientRegistrationRepository registrations) {
    return new InMemoryOAuth2AuthorizedClientService(registrations);
  }

  // 이 아래로 로컬 로그인 @@@@@@@@@@@@@@@@@@@@@@@
  @Bean
  public PasswordEncoder passwordEncoder(){
    return new BCryptPasswordEncoder() ;
  }

}
