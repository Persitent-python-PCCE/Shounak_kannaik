import java.util.*;

public class SymmetricDifference {

    public static <String> Set<String> symmetricDifference(Set<String> setA, Set<String> setB) {
        Set<String> union = new HashSet<>(setA);
        union.addAll(setB);

        Set<String> intersection = new HashSet<>(setA);
        intersection.retainAll(setB);

        union.removeAll(intersection);

        return union;
    }

    public static void main(String[] args) {
        Set<String> setA = new LinkedHashSet<>(Arrays.asList("apple", "banana", "cherry", "date"));
        Set<String> setB = new LinkedHashSet<>(Arrays.asList("banana", "date", "fig", "grape"));
        System.out.println(symmetricDifference(setA, setB));
    }
}