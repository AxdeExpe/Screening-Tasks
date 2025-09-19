import string
import matplotlib.pyplot as plt

class WordAnalysis:
    def __init__(self, input_string: str) -> None:

        if not isinstance(input_string, str):
            raise TypeError("Input must be a string")

        self.input_string = input_string

    def __check_2d_list(self, word_counted_list: list) -> None:

        if not isinstance(word_counted_list, list):
            raise TypeError("Input must be a list")
        
        if not all(isinstance(word, list) for word in word_counted_list):
            raise TypeError("Input must be a 2D list")

        return

    def __prepare_string(self) -> list:

        input_string_lower = self.input_string.lower()
        input_string_splited = input_string_lower.split()
        input_string_punc_removed = [word.translate(str.maketrans('', '', string.punctuation)) for word in input_string_splited]
        
        return input_string_punc_removed
    
    def count_duplicates(self) -> list:

        prepared_list = self.__prepare_string()

        words_counted_list = {}

        for word in prepared_list:
            if word in words_counted_list:
                words_counted_list[word] += 1
            else:
                words_counted_list[word] = 1

        return [[word, count] for word, count in words_counted_list.items()]

    def sort_by_count_or_alphabetically_top_n(self, word_counted_list: list, top_n: int = 5) -> list:

        self.__check_2d_list(word_counted_list)

        if not isinstance(top_n, int):
            raise TypeError("Input must be an integer")

        if top_n <= 0:
            raise ValueError("Input must be a positive integer")

        sorted_list = sorted(word_counted_list, key=lambda x: (-x[1], x[0]))
        return sorted_list[:top_n]
    
    def plot_word_count(self, word_counted_list: list, save_path: str = "word_count.png") -> None:

        self.__check_2d_list(word_counted_list)

        word_list = [word[0] for word in word_counted_list]
        count_list = [word[1] for word in word_counted_list]

        plt.bar(word_list, count_list)
        plt.xlabel("Words")
        plt.ylabel("Count")
        plt.title("Word Count")
        plt.savefig(save_path)
        plt.show()
        
    
if __name__ == "__main__":
    word = input("Enter a text: ")
    word_analysis = WordAnalysis(word)

    duplicates = word_analysis.count_duplicates()
    print(duplicates)

    sorted_list = word_analysis.sort_by_count_or_alphabetically_top_n(duplicates)
    print(sorted_list)
    word_analysis.plot_word_count(sorted_list)