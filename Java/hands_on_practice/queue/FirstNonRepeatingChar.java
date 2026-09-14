import java.util.*;

public class FirstNonRepeatingChar {

    public static List<Character> firstNonRepeating(String stream) {
        List<Character> result = new ArrayList<>();
        Map<Character, Integer> count = new HashMap<>();
        Queue<Character> queue = new LinkedList<>();

        for (char c : stream.toCharArray()) {
            queue.add(c);
            count.merge(c, 1, Integer::sum);

            while (!queue.isEmpty() && count.get(queue.peek()) > 1) {
                queue.poll();
            }

            result.add(queue.isEmpty() ? '#' : queue.peek());
        }
        return result;
    }

    public static void main(String[] args) {
        String stream = "aabcbc";
        List<Character> result = firstNonRepeating(stream);

        StringBuilder sb = new StringBuilder();
        for (char c : result) {
            sb.append(c).append(' ');
        }
        System.out.println(sb.toString().trim());
    }
}