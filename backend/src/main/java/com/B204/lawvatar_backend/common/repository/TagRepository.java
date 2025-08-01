package com.B204.lawvatar_backend.common.repository;

import com.B204.lawvatar_backend.common.entity.Tag;

import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface TagRepository extends JpaRepository<Tag, Long> {
    Optional<Tag> findById(Long Id);
    List<Tag> findAllById(Iterable<Long> ids);
}