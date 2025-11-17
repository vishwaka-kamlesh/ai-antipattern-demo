package com.example.antipatterns;

import com.example.dto.PaymentRequestDTO;
import com.example.repository.UserRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.*;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.List;

@RestController
@RequestMapping("/test")
public class AntiPatternDemo {

    private static final Logger logger = LoggerFactory.getLogger(AntiPatternDemo.class);

    // 16. Field injection (banned)
    @Autowired
    private UserRepository userRepository;

    // 5. Hardcoded credentials
    private String dbPassword = "SuperSecret123!@#";

    // 6. Hardcoded URL (not localhost)
    private String apiUrl = "https://api.payment-gateway.com/v1/charge";

    @Value("${app.debug:false}")
    private boolean debug;

    @GetMapping("/demo")
    public String demo() {
        try {
            // 8. Thread.sleep
            Thread.sleep(5000);

            // 2. printStackTrace
            throw new RuntimeException("Test");
        } catch (Exception e) {
            e.printStackTrace(); // VIOLATION #2

            // 1. Empty catch block
            try {
                Class.forName("com.mysql.Driver");
            } catch (ClassNotFoundException ex) {
                // VIOLATION #1 — completely empty
            }

            // 6. Broad catch without handling (another one)
            try {
                Connection conn = DriverManager.getConnection(
                    "jdbc:mysql://prod-db:3306/app", "root", dbPassword);
            } catch (Exception ex) { // VIOLATION #6 (broad catch, no log/rethrow)
                System.out.println("DB connection failed"); // VIOLATION #3
            }
        }

        // 3. System.out
        System.out.println("Processing payment...");

        // 4. Logging sensitive data
        logger.info("User token: A1B2C3D4E5F6G7H8I9J0 user phone: 9876543210");

        // 7. SQL string concatenation
        String userId = "123'; DROP TABLE users; --";
        String query = "SELECT * FROM users WHERE id = '" + userId + "'";

        // 12. String == comparison
        if ("ACTIVE" == "active".toUpperCase()) {
            logger.info("User is active");
        }

        // 9. String concatenation in loop
        String result = "";
        for (int i = 0; i < 1000; i++) {
            result += "X"; // VIOLATION #9
        }

        // 10. Object creation in loop
        List<StringBuilder> builders = new ArrayList<>();
        for (int i = 0; i < 10000; i++) {
            builders.add(new StringBuilder("data" + i)); // VIOLATION #10
        }

        // 11. N+1 query
        List<Long> ids = List.of(1L, 2L, 3L, 4L, 5L);
        for (Long id : ids) {
            userRepository.findById(id).get(); // VIOLATION #11
        }

        // 15. Magic number
        if (result.length() > 9999) { // VIOLATION #15
            return "Too long";
        }

        return query;
    }
}

// 13. DTO with public fields
class BadPaymentRequestDTO {
    public String cardNumber;    // VIOLATION #13
    public String cvv;
    public String email;
    public int amount = 25000;   // Magic number, but caught by class name
}

// 14. Unused import (Semgrep will detect automatically)
import java.util.HashMap;