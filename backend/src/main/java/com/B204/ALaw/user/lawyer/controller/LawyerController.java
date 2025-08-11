package com.B204.ALaw.user.lawyer.controller;

import com.B204.ALaw.common.principal.LawyerPrincipal;
import com.B204.ALaw.user.lawyer.dto.LawyerInfoDto;
import com.B204.ALaw.user.lawyer.dto.LawyerLoginDto;
import com.B204.ALaw.user.lawyer.dto.LawyerSearchDto;
import com.B204.ALaw.user.lawyer.dto.LawyerSignupDto;
import com.B204.ALaw.user.lawyer.dto.LawyerUpdateDto;
import com.B204.ALaw.user.lawyer.dto.LoginResponseDto;
import com.B204.ALaw.user.lawyer.dto.LoginResult;
import com.B204.ALaw.user.lawyer.dto.UnavailabilitySlotDto;
import com.B204.ALaw.user.lawyer.entity.CertificationStatus;
import com.B204.ALaw.user.lawyer.entity.Lawyer;
import com.B204.ALaw.user.lawyer.repository.LawyerRepository;
import com.B204.ALaw.user.lawyer.repository.LawyerTagRepository;
import com.B204.ALaw.common.tag.repository.TagRepository;
import com.B204.ALaw.user.lawyer.service.LawyerService;
import com.B204.ALaw.user.lawyer.service.UnavailabilityService;
import jakarta.validation.Valid;
import java.util.List;
import java.util.Map;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequestMapping("/api/lawyers")
public class LawyerController {
  private final LawyerRepository lawyerRepo;
  private final LawyerTagRepository lawyerTagRepo;
  private final TagRepository tagRepo;

  private final LawyerService lawyerService;
  private final UnavailabilityService unavailabilityService;

  private final PasswordEncoder pwEncoder;
  private final AuthenticationManager authManager;

  public LawyerController(LawyerRepository lawyerRepo,
      LawyerTagRepository lawyerTagRepo,
      TagRepository tagRepo,
      LawyerService lawyerService, UnavailabilityService unavailabilityService,
      PasswordEncoder pwEncoder,
      @Qualifier("lawyerAuthenticationManager") AuthenticationManager authManager
      ) {
    this.lawyerRepo = lawyerRepo;
    this.lawyerTagRepo = lawyerTagRepo;
    this.tagRepo = tagRepo;
    this.lawyerService = lawyerService;
    this.unavailabilityService = unavailabilityService;
    this.pwEncoder = pwEncoder;
    this.authManager = authManager;
  }

  @PostMapping("/signup")
  public ResponseEntity<?> signup(
      @RequestBody LawyerSignupDto dto
  ) {

    lawyerService.registerLawyer(dto);
    return ResponseEntity.status(HttpStatus.CREATED).build();

  }

  @PostMapping("/emails/check")
  public ResponseEntity<?> isEmailAvailable(
      @RequestBody Map<String, String> body
  ){
    String loginEmail = body.get("loginEmail");

    boolean isAvailable = !lawyerRepo.existsByLoginEmail(loginEmail);
    Map<String, String> response = Map.of("isAvailable", String.valueOf(isAvailable));

    return ResponseEntity.ok(response);
  }

//  @PostMapping("/login")
//  public ResponseEntity<?> login(
//      @Valid @RequestBody LawyerLoginDto dto
//  ) {
//    try {
//      // 1. 인증 시도
//      Authentication authentication = authManager.authenticate(
//          new UsernamePasswordAuthenticationToken(dto.getLoginEmail(), dto.getPassword())
//      );
//
//      Lawyer lawyer = lawyerService.findByLoginEmail(authentication.getName());
//
//      System.out.println("변호사 / 현 상태 :  " + lawyer.getCertificationStatus());
//
//      if (lawyer.getCertificationStatus() == CertificationStatus.PENDING) {
//        return ResponseEntity
//            .status(HttpStatus.FORBIDDEN)
//            .body(Map.of("error", "계정 승인 대기 중입니다."));
//      }
//      if (lawyer.getCertificationStatus() == CertificationStatus.REJECTED) {
//        return ResponseEntity
//            .status(HttpStatus.FORBIDDEN)
//            .body(Map.of("error", "승인 거부된 계정입니다."));
//      }
//
//      LoginResult result = lawyerService.loginLawyer(authentication);
//
//      return ResponseEntity.ok()
//          .header(HttpHeaders.SET_COOKIE, result.getRefreshCooktie())
//          .body(new LoginResponseDto(result.getAccessToken(), result.getName()));
//
//    } catch (BadCredentialsException e) {
//      return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
//          .body(Map.of("error", "무엇인가 올바르지 않다."));
//    }catch (Exception e) {
//      return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
//          .body(Map.of("error", e.getMessage()));
//    }
//  }

  @GetMapping("/me")
  @PreAuthorize("hasRole('LAWYER')")
  public ResponseEntity<?> getMyInfo(
    @AuthenticationPrincipal LawyerPrincipal lawyer
  ) {
    Lawyer fullLawyer = lawyerRepo.findById(lawyer.getId())
        .orElseThrow(() -> new UsernameNotFoundException("해당 변호사를 찾을 수 없습니다."));

    return ResponseEntity.ok(LawyerInfoDto.from(fullLawyer));
  }

  @PatchMapping("/me/edit")
  @PreAuthorize("hasRole('LAWYER')")
  public ResponseEntity<Void> updateMyInfo(
      @Valid @RequestBody LawyerUpdateDto dto,
      @AuthenticationPrincipal LawyerPrincipal lawyer
  ) {

    lawyerService.updateLawyerInfo(lawyer.getId(), dto);
    return ResponseEntity.ok().build();

  }

  @DeleteMapping("/me")
  @PreAuthorize("hasRole('LAWYER')")
  public ResponseEntity<Void> deleteMyAccount(
     @AuthenticationPrincipal LawyerPrincipal lawyer
  ){
    Long lawyerId = lawyer.getId();
    lawyerService.deleteLawyerById(lawyerId);

    return ResponseEntity.noContent().build();
  }

  @GetMapping("/list")
  public ResponseEntity<List<LawyerSearchDto>> getLawyers(
    @RequestParam(value = "tags" , required = false) List<Long> tagIds,
    @RequestParam(value = "search", required = false) String search,
      @RequestParam(value = "sortBy", defaultValue = "name") String sortBy
    ){

    List<Lawyer> lawyers = lawyerService.findLawyers(tagIds, search, sortBy);

    List<LawyerSearchDto> result = lawyers.stream()
        .map(LawyerSearchDto::from)
        .toList();

    return ResponseEntity.ok(result);
  }

  @GetMapping("/{lawyerId}")
  ResponseEntity<LawyerSearchDto> getLawyerById(
      @PathVariable Long lawyerId
  ){
    Lawyer lawyer = lawyerRepo.findById(lawyerId)
        .orElseThrow(() ->
            new ResponseStatusException(HttpStatus.NOT_FOUND,
                "변호사를 찾을 수 없습니다. id=" + lawyerId));

    if (lawyer.getCertificationStatus() != CertificationStatus.APPROVED) {
      throw new ResponseStatusException(
          HttpStatus.NOT_FOUND,
          "승인된 변호사를 찾을 수 없습니다. id=" + lawyerId
      );
    }

    // 3) DTO 변환 후 응답
    return ResponseEntity.ok(LawyerSearchDto.from(lawyer));
  }

  @GetMapping("/{lawyerId}/unavailable-slot")
  ResponseEntity<List<UnavailabilitySlotDto>> getUnavailibility(
      @PathVariable Long lawyerId
  ){
    List<UnavailabilitySlotDto> slots = unavailabilityService.getSlotsForLawyer(lawyerId);
    return ResponseEntity.ok(slots);
  }

}