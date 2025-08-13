package com.B204.ALaw.common.tag.service;

import com.B204.ALaw.common.tag.dto.RecommendedLawyerDto;
import com.B204.ALaw.common.tag.entity.Tag;
import com.B204.ALaw.common.tag.repository.TagRepository;
import com.B204.ALaw.user.lawyer.entity.CertificationStatus;
import com.B204.ALaw.user.lawyer.entity.Lawyer;
import com.B204.ALaw.user.lawyer.repository.LawyerRepository;

import java.util.Comparator;
import java.util.HashSet;
import java.util.List;
import java.util.NoSuchElementException;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Sort;
import org.springframework.data.domain.Sort.Direction;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class TagService {

  private final TagRepository tagRepo;
  private final LawyerRepository lawyerRepo;

  public List<Long> resolveTagIds(List<String> tagNames) {

    List<Tag> tags = tagRepo.findByNameIn(tagNames);

    if(tags.size() != new HashSet<>(tagNames).size()){
      throw new NoSuchElementException("존재하지 않는 태그 이름이 포함되어 있습니다.");
    }

    return tags.stream()
        .map(Tag::getId)
        .toList();
  }

  public List<RecommendedLawyerDto> recommendLawyers(List<Long> tagIds, int limit) {
    // 1) 전체 APPROVED 변호사 조회
    List<Lawyer> all = lawyerRepo.findByCertificationStatus(
        CertificationStatus.APPROVED, Sort.by(Direction.DESC, "consultationCount")
    );

    // 2) 각 변호사별 일치 태그 개수 계산
    List<LawyerMatch> matches = all.stream()
        .map(lawyer -> {
          // lawyer.getTags() → List<ApplicationTag> → tag.getTag().getId()
          List<Long> own = lawyer.getTags().stream()
              .map(lt -> lt.getTag().getId())
              .toList();
          long matchCount = tagIds.stream().filter(own::contains).count();
          return new LawyerMatch(lawyer, matchCount);
        })
        // 일치 태그 수 내림차순, 이미 consultationCount 내림차순으로 all이 정렬되어 있으므로
        // matchCount 같으면 기존 순서 유지 (consultationCount 기준)
        .filter(m -> m.matchCount > 0)
        .sorted(Comparator.comparingLong(LawyerMatch::getMatchCount).reversed())
        .toList();

    // 3) limit 개수만큼 자르고 DTO로 변환
    return matches.stream()
        .limit(limit)
        .map(m -> RecommendedLawyerDto.builder()
            .lawyerId(m.lawyer.getId())
            .name(m.lawyer.getName())
            .introduction(m.lawyer.getIntroduction())
            .exam(m.lawyer.getExam())
            .tags(
                m.lawyer.getTags().stream()
                    .map(lt -> lt.getTag().getId())
                    .toList()
            )
            .consultationCnt(m.lawyer.getConsultationCount())
            .build()
        )
        .toList();
  }

  // 내부 헬퍼 클래스
  @RequiredArgsConstructor
  private static class LawyerMatch {
    private final Lawyer lawyer;
    private final long matchCount;
    public long getMatchCount() { return matchCount; }
  }

}
