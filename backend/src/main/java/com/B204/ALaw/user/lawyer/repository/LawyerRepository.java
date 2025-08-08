package com.B204.ALaw.user.lawyer.repository;

import com.B204.ALaw.user.lawyer.entity.CertificationStatus;
import com.B204.ALaw.user.lawyer.entity.Lawyer;
import java.util.List;
import java.util.Optional;
import org.springframework.data.domain.Sort;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface LawyerRepository extends JpaRepository<Lawyer, Long> {

  Optional<Lawyer> findByLoginEmail(String loginEmail);

  boolean existsByLoginEmail(String loginEmail);

  List<Lawyer> findByNameContainingIgnoreCase(String search, Sort sort);

  /**
   * 태그 리스트에 포함된 모든 tagId를 가진 변호사만 조회
   */
  @Query("""
        SELECT l
          FROM Lawyer l
          JOIN l.tags lt
         WHERE lt.tag.id IN :tagIds
         GROUP BY l.id
        HAVING COUNT(DISTINCT lt.tag.id) = :tagCount
        """)
  List<Lawyer> findByAllTagIds(
      @Param("tagIds") List<Long> tagIds,
      @Param("tagCount") long tagCount,
      Sort sort);

  /**
   // 모든 태그 + 이름 검색 조합
   */
  @Query("""
        SELECT l
          FROM Lawyer l
          JOIN l.tags lt
         WHERE lt.tag.id IN :tagIds
           AND LOWER(l.name) LIKE CONCAT('%', LOWER(:search), '%')
         GROUP BY l.id
        HAVING COUNT(DISTINCT lt.tag.id) = :tagCount
        """)
  List<Lawyer> findByAllTagIdsAndNameContainingIgnoreCase(
      @Param("tagIds") List<Long> tagIds,
      @Param("tagCount") long tagCount,
      @Param("search") String search,
      Sort sort);

  List<Lawyer> findByCertificationStatus(CertificationStatus status);

  List<Lawyer> findByCertificationStatus(CertificationStatus status, Sort sort);
}
