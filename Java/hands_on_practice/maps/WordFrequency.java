import java.util.*;

public class WordFrequency {

    public static void main(String[] args) {
        String text = "the cat the dog the cat sat";
        Map<String, Integer> freq = new TreeMap<>();
        for (String word : text.toLowerCase().split("\\s+")) {
            freq.merge(word, 1, Integer::sum);
        }
        System.out.println("Frequencies: " + freq);

        String best = null;
        int bestCount = -1;
        for (Map.Entry<String, Integer> entry : freq.entrySet()) {
            if (entry.getValue() > bestCount) {
                best = entry.getKey();
                bestCount = entry.getValue();
            }
        }
        System.out.println("Most frequent: " + best + " "+ bestCount);
    }
}