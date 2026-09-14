import java.util.*;

public class GroupAnagrams {

    public static Map<String, List<String>> groupAnagrams(List<String> words) {
        Map<String, List<String>> groups = new HashMap<>();
        for (String word : words) {
            char[] chars = word.toCharArray();
            Arrays.sort(chars);
            String key = new String(chars);
            if (!groups.containsKey(key)) {
                groups.put(key, new ArrayList<>());
            }
            groups.get(key).add(word);
        }

        return groups;
    }

    public static void main(String[] args) {
        List<String> words = Arrays.asList("listen", "silent", "enlist", "google", "gogole", "cat", "act");
        Map<String, List<String>> groups = groupAnagrams(words);
        for (List<String> group : groups.values()) {
            System.out.println(group);
        }
    }
}