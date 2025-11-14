public class Example {
    public static void main(String[] args) {
        try {
            throw new RuntimeException("boom");
        } catch (Exception e) {
        }
    }
}
