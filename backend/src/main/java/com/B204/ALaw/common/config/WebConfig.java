package com.B204.ALaw.common.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class WebConfig implements WebMvcConfigurer {

  // Method
  /**
   * AI 파트에 요청보낼 때 필요해서 빈주입 메서드 추가
   * @return RestTemplate 객체
   */
  @Bean
  public RestTemplate restTemplate() {
    return new RestTemplate();
  }

  @Override
  public void addCorsMappings(CorsRegistry registry) {
    registry.addMapping("/**")
        .allowedOrigins("http://localhost:5173")
        .allowedMethods("GET","POST", "PATCH" ,"PUT","DELETE","OPTIONS")
        .allowedHeaders("*")
        .allowCredentials(true);
  }

}
