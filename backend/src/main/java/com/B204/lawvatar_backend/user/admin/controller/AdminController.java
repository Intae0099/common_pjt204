package com.B204.lawvatar_backend.user.admin.controller;

import com.B204.lawvatar_backend.user.lawyer.entity.Lawyer;
import com.B204.lawvatar_backend.user.lawyer.service.LawyerService;
import jakarta.persistence.EntityNotFoundException;
import java.util.Map;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/admin")
@RequiredArgsConstructor
public class AdminController {

  private final LawyerService lawyerService;

  @PatchMapping("/{id}/approve")
  public ResponseEntity<?> approveLawyer(@PathVariable("id") Long id) {
    try{
      Lawyer l = lawyerService.approveLawyer(id);

      return ResponseEntity.ok(Map.of(
         "lawyerId", l.getId(),
          "status", l.getCertificationStatus().name()
      ));

    }catch (EntityNotFoundException e){
      return ResponseEntity.status(HttpStatus.NOT_FOUND)
          .body(Map.of("error", e.getMessage()));
    }catch (IllegalStateException e){
      return ResponseEntity.status(HttpStatus.BAD_REQUEST)
          .body(Map.of("error", e.getMessage()));
    }

  }

}
