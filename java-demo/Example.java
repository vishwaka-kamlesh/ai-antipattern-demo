public class Example {
    public static void main(String[] args) {
        String a = "hello";
        String b = new String("hello");
        if (a == b) {
            System.out.println("Equal!");
        }

        if ("a" == "a") {
            System.out.println("Equal!");
        }
    }
}
