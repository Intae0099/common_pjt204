package com.B204.lawvatar_backend.common.tag.service;

import com.B204.lawvatar_backend.common.tag.entity.Tag;
import com.B204.lawvatar_backend.common.tag.repository.TagRepository;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import java.util.HashSet;
import java.util.List;
import java.util.NoSuchElementException;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class TagService {

  private final TagRepository tagRepo;

  public List<Long> resolveTagIds(List<String> tagNames) {

    List<Tag> tags = tagRepo.findByNameIn(tagNames);

    if(tags.size() != new HashSet<>(tagNames).size()){
      throw new NoSuchElementException("존재하지 않는 태그 이름이 포함되어 있습니다.");
    }

    return tags.stream()
        .map(Tag::getId)
        .toList();
  }
}
