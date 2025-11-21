package com.example.antipatterns;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.io.*;
import java.math.BigDecimal;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.Statement;
import java.text.SimpleDateFormat;
import java.util.*;
import javax.persistence.EntityManager;

/**
 * Comprehensive test file for all 26 Semgrep rules
 * Tests both TRUE POSITIVES (should trigger) and FALSE POSITIVES (should NOT trigger)
 */
@Service
public class ComprehensiveAntiPatternTest {
    
    private static final Logger logger = LoggerFactory.getLogger(ComprehensiveAntiPatternTest.class);
    private static final int MAX_RETRIES = 5; // Should NOT trigger magic number (constant)
    private static final String API_URL = "https://api.example.com"; // Should NOT trigger hardcoded URL (constant)
    
    private UserRepository userRepository;
    private OrderRepository orderRepository;
    
    // ============================================
    // RULE 1: Empty catch blocks
    // ============================================
    
    // SHOULD TRIGGER #1
    public void emptyCatch1() {
        try {
            riskyOperation();
        } catch (Exception e) {
        }
    }
    
    // SHOULD TRIGGER #2
    public void emptyCatch2() {
        try {
            riskyOperation();
        } catch (IOException e) {
        }
    }
    
    // SHOULD NOT TRIGGER: has code
    public void goodCatch() {
        try {
            riskyOperation();
        } catch (Exception e) {
            logger.error("Operation failed", e);
        }
    }
    
    // ============================================
    // RULE 2: printStackTrace()
    // ============================================
    
    // SHOULD TRIGGER #3
    public void usesPrintStackTrace() {
        try {
            riskyOperation();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    
    // SHOULD NOT TRIGGER: uses logger
    public void usesLogger() {
        try {
            riskyOperation();
        } catch (Exception e) {
            logger.error("Error occurred", e);
        }
    }
    
    // ============================================
    // RULE 3: System.out/err
    // ============================================
    
    // SHOULD TRIGGER #4
    public void usesSystemOut() {
        System.out.println("Debug message");
    }
    
    // SHOULD TRIGGER #5
    public void usesSystemErr() {
        System.err.println("Error message");
    }
    
    // SHOULD NOT TRIGGER: uses logger
    public void usesLoggerCorrectly() {
        logger.info("Info message");
        logger.debug("Debug message");
    }
    
    // ============================================
    // RULE 4: Logging sensitive data
    // ============================================
    
    // SHOULD TRIGGER #6
    public void logsSensitiveData(String username, String password) {
        logger.info("User {} logged in with password {}", username, password);
    }
    
    // SHOULD TRIGGER #7
    public void logsToken(String apiToken) {
        logger.debug("API token: {}", apiToken);
    }
    
    // SHOULD TRIGGER #8
    public void logsCardNumber(String cardNumber) {
        logger.error("Payment failed for card: " + cardNumber);
    }
    
    // SHOULD NOT TRIGGER: just words in message
    public void logsPasswordResetMessage() {
        logger.info("Password reset email sent successfully");
        logger.debug("Token validation completed");
    }
    
    // SHOULD NOT TRIGGER: masked data
    public void logsMaskedData(String password) {
        String masked = maskPassword(password);
        logger.info("Password updated: {}", masked);
    }
    
    // ============================================
    // RULE 5: Hardcoded credentials
    // ============================================
    
    // SHOULD TRIGGER #9
    public void hardcodedApiKey() {
        String apiKey = "sk_live_1234567890abcdef";
    }
    
    // SHOULD TRIGGER #10
    public void hardcodedPassword() {
        String password = "MySecretPass123";
    }
    
    // SHOULD TRIGGER #11
    public void hardcodedToken() {
        String token = "bearer_abc123456789";
    }
    
    // SHOULD NOT TRIGGER: placeholder
    public void placeholderPassword() {
        String examplePassword = "your_password_here";
        String testPassword = "test_password_123";
    }
    
    // SHOULD NOT TRIGGER: from config
    @Value("${api.key}")
    private String configApiKey;
    
    // ============================================
    // RULE 6: Hardcoded URLs
    // ============================================
    
    // SHOULD TRIGGER #12
    public void hardcodedApiUrl() {
        String apiUrl = "https://api.production.com/v1";
    }
    
    // SHOULD TRIGGER #13
    public void hardcodedServiceEndpoint() {
        String serviceEndpoint = "https://payment.gateway.com";
    }
    
    // SHOULD NOT TRIGGER: documentation URL
    public void documentationUrl() {
        String docs = "https://docs.oracle.com/javase";
        String example = "https://example.com/api";
    }
    
    // SHOULD NOT TRIGGER: from config
    @Value("${service.url}")
    private String serviceUrl;
    
    // ============================================
    // RULE 7: SQL injection
    // ============================================
    
    // SHOULD TRIGGER #14
    public void sqlInjection1(Connection conn, String userId) throws Exception {
        Statement stmt = conn.createStatement();
        stmt.executeQuery("SELECT * FROM users WHERE id = " + userId);
    }
    
    // SHOULD TRIGGER #15
    public void sqlInjection2(Connection conn, String name) throws Exception {
        Statement stmt = conn.createStatement();
        stmt.execute("UPDATE users SET status = '" + name + "'");
    }
    
    // SHOULD NOT TRIGGER: just string with SQL words
    public void messageWithSqlWords() {
        String message = "Please select your option from the menu";
        logger.info("Updated user preferences");
    }
    
    // SHOULD NOT TRIGGER: PreparedStatement
    public void goodSql(Connection conn, String userId) throws Exception {
        PreparedStatement pstmt = conn.prepareStatement("SELECT * FROM users WHERE id = ?");
        pstmt.setString(1, userId);
        pstmt.executeQuery();
    }
    
    // ============================================
    // RULE 8: Thread.sleep
    // ============================================
    
    // SHOULD TRIGGER #16
    public void usesThreadSleep() throws InterruptedException {
        Thread.sleep(1000);
    }
    
    // SHOULD NOT TRIGGER: uses ScheduledExecutor
    public void usesScheduledExecutor() {
        // ScheduledExecutorService executor = Executors.newScheduledThreadPool(1);
        // executor.schedule(() -> doWork(), 1, TimeUnit.SECONDS);
    }
    
    // ============================================
    // RULE 9: String concatenation in loop
    // ============================================
    
    // SHOULD TRIGGER #17
    public String stringConcatInLoop(List<String> items) {
        String result = "";
        for (String item : items) {
            result += item + ", ";
        }
        return result;
    }
    
    // SHOULD NOT TRIGGER: StringBuilder
    public String goodStringConcat(List<String> items) {
        StringBuilder sb = new StringBuilder();
        for (String item : items) {
            sb.append(item).append(", ");
        }
        return sb.toString();
    }
    
    // ============================================
    // RULE 10: Expensive objects in loop
    // ============================================
    
    // SHOULD TRIGGER #18, #19, #20
    public void expensiveObjectsInLoop(List<String> dates) {
        for (String date : dates) {
            SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd");
            Pattern.compile("[a-z]+");
            com.fasterxml.jackson.databind.ObjectMapper mapper = new com.fasterxml.jackson.databind.ObjectMapper();
        }
    }
    
    // SHOULD NOT TRIGGER: created outside loop
    public void goodObjectCreation(List<String> dates) {
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd");
        for (String date : dates) {
            // use sdf
        }
    }
    
    // SHOULD NOT TRIGGER: StringBuilder is allowed in loops
    public void allowedObjectInLoop(List<String> items) {
        for (String item : items) {
            StringBuilder sb = new StringBuilder();
            sb.append(item);
        }
    }
    
    // ============================================
    // RULE 11: N+1 queries
    // ============================================
    
    // SHOULD TRIGGER #21
    public void nPlusOne1(List<User> users) {
        for (User user : users) {
            List<Order> orders = orderRepository.findByUserId(user.getId());
        }
    }
    
    // SHOULD TRIGGER #22
    public void nPlusOne2(List<Order> orders) {
        for (Order order : orders) {
            User user = order.getUser();
        }
    }
    
    // SHOULD TRIGGER #23
    public void nPlusOne3(List<User> users) {
        for (User user : users) {
            user.getOrders();
        }
    }
    
    // SHOULD NOT TRIGGER: fetched with JOIN
    public void goodFetch() {
        List<User> users = userRepository.findAllWithOrders();
        for (User user : users) {
            logger.info("User: {}", user.getName());
        }
    }
    
    // SHOULD NOT TRIGGER: no database call
    public void simpleLoop(List<String> items) {
        for (String item : items) {
            logger.info(item);
        }
    }
    
    // ============================================
    // RULE 12: String == comparison
    // ============================================
    
    // SHOULD TRIGGER #24
    public void stringEqualsOperator(String input) {
        if (input == "test") {
            logger.info("Match");
        }
    }
    
    // SHOULD TRIGGER #25
    public void stringNotEqualsOperator(String input) {
        if (input != "admin") {
            logger.info("Not admin");
        }
    }
    
    // SHOULD NOT TRIGGER: uses .equals()
    public void goodStringComparison(String input) {
        if ("test".equals(input)) {
            logger.info("Match");
        }
    }
    
    // ============================================
    // RULE 13: DTO public fields
    // ============================================
    
    // SHOULD TRIGGER #26, #27, #28
    public class UserDTO {
        public String username;
        public String email;
        public int age;
        
        // Should NOT trigger: constant
        public static final String TYPE = "USER";
    }
    
    // SHOULD TRIGGER #29, #30
    public class UserRequest {
        public String name;
        public String password;
    }
    
    // SHOULD NOT TRIGGER: private fields
    public class GoodUserDTO {
        private String username;
        private String email;
        
        public String getUsername() { return username; }
    }
    
    // SHOULD NOT TRIGGER: not a DTO
    public class RegularClass {
        public String name;
        public int count;
    }
    
    // ============================================
    // RULE 14: Magic numbers
    // ============================================
    
    // SHOULD TRIGGER #31, #32, #33
    public void magicNumbers() {
        int timeout = 30000;
        int maxRetries = 15;
        processData(100);
    }
    
    // SHOULD NOT TRIGGER: HTTP status codes
    public void httpStatusCodes() {
        int ok = 200;
        int notFound = 404;
        int serverError = 500;
    }
    
    // SHOULD NOT TRIGGER: common ports
    public void commonPorts() {
        int port = 8080;
        int securePort = 8443;
    }
    
    // SHOULD NOT TRIGGER: constants
    public void usesConstants() {
        processData(MAX_RETRIES);
    }
    
    // SHOULD NOT TRIGGER: small numbers
    public void smallNumbers() {
        int count = 5;
        int retry = 3;
        for (int i = 0; i < 10; i++) {
            // loop
        }
    }
    
    // ============================================
    // RULE 15: Field injection
    // ============================================
    
    // SHOULD TRIGGER #34
    @Autowired
    private OrderRepository badFieldInjection;
    
    // SHOULD NOT TRIGGER: @Value is allowed
    @Value("${app.name}")
    private String appName;
    
    // SHOULD NOT TRIGGER: constructor injection (good pattern)
    private final UserRepository goodInjection;
    
    @Autowired
    public ComprehensiveAntiPatternTest(UserRepository userRepository) {
        this.goodInjection = userRepository;
    }
    
    // ============================================
    // RULE 16: Catch generic Exception
    // ============================================
    
    // SHOULD TRIGGER #35
    public void catchesGenericException() {
        try {
            riskyOperation();
        } catch (Exception e) {
            logger.error("Error", e);
        }
    }
    
    // SHOULD NOT TRIGGER: specific exception
    public void catchesSpecificException() {
        try {
            riskyOperation();
        } catch (IOException e) {
            logger.error("IO Error", e);
        }
    }
    
    // SHOULD NOT TRIGGER: main method
    public static void main(String[] args) {
        try {
            // startup
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    
    // ============================================
    // RULE 17: Resource leaks
    // ============================================
    
    // SHOULD TRIGGER #36, #37
    public void resourceLeak() throws IOException {
        FileInputStream fis = new FileInputStream("file.txt");
        BufferedReader br = new BufferedReader(new FileReader("data.txt"));
    }
    
    // SHOULD NOT TRIGGER: try-with-resources
    public void goodResourceHandling() throws IOException {
        try (FileInputStream fis = new FileInputStream("file.txt")) {
            // auto-closed
        }
    }
    
    // ============================================
    // RULE 18: Null check after dereferencing
    // ============================================
    
    // SHOULD TRIGGER #38
    public void nullCheckAfterUse(User user) {
        user.getName();
        user.getEmail();
        
        if (user == null) {
            return;
        }
    }
    
    // SHOULD NOT TRIGGER: check before use
    public void goodNullCheck(User user) {
        if (user == null) {
            return;
        }
        user.getName();
    }
    
    // ============================================
    // RULE 19: Inefficient isEmpty() check
    // ============================================
    
    // SHOULD TRIGGER #39, #40, #41
    public void inefficientEmptyCheck(List<String> items, String text) {
        if (items.size() == 0) {
            return;
        }
        if (items.size() > 0) {
            process(items);
        }
        if (text.length() == 0) {
            return;
        }
    }
    
    // SHOULD NOT TRIGGER: uses isEmpty()
    public void goodEmptyCheck(List<String> items, String text) {
        if (items.isEmpty()) {
            return;
        }
        if (!text.isEmpty()) {
            process(text);
        }
    }
    
    // ============================================
    // RULE 20: Double-checked locking without volatile
    // ============================================
    
    // SHOULD TRIGGER #42
    public static class BadSingleton {
        private static BadSingleton instance;
        
        public static BadSingleton getInstance() {
            if (instance == null) {
                synchronized (BadSingleton.class) {
                    if (instance == null) {
                        instance = new BadSingleton();
                    }
                }
            }
            return instance;
        }
    }
    
    // SHOULD NOT TRIGGER: has volatile
    public static class GoodSingleton {
        private static volatile GoodSingleton instance;
        
        public static GoodSingleton getInstance() {
            if (instance == null) {
                synchronized (GoodSingleton.class) {
                    if (instance == null) {
                        instance = new GoodSingleton();
                    }
                }
            }
            return instance;
        }
    }
    
    // ============================================
    // RULE 21: Boolean == comparison
    // ============================================
    
    // SHOULD TRIGGER #43, #44
    public void booleanEqualsOperator(Boolean flag) {
        if (flag == Boolean.TRUE) {
            process();
        }
        if (Boolean.FALSE == flag) {
            stop();
        }
    }
    
    // SHOULD NOT TRIGGER: uses .equals()
    public void goodBooleanComparison(Boolean flag) {
        if (Boolean.TRUE.equals(flag)) {
            process();
        }
    }
    
    // ============================================
    // RULE 22: Arrays.asList on primitives
    // ============================================
    
    // SHOULD TRIGGER #45
    public void arraysAsListPrimitive() {
        int[] numbers = {1, 2, 3, 4, 5};
        List<int[]> list = Arrays.asList(numbers);
    }
    
    // SHOULD NOT TRIGGER: object array
    public void arraysAsListObject() {
        String[] names = {"Alice", "Bob", "Charlie"};
        List<String> list = Arrays.asList(names);
    }
    
    // SHOULD NOT TRIGGER: proper conversion
    public void goodPrimitiveToList() {
        int[] numbers = {1, 2, 3, 4, 5};
        List<Integer> list = Arrays.stream(numbers)
            .boxed()
            .collect(Collectors.toList());
    }
    
    // ============================================
    // RULE 23: Modify collection while iterating
    // ============================================
    
    // SHOULD TRIGGER #46, #47, #48
    public void modifyWhileIterating(List<String> items) {
        for (String item : items) {
            items.remove(item);
        }
        
        for (String item : items) {
            if (item.isEmpty()) {
                items.remove(item);
            }
        }
        
        for (String item : items) {
            items.add(item + "_copy");
        }
    }
    
    // SHOULD NOT TRIGGER: Iterator.remove()
    public void goodModification(List<String> items) {
        Iterator<String> it = items.iterator();
        while (it.hasNext()) {
            String item = it.next();
            if (item.isEmpty()) {
                it.remove();
            }
        }
    }
    
    // SHOULD NOT TRIGGER: different collection
    public void modifyDifferentCollection(List<String> items, List<String> toRemove) {
        for (String item : items) {
            toRemove.remove(item);
        }
    }
    
    // ============================================
    // RULE 24: BigDecimal from double
    // ============================================
    
    // SHOULD TRIGGER #49, #50
    public void bigDecimalFromDouble() {
        BigDecimal price = new BigDecimal(19.99);
        BigDecimal tax = new BigDecimal(0.08);
    }
    
    // SHOULD NOT TRIGGER: valueOf or String
    public void goodBigDecimal() {
        BigDecimal price = BigDecimal.valueOf(19.99);
        BigDecimal tax = new BigDecimal("0.08");
    }
    
    // SHOULD NOT TRIGGER: from integer
    public void bigDecimalFromInt() {
        BigDecimal count = new BigDecimal(100);
    }
    
    // ============================================
    // Helper methods and classes
    // ============================================
    
    private void riskyOperation() throws IOException {
    }
    
    private void process(Object obj) {
    }
    
    private void process() {
    }
    
    private void stop() {
    }
    
    private void processData(int count) {
    }
    
    private String maskPassword(String password) {
        return "***";
    }
    
    interface UserRepository {
        List<User> findAllWithOrders();
    }
    
    interface OrderRepository {
        List<Order> findByUserId(Long userId);
    }
    
    static class User {
        private Long id;
        private String name;
        private String email;
        private List<Order> orders;
        
        public Long getId() { return id; }
        public String getName() { return name; }
        public String getEmail() { return email; }
        public List<Order> getOrders() { return orders; }
    }
    
    static class Order {
        private Long id;
        private User user;
        
        public Long getId() { return id; }
        public User getUser() { return user; }
    }
    
    static class Pattern {
        static Pattern compile(String regex) {
            return new Pattern();
        }
    }
}