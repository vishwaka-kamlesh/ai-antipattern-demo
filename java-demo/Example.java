public class Example {
    public static void main(String[] args) {
String str1 = "hello";
        String str2 = "hello";

        // Triggers no-eq-string
        if (str1 == str2) {
            System.out.println("Strings are equal"); // Triggers no-system-out
        }

        try {
            int x = 1 / 0;
        } catch (ArithmeticException e) {
            e.printStackTrace(); // Triggers no-print-stacktrace
        }

        try {
            int y = Integer.parseInt("abc");
        } catch (NumberFormatException ex) {
            // Triggers java.empty-catch-block
        }
    }
    }
}
