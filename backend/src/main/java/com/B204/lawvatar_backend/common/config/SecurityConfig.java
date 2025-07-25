package com.B204.lawvatar_backend.common.config;

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
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.MediaType;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.dao.DaoAuthenticationProvider;
import org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.core.Authentication;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.oauth2.client.InMemoryOAuth2AuthorizedClientService;
import org.springframework.security.oauth2.client.OAuth2AuthorizedClient;
import org.springframework.security.oauth2.client.OAuth2AuthorizedClientService;
import org.springframework.security.oauth2.client.authentication.OAuth2AuthenticationToken;
import org.springframework.security.oauth2.client.registration.ClientRegistration;
import org.springframework.security.oauth2.client.registration.ClientRegistrationRepository;
import org.springframework.security.oauth2.core.user.OAuth2User;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.AuthenticationFailureHandler;
import org.springframework.security.web.authentication.AuthenticationSuccessHandler;
import org.springframework.stereotype.Component;

@Configuration
@EnableWebSecurity
public class SecurityConfig {

  private final ClientService clientService;
  private final LawyerService lawyerService;
  private final JwtUtil jwtUtil;
  private final RefreshTokenService refreshTokenService;

  public SecurityConfig(ClientService clientService,
      LawyerService lawyerService,
      JwtUtil jwtUtil,
      RefreshTokenService refreshTokenService
  ) {
    this.clientService = clientService;
    this.lawyerService = lawyerService;
    this.jwtUtil = jwtUtil;
    this.refreshTokenService = refreshTokenService;
  }

  @Component
  public static class OAuth2JwtSuccessHandler implements AuthenticationSuccessHandler {

    private final OAuth2AuthorizedClientService authorizedClientService;
    private final ClientRepository clientRepository;
    private final JwtUtil jwtUtil;
    private final RefreshTokenService refreshTokenService;
    private final ClientRegistrationRepository clientRegRepo; // UserNameAttributeName 조회용

    public OAuth2JwtSuccessHandler(
        OAuth2AuthorizedClientService authorizedClientService,
        ClientRepository clientRepository,
        JwtUtil jwtUtil,
        RefreshTokenService refreshTokenService, ClientRegistrationRepository clientRegRepo
    ) {
      this.authorizedClientService = authorizedClientService;
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
      String principal = oauthToken.getName();

      // 여기서 소셜 토큰 꺼내기
      OAuth2AuthorizedClient authorizedClient = authorizedClientService.loadAuthorizedClient(regId, principal);
      String socialAccessToken  = authorizedClient.getAccessToken().getTokenValue();
      String socialRefreshToken = authorizedClient.getRefreshToken().getTokenValue();

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

      // 4) 서버용 JWT Access Token 생성
      String accessToken = jwtUtil.generateAccessToken(
          client.getOauthIdentifier(),
          List.of("ROLE_USER"),
          "CLIENT"
      );
      // 5) 서버용 Refresh Token 생성·저장
      String refreshToken = jwtUtil.generateRefreshToken(client.getOauthIdentifier());
      refreshTokenService.createForClient(client, refreshToken);

      Map<String, String> responseBody = new LinkedHashMap<>();
      responseBody.put("accessToken", accessToken);
      responseBody.put("refreshToken", refreshToken);
      responseBody.put("socialAccessToken", socialAccessToken);
      if (socialRefreshToken != null) {
        responseBody.put("socialRefreshToken", socialRefreshToken);
      }

      res.setStatus(HttpServletResponse.SC_OK);
      res.setContentType(MediaType.APPLICATION_JSON_VALUE);
      res.getWriter().write(new ObjectMapper().writeValueAsString(responseBody));
    }
  }

  @Bean
  public SecurityFilterChain filterChain(HttpSecurity http,
      OAuth2JwtSuccessHandler oauth2JwtSuccessHandler,
      LawyerService lawyerService) throws Exception {

    // OAuth2 로그인 실패 핸들러
    AuthenticationFailureHandler oauth2FailureHandler = (req, res, ex) ->
        res.sendError(HttpServletResponse.SC_UNAUTHORIZED, "OAuth2 Login Failed");

    // 로컬 로그인 성공 핸들러 → JWT 발급
    AuthenticationSuccessHandler lawyerLoginSuccessHandler = (req, res, auth) -> {
      String username = auth.getName();
      List<String> roles = auth.getAuthorities().stream()
          .map(a -> a.getAuthority())
          .toList();

      String accessToken = jwtUtil.generateAccessToken(username, roles, "LAWYER");
      String refreshToken = jwtUtil.generateRefreshToken(username);

      Lawyer lawyer = lawyerService.findByLoginEmail(username);
      refreshTokenService.createForLawyer(lawyer, refreshToken);

      Map<String,String> body = new LinkedHashMap<>();
      body.put("accessToken",  accessToken);
      body.put("refreshToken", refreshToken);

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

    // DaoAuthenticationProvider (Lawyer 전용)
    DaoAuthenticationProvider daoProvider = new DaoAuthenticationProvider();
    daoProvider.setUserDetailsService(lawyerService);
    daoProvider.setPasswordEncoder(passwordEncoder());

    http
        // CSRF 비활성화
        .csrf(csrf -> csrf.disable())

        // 로컬 로그인 설정 (formLogin)
        .formLogin(form -> form
            .loginProcessingUrl("/auth/login") // POST 요청
            .usernameParameter("loginEmail")
            .passwordParameter("password")
            .successHandler(lawyerLoginSuccessHandler)
            .failureHandler(lawyerLoginFailureHandler)
        )

        // OAuth2 로그인 설정
        .oauth2Login(oauth -> oauth
            .userInfoEndpoint(u -> u.userService(clientService))
            .successHandler(oauth2JwtSuccessHandler)
            .failureHandler(oauth2FailureHandler)
        )

        // 세션 설정 (기존 유지: OAuth2용 state 저장 가능)
        .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.IF_REQUIRED))

        // 인증 Provider 등록 (Lawyer 전용)
        .authenticationProvider(lawyerAuthProvider(lawyerService))


        // JWT 필터: OAuth2 로그인 이후에 추가
        // .addFilterAfter(new JwtAuthenticationFilter(jwtUtil), OAuth2LoginAuthenticationFilter.class)

        // URL 접근 제한
        .authorizeHttpRequests(auth -> auth
            .requestMatchers( "/login/oauth2/**").permitAll()
            .requestMatchers("/.well-known/**").permitAll()
            .requestMatchers("/api/protected/**").authenticated()
            .requestMatchers("/auth/**", "/oauth2/**").permitAll()
            .anyRequest().permitAll()
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
