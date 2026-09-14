import java.util.*;

public class CommonElements {

    public static Set<Integer> commonElements(List<Set<Integer>> sets) {
        if (sets.isEmpty()) {
            return new HashSet<>();
        }
        Set<Integer> result = new HashSet<>(sets.get(0));
        for (int i = 1; i < sets.size(); i++) {
            result.retainAll(sets.get(i));
        }
        return result;
    }

    public static void main(String[] args) {
        Set<Integer> s1 = new HashSet<>(Arrays.asList(1, 2, 3, 4, 5));
        Set<Integer> s2 = new HashSet<>(Arrays.asList(2, 3, 5, 7));
        Set<Integer> s3 = new HashSet<>(Arrays.asList(2, 3, 5, 9, 11));
        List<Set<Integer>> sets = Arrays.asList(s1, s2, s3);

        List<Integer> sorted = new ArrayList<>(commonElements(sets));
        Collections.sort(sorted);
        System.out.println(sorted);
    }
}