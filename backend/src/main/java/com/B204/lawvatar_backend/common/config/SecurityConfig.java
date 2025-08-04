package com.B204.lawvatar_backend.common.config;

import com.B204.lawvatar_backend.common.filter.JwtAuthenticationFilter;
import com.B204.lawvatar_backend.common.util.JwtUtil;
import com.B204.lawvatar_backend.user.auth.service.RefreshTokenService;
import com.B204.lawvatar_backend.user.client.entity.Client;
import com.B204.lawvatar_backend.user.client.repository.ClientRepository;
import com.B204.lawvatar_backend.user.client.service.ClientService;
import com.B204.lawvatar_backend.user.lawyer.entity.Lawyer;
import com.B204.lawvatar_backend.user.lawyer.service.LawyerService;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.time.Duration;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseCookie;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.dao.DaoAuthenticationProvider;
import org.springframework.security.config.Customizer;
import org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.core.Authentication;
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
      RefreshTokenService refreshTokenService
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

      String refreshToken = jwtUtil.generateRefreshToken(client.getOauthIdentifier());
      refreshTokenService.createForClient(client, refreshToken);

      ResponseCookie refreshCookie = ResponseCookie.from("refresh_token", refreshToken)
          .httpOnly(true)
          .secure(true)
          .sameSite("Strict")
          .path("/")
          .maxAge(Duration.ofDays(7))
          .build();
      res.setHeader(HttpHeaders.SET_COOKIE, refreshCookie.toString());

      // BE 개발 편의를 위해 8080으로 변경 (-> front 서버 결합 시 5173으로 변경 필요)
      String redirectUrl = UriComponentsBuilder
          .fromUriString("http://localhost:5173/user/mypage")
          .queryParam("accessToken", accessToken)
          .build().toUriString();

      res.sendRedirect(redirectUrl);
    }
  }

  @Bean
  public SecurityFilterChain filterChain(HttpSecurity http,
      OAuth2JwtSuccessHandler oauth2JwtSuccessHandler,
      LawyerService lawyerService) throws Exception {

    // OAuth2 로그인 실패 핸들러
    AuthenticationFailureHandler oauth2FailureHandler = (
        req,
        res,
        ex) ->
        res.sendError(HttpServletResponse.SC_UNAUTHORIZED, "OAuth2 Login Failed");

    // 로컬 로그인 성공 핸들러 → JWT 발급
    AuthenticationSuccessHandler lawyerLoginSuccessHandler = (
        req,
        res,
        auth) -> {
      List<String> roles = auth.getAuthorities().stream()
          .map(a -> a.getAuthority())
          .toList();

      Lawyer lawyer = lawyerService.findByLoginEmail(auth.getName());

      String accessToken = jwtUtil.generateAccessToken(String.valueOf(lawyer.getId()), roles, "LAWYER");
      String refreshToken = jwtUtil.generateRefreshToken(String.valueOf(lawyer.getId()));

      refreshTokenService.createForLawyer(lawyer, refreshToken);

      ResponseCookie refreshCookie = ResponseCookie.from("refresh_token", refreshToken)
          .httpOnly(true)
          .secure(true)
          .sameSite("Strict")
          .path("/")
          .maxAge(Duration.ofDays(7))
          .build();
      res.setHeader(HttpHeaders.SET_COOKIE, refreshCookie.toString());

      Map<String,String> body = new LinkedHashMap<>();
      body.put("accessToken",  accessToken);

      res.setStatus(HttpServletResponse.SC_OK);
      res.setContentType(MediaType.APPLICATION_JSON_VALUE);
      res.getWriter()
          .write(new ObjectMapper().writeValueAsString(body));
    };

    // 로컬 로그인 실패 핸들러
    AuthenticationFailureHandler lawyerLoginFailureHandler = (req, res, ex) -> {
      res.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
      res.setContentType("application/json");
      res.getWriter().write("{\"error\":\"Lawyer Login Failed\"}");
      res.getWriter().flush();
    };

    http
        // 1) CSRF 비활성화
        .csrf(csrf -> csrf.disable())

        // 2) CORS 활성화 (기본 CorsConfigurationSource 빈을 사용하려면 withDefaults())
        .cors(Customizer.withDefaults())

        // 로컬 로그인 설정 (formLogin)
        .formLogin(form -> form
            .loginPage("/auth/login")
            .loginProcessingUrl("/auth/login") // POST 요청
            .usernameParameter("loginEmail")
            .passwordParameter("password")
            .successHandler(lawyerLoginSuccessHandler)
            .failureHandler(lawyerLoginFailureHandler)
            .permitAll()
        )

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

        // 인증 Provider 등록 (Lawyer 전용)
        .authenticationProvider(lawyerAuthProvider(lawyerService))

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

            // .requestMatchers("/.well-known/**").permitAll()
            // .requestMatchers("/api/protected/**").authenticated()

            .requestMatchers(HttpMethod.OPTIONS).permitAll()
            .anyRequest().authenticated()
        );

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

  @Bean
  public DaoAuthenticationProvider lawyerAuthProvider(LawyerService lawyerDetailsService) {
    DaoAuthenticationProvider provider = new DaoAuthenticationProvider();
    provider.setUserDetailsService(lawyerDetailsService);
    provider.setPasswordEncoder(passwordEncoder());
    return provider;
  }

  @Bean
  public AuthenticationManager authenticationManager(AuthenticationConfiguration config) throws Exception {
    return config.getAuthenticationManager();
  }

}
