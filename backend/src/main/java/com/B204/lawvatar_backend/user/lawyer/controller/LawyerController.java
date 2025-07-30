package com.B204.lawvatar_backend.user.lawyer.controller;

import com.B204.lawvatar_backend.common.entity.Tag;
import com.B204.lawvatar_backend.common.principal.LawyerPrincipal;
import com.B204.lawvatar_backend.common.util.JwtUtil;
import com.B204.lawvatar_backend.user.auth.service.RefreshTokenService;
import com.B204.lawvatar_backend.user.lawyer.dto.LawyerInfoDto;
import com.B204.lawvatar_backend.user.lawyer.dto.LawyerLoginDto;
import com.B204.lawvatar_backend.user.lawyer.dto.LawyerSearchDto;
import com.B204.lawvatar_backend.user.lawyer.dto.LawyerSignupDto;
import com.B204.lawvatar_backend.user.lawyer.dto.LawyerUpdateDto;
import com.B204.lawvatar_backend.user.lawyer.entity.CertificationStatus;
import com.B204.lawvatar_backend.user.lawyer.entity.Lawyer;
import com.B204.lawvatar_backend.user.lawyer.entity.LawyerTag;
import com.B204.lawvatar_backend.user.lawyer.repository.LawyerRepository;
import com.B204.lawvatar_backend.user.lawyer.repository.LawyerTagRepository;
import com.B204.lawvatar_backend.user.lawyer.repository.TagRepository;
import com.B204.lawvatar_backend.user.lawyer.service.LawyerService;
import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.Valid;
import java.time.Duration;
import java.util.ArrayList;
import java.util.Base64;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseCookie;
import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/lawyers")
public class LawyerController {
  private final LawyerRepository lawyerRepo;
  private final LawyerTagRepository lawyerTagRepo;
  private final TagRepository tagRepo;

  private final LawyerService lawyerService;
  private final RefreshTokenService refreshTokenService;

  private final PasswordEncoder pwEncoder;
  private final JwtUtil jwtUtil;
  private final AuthenticationManager authManager;

  public LawyerController(LawyerRepository lawyerRepo,
      LawyerTagRepository lawyerTagRepo,
      TagRepository tagRepo, LawyerService lawyerService, RefreshTokenService refreshTokenService,
      PasswordEncoder pwEncoder,
      AuthenticationManager authManager,
      JwtUtil jwtUtil) {
    this.lawyerRepo = lawyerRepo;
    this.lawyerTagRepo = lawyerTagRepo;
    this.tagRepo = tagRepo;
    this.lawyerService = lawyerService;
    this.refreshTokenService = refreshTokenService;

    this.pwEncoder = pwEncoder;
    this.jwtUtil = jwtUtil;
    this.authManager = authManager;
  }

  @PostMapping("/signup")
  public ResponseEntity<?> signup(@RequestBody LawyerSignupDto dto) {

    Lawyer l = new Lawyer();
    l.setLoginEmail(dto.getLoginEmail());
    l.setPasswordHash(pwEncoder.encode(dto.getPassword()));
    l.setName(dto.getName());
    l.setIntroduction(dto.getIntroduction());
    l.setExam(dto.getExam());
    l.setRegistrationNumber(dto.getRegistrationNumber());
    l.setCertificationStatus(CertificationStatus.PENDING);
    l.setConsultationCount(0);
    l.setTags(new ArrayList<>());

    // 3) photoBase64 가 있으면 디코딩하여 설정
    if (dto.getPhotoBase64() != null && !dto.getPhotoBase64().isBlank()) {
      byte[] img = Base64.getDecoder().decode(dto.getPhotoBase64());
      l.setPhoto(img);
    }

    lawyerRepo.save(l);

    // 가입 승인 API 생기면 옮겨야 함
    List<Tag> tags = tagRepo.findAllById(dto.getTags());
    if (tags.isEmpty()) {
      return ResponseEntity
          .badRequest()
          .body("유효한 태그가 하나도 없습니다.");
    }

    List<LawyerTag> ltList = tags.stream()
        .map(tag -> LawyerTag.builder()
            .lawyer(l)
            .tag(tag)
            .build())
        .collect(Collectors.toList());
    lawyerTagRepo.saveAll(ltList);
    // 가입 승인 API 생기면 옮겨야 함. #################################


    return ResponseEntity.ok("가입 신청이 완료되었습니다.");
  }

  @PostMapping("/emails/check")
  public ResponseEntity<?> isEmailAvailable(
      @JsonProperty("loginEmail") String loginEmail){
    boolean isAvailable = lawyerRepo.existsByLoginEmail(loginEmail);

    Map<String, String> response = Map.of("isAvailable", String.valueOf(isAvailable));

    return ResponseEntity.ok(response);
  }

  @PostMapping("/login")
  public ResponseEntity<?> loginJson(@RequestBody LawyerLoginDto dto) {
    if (dto.getLoginEmail() == null || dto.getPassword() == null) {
      return ResponseEntity.badRequest().body(Map.of("error", "이메일 또는 비밀번호 누락"));
    }

    try {
      // 1. 인증 시도
      Authentication authentication = authManager.authenticate(
          new UsernamePasswordAuthenticationToken(dto.getLoginEmail(), dto.getPassword())
      );

      Lawyer lawyer = lawyerService.findByLoginEmail(authentication.getName());

      // 2. Access Token 생성 (userType은 "LAWYER")
      String accessToken = jwtUtil.generateAccessToken(
          String.valueOf(lawyer.getId()),
          authentication.getAuthorities().stream()
              .map(GrantedAuthority::getAuthority)
              .toList(),
          "LAWYER"
      );

      // 3. Refresh Token 생성 및 DB 저장
      String refreshToken = jwtUtil.generateRefreshToken(authentication.getName());
      // 기존 토큰 삭제 후 새로 저장
      refreshTokenService.createForLawyer(lawyer, refreshToken);

      ResponseCookie refreshCookie = ResponseCookie.from("refresh_token", refreshToken)
          .httpOnly(true)
          .secure(true)
          .sameSite("Strict")
          .path("/")
          .maxAge(Duration.ofDays(7))
          .build();

      // 5. 응답에 토큰 포함
      Map<String, String> body = new LinkedHashMap<>();
      body.put("accessToken",  accessToken);
      body.put("name",     authentication.getName());

      return ResponseEntity.ok()
          .header(HttpHeaders.SET_COOKIE, refreshCookie.toString())
          .body(body);

    } catch (BadCredentialsException e) {
      return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
          .body(Map.of("error", "비밀번호가 올바르지 않다."));
    } catch (UsernameNotFoundException e) {
      return ResponseEntity.status(HttpStatus.NOT_FOUND)
          .body(Map.of("error", "그런 계정은 없다."));
    } catch (Exception e) {
      return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
          .body(Map.of("error", "아무튼 실패"));
    }
  }

  @GetMapping("/me")
  public ResponseEntity<?> getMyInfo(Authentication authentication) {
    if (!(authentication.getPrincipal() instanceof LawyerPrincipal principal)) {
      return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
    }

    Lawyer fullLawyer = lawyerRepo.findById(principal.getId())
        .orElseThrow(() -> new UsernameNotFoundException("해당 변호사를 찾을 수 없습니다."));
    return ResponseEntity.ok(LawyerInfoDto.from(fullLawyer));
  }

  @PatchMapping("/me/edit")
  public ResponseEntity<Void> updateMyInfo(
      @Valid @RequestBody LawyerUpdateDto dto,
      @AuthenticationPrincipal LawyerPrincipal principal) {
    lawyerService.updateLawyerInfo(principal.getId(), dto);
    return ResponseEntity.ok().build();
  }

  @DeleteMapping("/me")
  public ResponseEntity<Void> deleteMyAccount(Authentication authentication){

    if(!(authentication.getPrincipal() instanceof LawyerPrincipal lawyer)) {
      return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
    }

    Long lawyerId = lawyer.getId();
    lawyerService.deleteLawyerById(lawyerId);
    return ResponseEntity.noContent().build();
  }

  @GetMapping("/list")
  public ResponseEntity<List<LawyerSearchDto>> getLawyers(
    @RequestParam(value = "tags" , required = false) List<Long> tagIds,
    @RequestParam(value = "search", required = false) String search
    ){

    List<Lawyer> lawyers = lawyerService.findLawyers(tagIds, search);

    List<LawyerSearchDto> result = lawyers.stream()
        .map(LawyerSearchDto::from)
        .toList();

    return ResponseEntity.ok(result);

  }
}