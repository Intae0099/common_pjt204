package com.B204.lawvatar_backend.user.lawyer.service;

import com.B204.lawvatar_backend.user.auth.repository.RefreshTokenRepository;
import com.B204.lawvatar_backend.user.lawyer.dto.LawyerUpdateDto;
import com.B204.lawvatar_backend.user.lawyer.entity.CertificationStatus;
import com.B204.lawvatar_backend.user.lawyer.entity.Lawyer;
import com.B204.lawvatar_backend.user.lawyer.entity.LawyerTag;
import com.B204.lawvatar_backend.user.lawyer.repository.LawyerRepository;
import com.B204.lawvatar_backend.user.lawyer.repository.LawyerTagRepository;
import com.B204.lawvatar_backend.user.lawyer.repository.TagRepository;
import jakarta.persistence.EntityNotFoundException;

import java.util.Base64;
import java.util.List;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.core.authority.AuthorityUtils;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class LawyerService implements UserDetailsService {

  private final LawyerRepository lawyerRepo;
  private final RefreshTokenRepository refreshTokenRepo;
  private final LawyerTagRepository lawyerTagRepo;
  private final TagRepository tagRepo;

  public LawyerService(LawyerRepository lawyerRepo,
      RefreshTokenRepository refreshTokenRepo,
      LawyerTagRepository lawyerTagRepo,
      TagRepository tagRepo) {
    this.lawyerRepo = lawyerRepo;
    this.refreshTokenRepo = refreshTokenRepo;
    this.lawyerTagRepo = lawyerTagRepo;
    this.tagRepo = tagRepo;
  }

  @Override
  public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
    Lawyer lawyer = lawyerRepo.findByLoginEmail(username)
        .orElseThrow(() -> new UsernameNotFoundException("변호사 계정이 없습니다이"));

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

  public List<Lawyer> findLawyers(List<Long> tagIds, String search) {

    boolean hasTags = tagIds != null && !tagIds.isEmpty();
    boolean hasSearch = search != null && !search.isEmpty();

    if (hasTags && hasSearch) {
      // 모든 태그 + 이름 검색
      return lawyerRepo.findByAllTagIdsAndNameContainingIgnoreCase(
          tagIds, tagIds.size(), search);
    }
    if (hasTags) {
      // 모든 태그만
      return lawyerRepo.findByAllTagIds(tagIds, tagIds.size());
    }
    if (hasSearch) {
      // 이름만 검색
      return lawyerRepo.findByNameContainingIgnoreCase(search);
    }
    // 둘 다 없으면 전체
    return lawyerRepo.findAll();

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

