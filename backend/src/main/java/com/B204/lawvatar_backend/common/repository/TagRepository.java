package com.B204.lawvatar_backend.common.repository;

import com.B204.lawvatar_backend.common.entity.Tag;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface TagRepository extends JpaRepository<Tag, Long> {
}
