package com.B204.ALaw.common.tag.controller;

import com.B204.ALaw.common.tag.dto.RecommendLawyerRequest;
import com.B204.ALaw.common.tag.dto.RecommendLawyerResponse;
import com.B204.ALaw.common.tag.dto.RecommendedLawyerDto;
import com.B204.ALaw.common.tag.dto.TagResolveRequest;
import com.B204.ALaw.common.tag.dto.TagResolveResponse;
import com.B204.ALaw.common.tag.service.TagService;
import jakarta.validation.Valid;
import java.util.List;
import java.util.NoSuchElementException;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/tag")
@RequiredArgsConstructor
public class TagController {

  private final TagService tagService;

  @PostMapping("/resolve")
  public ResponseEntity<TagResolveResponse> resolveTag(
      @RequestBody @Valid TagResolveRequest request
  ) {
    List<Long> tagIds;
    try{
      tagIds = tagService.resolveTagIds(request.getTags());
    }catch (NoSuchElementException e){
      return ResponseEntity.status(HttpStatus.NOT_FOUND).build();
    }

    TagResolveResponse.Data data = new TagResolveResponse.Data(tagIds);
    TagResolveResponse response = new TagResolveResponse(data);
    return ResponseEntity.ok(response);
  }

  @PostMapping("/recommend")
  public ResponseEntity<RecommendLawyerResponse> recommendLawyer(
    @Valid @RequestBody RecommendLawyerRequest req
  ){
    List<RecommendedLawyerDto> list = tagService.recommendLawyers(req.getTagIds(), req.getLimit());
    RecommendLawyerResponse.Data data = new RecommendLawyerResponse.Data(list);
    return ResponseEntity.ok(new RecommendLawyerResponse(data));
  }

}
