package com.B204.lawvatar_backend.user.client.controller;


import com.B204.lawvatar_backend.appointment.repository.AppointmentRepository;
import com.B204.lawvatar_backend.common.principal.ClientPrincipal;
import com.B204.lawvatar_backend.common.principal.LawyerPrincipal;
import com.B204.lawvatar_backend.common.util.JwtUtil;
import com.B204.lawvatar_backend.user.client.dto.ClientSearchDto;
import com.B204.lawvatar_backend.user.client.dto.ClientUpdateDto;
import com.B204.lawvatar_backend.user.client.entity.Client;
import com.B204.lawvatar_backend.user.client.repository.ClientRepository;
import com.B204.lawvatar_backend.user.client.service.ClientService;
import jakarta.validation.Valid;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequestMapping("/api/clients")
public class ClientController {

  private final ClientService clientService;

  private final ClientRepository clientRepo;
  private final AppointmentRepository appointmentRepo;

  public ClientController(ClientService clientService, ClientRepository clientRepo, AppointmentRepository appointmentRepo) {
    this.clientService = clientService;
    this.clientRepo = clientRepo;
    this.appointmentRepo = appointmentRepo;
  }

  @GetMapping("/me")
  @PreAuthorize("hasRole('CLIENT')")
  public ResponseEntity<Map<String, Object>> getMyInfo(
      @AuthenticationPrincipal ClientPrincipal client
  ){

    Map<String ,Object> response = new LinkedHashMap<>();
    response.put("clientId", client.getUsername());
    response.put("oauthName", client.getOauthtName());
    response.put("oauthProvider", client.getOauthProvider());
    response.put("oauthIdentifier", client.getOauthIndentifier());

    return ResponseEntity.ok(response);
  }


  @PatchMapping("/me/edit")
  @PreAuthorize("hasRole('CLIENT')")
  public ResponseEntity<Void> updateMyInfo(
      @Valid @RequestBody ClientUpdateDto dto,
      @AuthenticationPrincipal ClientPrincipal principal) {

    clientService.updateClientInfo(principal.getId(), dto);
    return ResponseEntity.ok().build();
  }

  @DeleteMapping("/me")
  @PreAuthorize("hasRole('CLIENT')")
  public ResponseEntity<Void> deleteMyAccount(
      @AuthenticationPrincipal ClientPrincipal client
  ){
    clientService.deleteByClientId(client.getId());

    return ResponseEntity.noContent().build();
  }

  @GetMapping("/{clientId}")
  @PreAuthorize("hasRole('LAWYER')")
  ResponseEntity<ClientSearchDto> getClientById(
      @PathVariable Long clientId,
      @AuthenticationPrincipal LawyerPrincipal lp
  ){
    Long lawyerId = lp.getId();

    boolean exists = appointmentRepo.existsByLawyerIdAndClientId(lawyerId, clientId);
    if(!exists) {
      throw new ResponseStatusException(HttpStatus.FORBIDDEN, "해당 의뢰인과의 상담 기록이 없으므로 조회할 수 없습니다.");
    }

    Client client = clientRepo.findById(clientId)
        .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "의뢰인을 찾을 수 없습니다."));

    return ResponseEntity.ok(ClientSearchDto.from(client));
  }

}
