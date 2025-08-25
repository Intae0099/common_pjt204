package com.B204.ALaw.user.lawyer.service;

import com.B204.ALaw.common.tag.entity.Tag;
import com.B204.ALaw.common.util.JwtUtil;
import com.B204.ALaw.user.auth.repository.RefreshTokenRepository;
import com.B204.ALaw.user.auth.service.RefreshTokenService;
import com.B204.ALaw.user.lawyer.dto.LawyerSignupDto;
import com.B204.ALaw.user.lawyer.dto.LawyerUpdateDto;
import com.B204.ALaw.user.lawyer.dto.LoginResult;
import com.B204.ALaw.user.lawyer.entity.CertificationStatus;
import com.B204.ALaw.user.lawyer.entity.Lawyer;
import com.B204.ALaw.user.lawyer.entity.LawyerTag;
import com.B204.ALaw.user.lawyer.repository.LawyerRepository;
import com.B204.ALaw.user.lawyer.repository.LawyerTagRepository;
import com.B204.ALaw.common.tag.repository.TagRepository;
import jakarta.persistence.EntityNotFoundException;
import java.time.Duration;
import java.util.Base64;
import java.util.List;
import java.util.stream.Collectors;
import org.springframework.data.domain.Sort;
import org.springframework.data.domain.Sort.Direction;
import org.springframework.http.ResponseCookie;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.authority.AuthorityUtils;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.StringUtils;

@Service
public class LawyerService implements UserDetailsService {

  private final RefreshTokenService refreshTokenService;

  private final LawyerRepository lawyerRepo;
  private final RefreshTokenRepository refreshTokenRepo;
  private final LawyerTagRepository lawyerTagRepo;
  private final TagRepository tagRepo;

  private final JwtUtil jwtUtil;
  private final PasswordEncoder pwEncoder;

  public LawyerService(RefreshTokenService refreshTokenService, LawyerRepository lawyerRepo,
      RefreshTokenRepository refreshTokenRepo,
      LawyerTagRepository lawyerTagRepo,
      TagRepository tagRepo, JwtUtil jwtUtil, PasswordEncoder pwEncoder) {
    this.refreshTokenService = refreshTokenService;
    this.lawyerRepo = lawyerRepo;
    this.refreshTokenRepo = refreshTokenRepo;
    this.lawyerTagRepo = lawyerTagRepo;
    this.tagRepo = tagRepo;
    this.jwtUtil = jwtUtil;
    this.pwEncoder = pwEncoder;
  }

  @Transactional
  public void registerLawyer(LawyerSignupDto dto) {

    Lawyer l = new Lawyer();
    l.setLoginEmail(dto.getLoginEmail());
    l.setPasswordHash(pwEncoder.encode(dto.getPassword()));
    l.setName(dto.getName());
    l.setIntroduction(dto.getIntroduction());
    l.setExam(dto.getExam());
    l.setRegistrationNumber(dto.getRegistrationNumber());
    l.setCertificationStatus(CertificationStatus.PENDING);
    l.setConsultationCount(0);

    if (StringUtils.hasText(dto.getPhotoBase64())) {
      byte[] img = Base64.getDecoder().decode(dto.getPhotoBase64());
      l.setPhoto(img);
    }

    lawyerRepo.save(l);

    List<Tag> tags = tagRepo.findAllById(dto.getTags());
    List<LawyerTag> ltList = tags.stream()
        .map(tag -> LawyerTag.builder()
            .lawyer(l)
            .tag(tag)
            .build())
        .collect(Collectors.toList());

    lawyerTagRepo.saveAll(ltList);
  }

  public LoginResult loginLawyer(Authentication authentication) {
    // 1) 인증된 사용자 정보 조회
    String loginEmail = authentication.getName();
    Lawyer lawyer = findByLoginEmail(loginEmail);

    // 2) 권한 목록 준비
    List<String> roles = authentication.getAuthorities().stream()
        .map(GrantedAuthority::getAuthority)
        .toList();

    // 3) 토큰 생성
    String accessToken = jwtUtil.generateAccessToken(
        String.valueOf(lawyer.getId()), roles, "LAWYER");
    String refreshToken = jwtUtil.generateRefreshToken(String.valueOf(lawyer.getId()), "LAWYER");

    // 4) DB에 리프레시 토큰 저장
    refreshTokenService.createForLawyer(lawyer, refreshToken);

    // 5) 쿠키 생성
    ResponseCookie refreshCookie = ResponseCookie.from("refresh_token", refreshToken)
        .httpOnly(true)
        .secure(true)
        .sameSite("None")
        .path("/")
        .maxAge(Duration.ofDays(7))
        .build();

    // 6) 결과 반환
    return new LoginResult(
        accessToken,
        refreshCookie.toString(),
        loginEmail
    );
  }

  @Override
  public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
    Lawyer lawyer = lawyerRepo.findByLoginEmail(username)
        .orElseThrow(() -> new UsernameNotFoundException("변호사 계정이 없습니다이"));

    // 🔍 진짜 비교 상태 확인
    System.out.println("✅ [DEBUG] loginEmail = " + lawyer.getLoginEmail());
    System.out.println("✅ [DEBUG] certStatus (Enum) = " + lawyer.getCertificationStatus());
    System.out.println("✅ [DEBUG] certStatus name = " + lawyer.getCertificationStatus().name());
    System.out.println("✅ [DEBUG] certStatus equals APPROVED? = " + (lawyer.getCertificationStatus() == CertificationStatus.APPROVED));


    if(lawyer.getCertificationStatus() != CertificationStatus.APPROVED) {
      throw new BadCredentialsException("인증되지 않은 계정입니다. 관리자에게 문의하세요.");
    }

    return new org.springframework.security.core.userdetails.User(
        lawyer.getLoginEmail(),
        lawyer.getPasswordHash(),
        AuthorityUtils.createAuthorityList("ROLE_LAWYER")
    );
  }

  public Lawyer findByLoginEmail(String loginEmail) {
    return lawyerRepo.findByLoginEmail(loginEmail)
        .orElseThrow(() -> new UsernameNotFoundException("Lawyer not found: " + loginEmail));
  }

  public Lawyer approveLawyer(Long id) {
    Lawyer l = lawyerRepo.findById(id)
        .orElseThrow(() -> new EntityNotFoundException("해당 변호사는 존재하지 않습니다. : " + id));

    if(l.getCertificationStatus() != CertificationStatus.PENDING){
      throw new IllegalStateException("해당 변호사는 대기 중이 아닙니다 : " + id);
    }

    l.setCertificationStatus(CertificationStatus.APPROVED);
    return lawyerRepo.save(l);
  }

  @Transactional
  public void updateLawyerInfo(Long lawyerId, LawyerUpdateDto dto) {
    Lawyer lawyer = lawyerRepo.findById(lawyerId)
        .orElseThrow(() -> new EntityNotFoundException("Lawyer not found"));

    // **null 체크 후에만 setter 호출**
    if (dto.getName() != null) {
      lawyer.setName(dto.getName());
    }
    if (dto.getIntroduction() != null) {
      lawyer.setIntroduction(dto.getIntroduction());
    }
    if (dto.getExam() != null) {
      lawyer.setExam(dto.getExam());
    }
    if (dto.getRegistrationNumber() != null) {
      lawyer.setRegistrationNumber(dto.getRegistrationNumber());
    }

    if (dto.getTags() != null) {
      // 기존 태그 클리어
      lawyer.getTags().clear();
      // 새 태그 매핑
      for (Long tagId : dto.getTags()) {
        tagRepo.findById(tagId).ifPresent(tag -> {
          LawyerTag lt = new LawyerTag();
          lt.setLawyer(lawyer);
          lt.setTag(tag);
          lawyer.getTags().add(lt);
        });
      }
    }

    if (dto.getPhotoBase64() != null) {
      byte[] img = Base64.getDecoder().decode(dto.getPhotoBase64());
      lawyer.setPhoto(img);
    }

  }

  @Transactional
  public void deleteLawyerById(Long id) {
    lawyerTagRepo.deleteByLawyerId(id);

    refreshTokenRepo.deleteByLawyerId(id);

    lawyerRepo.deleteById(id);
  }

  public List<Lawyer> findLawyers(
      List<Long> tagIds,
      String search,
      String sortBy
  ) {

    boolean hasTags = tagIds != null && !tagIds.isEmpty();
    boolean hasSearch = search != null && !search.isEmpty();

    // sort 객체 생성
    Sort sort = "name".equals(sortBy)
        ? Sort.by(Direction.ASC, "name")
        : Sort.by(Direction.DESC, "consultationCount");

    List<Lawyer> lawyers ;
    if (hasTags && hasSearch) {
      // 모든 태그 + 이름 검색
      lawyers = lawyerRepo.findByAllTagIdsAndNameContainingIgnoreCase(
          tagIds, tagIds.size(), search, sort);
    }
    else if (hasTags) {
      // 모든 태그만
      lawyers = lawyerRepo.findByAllTagIds(tagIds, tagIds.size(), sort);
    }
    else if (hasSearch) {
      // 이름만 검색
      lawyers = lawyerRepo.findByNameContainingIgnoreCase(search, sort);
    }
    // 둘 다 없으면 전체
    else lawyers =  lawyerRepo.findAll(sort);

    return lawyers.stream()
        .filter(l -> l.getCertificationStatus() == CertificationStatus.APPROVED)
        .toList();
  }

  public Lawyer rejectLawyer(Long id) {
    Lawyer l = lawyerRepo.findById(id)
        .orElseThrow(() -> new EntityNotFoundException("해당 변호사는 존재하지 않습니다. : " + id));

    if(l.getCertificationStatus() != CertificationStatus.PENDING){
      throw new IllegalStateException("해당 변호사는 대기 중이 아닙니다 : " + id);
    }

    l.setCertificationStatus(CertificationStatus.REJECTED);
    return lawyerRepo.save(l);
  }

  public List<Lawyer> findByCertificationStatus(CertificationStatus status) {

    return lawyerRepo.findByCertificationStatus(status);

  }

}

