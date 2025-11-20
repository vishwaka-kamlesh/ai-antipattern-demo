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
 * Test file for Semgrep rules - Contains intentional anti-patterns
 * Each section corresponds to a rule number
 */
@Service
public class AntiPatternExamples {
    
    private static final Logger logger = LoggerFactory.getLogger(AntiPatternExamples.class);
    
    private UserRepository userRepository;
    
    // ============================================
    // RULE 1: Empty catch blocks
    // ============================================
    public void emptyCatchBlock() {
        try {
            riskyOperation();
        } catch (Exception e) {
            // SHOULD TRIGGER: Empty catch block
        }
    }
    
    public void goodCatchBlock() {
        try {
            riskyOperation();
        } catch (Exception e) {
            logger.error("Operation failed", e);
        }
    }
    
    // ============================================
    // RULE 2: printStackTrace()
    // ============================================
    public void printStackTraceUsage() {
        try {
            riskyOperation();
        } catch (Exception e) {
            e.printStackTrace(); // SHOULD TRIGGER
        }
    }
    
    // ============================================
    // RULE 3: System.out/err
    // ============================================
    public void systemOutUsage() {
        System.out.println("Debug message"); // SHOULD TRIGGER
        System.err.println("Error message"); // SHOULD TRIGGER
    }
    
    // ============================================
    // RULE 4: Logging sensitive data
    // ============================================
    public void loggingSensitiveData(String username, String password, String token) {
        // SHOULD TRIGGER: actual variable interpolation
        logger.info("User login: {} with password: {}", username, password);
        logger.debug("API Token: {}", token);
        logger.error("Authentication failed for: " + password);
        
        // SHOULD NOT TRIGGER: just words in string
        logger.info("Password reset successful");
        logger.debug("Token validation completed");
    }
    
    // ============================================
    // RULE 5: Hardcoded credentials
    // ============================================
    public void hardcodedCredentials() {
        // SHOULD TRIGGER
        String apiKey = "ak_live_1234567890abcdef";
        String password = "MySecretPass123";
        String token = "bearer_token_12345678";
        
        // SHOULD NOT TRIGGER: test placeholders
        String examplePassword = "your_password_here";
        String testToken = "test_token_placeholder";
    }
    
    // ============================================
    // RULE 6: Hardcoded URLs
    // ============================================
    public void hardcodedUrls() {
        // SHOULD TRIGGER
        String apiUrl = "https://api.production.com/v1";
        String serviceEndpoint = "https://payment.gateway.com";
        
        // SHOULD NOT TRIGGER: documentation
        String docs = "https://docs.oracle.com/javase";
        String example = "https://example.com/api";
    }
    
    // ============================================
    // RULE 7: SQL injection via concatenation
    // ============================================
    public void sqlInjection(Connection conn, String userId) throws Exception {
        Statement stmt = conn.createStatement();
        
        // SHOULD TRIGGER
        String query = "SELECT * FROM users WHERE id = " + userId;
        stmt.executeQuery(query);
        stmt.execute("UPDATE users SET status = '" + userId + "'");
        
        // SHOULD NOT TRIGGER: just string with SQL words
        String message = "Select your option from the menu";
    }
    
    public void sqlInjectionJdbcTemplate(org.springframework.jdbc.core.JdbcTemplate jdbc, String name) {
        // SHOULD TRIGGER
        String sql = "SELECT * FROM users WHERE name = '" + name + "'";
        jdbc.query(sql, (rs, rowNum) -> rs.getString("name"));
    }
    
    public void sqlInjectionJPA(EntityManager em, String status) {
        // SHOULD TRIGGER
        em.createNativeQuery("SELECT * FROM orders WHERE status = " + status).getResultList();
    }
    
    public void goodSql(Connection conn, String userId) throws Exception {
        // GOOD: Using PreparedStatement
        PreparedStatement pstmt = conn.prepareStatement("SELECT * FROM users WHERE id = ?");
        pstmt.setString(1, userId);
        pstmt.executeQuery();
    }
    
    // ============================================
    // RULE 8: Thread.sleep
    // ============================================
    public void threadSleep() throws InterruptedException {
        Thread.sleep(1000); // SHOULD TRIGGER
        
        // Better: use ScheduledExecutorService or @Scheduled
    }
    
    // ============================================
    // RULE 9: String concatenation in loop
    // ============================================
    public String stringConcatInLoop(List<String> items) {
        String result = "";
        
        // SHOULD TRIGGER
        for (String item : items) {
            result += item + ", ";
        }
        
        return result;
    }
    
    public String goodStringConcat(List<String> items) {
        // GOOD: Using StringBuilder
        StringBuilder sb = new StringBuilder();
        for (String item : items) {
            sb.append(item).append(", ");
        }
        return sb.toString();
    }
    
    // ============================================
    // RULE 10: Expensive object creation in loop
    // ============================================
    public void expensiveObjectsInLoop(List<String> dates) {
        for (String date : dates) {
            // SHOULD TRIGGER
            SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd");
            Pattern.compile("[a-z]+");
            ObjectMapper mapper = new ObjectMapper();
        }
    }
    
    public void goodObjectCreation(List<String> dates) {
        // GOOD: Create once outside loop
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd");
        for (String date : dates) {
            sdf.parse(date);
        }
    }
    
    // ============================================
    // RULE 11: N+1 query detection
    // ============================================
    public void nPlusOneQuery(List<User> users) {
        // SHOULD TRIGGER: repository call in loop
        for (User user : users) {
            List<Order> orders = orderRepository.findByUserId(user.getId());
        }
        
        // SHOULD TRIGGER: lazy loading in loop
        for (User user : users) {
            user.getOrders().size(); // lazy fetch
        }
    }
    
    public void goodQueryFetch() {
        // GOOD: Use JOIN FETCH or @EntityGraph
        List<User> users = userRepository.findAllWithOrders();
    }
    
    // ============================================
    // RULE 12: String comparison with ==
    // ============================================
    public void stringEqualsOperator(String input) {
        // SHOULD TRIGGER
        if (input == "test") {
            System.out.println("Match");
        }
        
        if ("admin" == input) {
            System.out.println("Admin");
        }
        
        String another = "value";
        if (input == another) {
            System.out.println("Same");
        }
    }
    
    public void goodStringComparison(String input) {
        // GOOD: Use .equals()
        if ("test".equals(input)) {
            System.out.println("Match");
        }
    }
    
    // ============================================
    // RULE 13: DTO with public fields
    // ============================================
    public class UserDTO {
        // SHOULD TRIGGER
        public String username;
        public String email;
        public int age;
        
        // SHOULD NOT TRIGGER: constants are fine
        public static final String TYPE = "USER";
    }
    
    public class UserRequest {
        // SHOULD TRIGGER
        public String name;
        public String password;
    }
    
    public class GoodUserDTO {
        // GOOD: private fields with getters/setters
        private String username;
        private String email;
        
        public String getUsername() { return username; }
        public void setUsername(String username) { this.username = username; }
    }
    
    // ============================================
    // RULE 14: Magic numbers
    // ============================================
    public void magicNumbers() {
        // SHOULD TRIGGER
        int timeout = 30000;
        int maxRetries = 15;
        double threshold = 0.75;
        processData(100);
        
        // SHOULD NOT TRIGGER: HTTP status codes
        int status = 200;
        int notFound = 404;
        
        // SHOULD NOT TRIGGER: common ports
        int port = 8080;
    }
    
    public void goodConstants() {
        // GOOD: Named constants
        final int TIMEOUT_MS = 30000;
        final int MAX_RETRIES = 15;
        processData(MAX_RETRIES);
    }
    
    // ============================================
    // RULE 15: Field injection with @Autowired
    // ============================================
    
    // SHOULD TRIGGER
    @Autowired
    private UserRepository badRepository;
    
    // SHOULD NOT TRIGGER: @Value is allowed
    @Value("${app.name}")
    private String appName;
    
    // GOOD: Constructor injection
    private final UserRepository goodRepository;
    
    @Autowired
    public AntiPatternExamples(UserRepository userRepository) {
        this.goodRepository = userRepository;
    }
    
    // ============================================
    // RULE 16: Catching generic Exception
    // ============================================
    public void catchGenericException() {
        try {
            riskyOperation();
        } catch (Exception e) { // SHOULD TRIGGER
            logger.error("Error", e);
        }
    }
    
    public void goodExceptionHandling() {
        try {
            riskyOperation();
        } catch (IOException e) { // GOOD: Specific exception
            logger.error("IO Error", e);
        } catch (SQLException e) {
            logger.error("DB Error", e);
        }
    }
    
    // ============================================
    // RULE 17: Resource leak
    // ============================================
    public void resourceLeak() throws IOException {
        // SHOULD TRIGGER
        FileInputStream fis = new FileInputStream("file.txt");
        BufferedReader br = new BufferedReader(new FileReader("data.txt"));
    }
    
    public void goodResourceHandling() throws IOException {
        // GOOD: try-with-resources
        try (FileInputStream fis = new FileInputStream("file.txt")) {
            // Auto-closed
        }
    }
    
    // ============================================
    // RULE 18: Null check after dereferencing
    // ============================================
    public void nullCheckAfterDereference(User user) {
        // SHOULD TRIGGER
        user.getName();
        user.getEmail();
        
        if (user == null) {
            return;
        }
    }
    
    public void goodNullCheck(User user) {
        // GOOD: Check before use
        if (user == null) {
            return;
        }
        user.getName();
    }
    
    // ============================================
    // RULE 19: Inefficient isEmpty() check
    // ============================================
    public void inefficientEmptyCheck(List<String> items, String text) {
        // SHOULD TRIGGER
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
    
    public void goodEmptyCheck(List<String> items, String text) {
        // GOOD: Use isEmpty()
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
    public class Singleton {
        // SHOULD TRIGGER: missing volatile
        private static Singleton instance;
        
        public static Singleton getInstance() {
            if (instance == null) {
                synchronized (Singleton.class) {
                    if (instance == null) {
                        instance = new Singleton();
                    }
                }
            }
            return instance;
        }
    }
    
    public class GoodSingleton {
        // GOOD: volatile keyword present
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
    // RULE 21: Boolean comparison with ==
    // ============================================
    public void booleanComparison(Boolean flag) {
        // SHOULD TRIGGER
        if (flag == Boolean.TRUE) {
            process();
        }
        
        if (Boolean.FALSE == flag) {
            stop();
        }
    }
    
    public void goodBooleanComparison(Boolean flag) {
        // GOOD: Use .equals()
        if (Boolean.TRUE.equals(flag)) {
            process();
        }
    }
    
    // ============================================
    // RULE 22: Arrays.asList on primitive arrays
    // ============================================
    public void arraysAsListPrimitive() {
        int[] numbers = {1, 2, 3, 4, 5};
        
        // SHOULD TRIGGER: doesn't work as expected
        List<int[]> list = Arrays.asList(numbers);
    }
    
    public void goodPrimitiveToList() {
        int[] numbers = {1, 2, 3, 4, 5};
        
        // GOOD: Use streams
        List<Integer> list = Arrays.stream(numbers)
            .boxed()
            .collect(Collectors.toList());
    }
    
    // ============================================
    // RULE 23: Modifying collection while iterating
    // ============================================
    public void modifyWhileIterating(List<String> items) {
        // SHOULD TRIGGER
        for (String item : items) {
            if (item.isEmpty()) {
                items.remove(item);
            }
        }
        
        // SHOULD TRIGGER
        for (String item : items) {
            if (item.length() > 10) {
                items.add(item + "_copy");
            }
        }
    }
    
    public void goodModification(List<String> items) {
        // GOOD: Use Iterator.remove()
        Iterator<String> it = items.iterator();
        while (it.hasNext()) {
            String item = it.next();
            if (item.isEmpty()) {
                it.remove();
            }
        }
        
        // GOOD: Collect to new list
        List<String> filtered = items.stream()
            .filter(item -> !item.isEmpty())
            .collect(Collectors.toList());
    }
    
    // ============================================
    // RULE 24: BigDecimal from double
    // ============================================
    public void bigDecimalFromDouble() {
        // SHOULD TRIGGER: precision loss
        BigDecimal price = new BigDecimal(19.99);
        BigDecimal tax = new BigDecimal(0.08);
    }
    
    public void goodBigDecimal() {
        // GOOD: Use valueOf or String constructor
        BigDecimal price = BigDecimal.valueOf(19.99);
        BigDecimal tax = new BigDecimal("0.08");
    }
    
    // ============================================
    // RULE 25: Missing @Transactional
    // ============================================
    
    // SHOULD TRIGGER: database operations without @Transactional
    public void saveUser(User user) {
        userRepository.save(user);
        orderRepository.deleteByUserId(user.getId());
    }
    
    // GOOD: @Transactional present
    @Transactional
    public void saveUserTransactional(User user) {
        userRepository.save(user);
        orderRepository.deleteByUserId(user.getId());
    }
    
    // ============================================
    // Helper methods and classes
    // ============================================
    
    private void riskyOperation() throws IOException, SQLException {
        // Simulated risky operation
    }
    
    private void process(Object obj) {
        // Process logic
    }
    
    private void process() {
        // Process logic
    }
    
    private void stop() {
        // Stop logic
    }
    
    // Mock classes
    private OrderRepository orderRepository;
    
    interface UserRepository {
        void save(User user);
        List<User> findAllWithOrders();
    }
    
    interface OrderRepository {
        List<Order> findByUserId(Long userId);
        void deleteByUserId(Long userId);
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
        private String status;
    }
    
    static class ObjectMapper {
        // Mock Jackson ObjectMapper
    }
    
    static class Pattern {
        static Pattern compile(String regex) {
            return new Pattern();
        }
    }
}