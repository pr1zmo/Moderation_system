def check(word: str) -> int:
    print(word, 0)

def tokenize(words: list) -> int:
    for i in range(len(words)):
        if i + 1 < len(words):
            check(words[i] + " " + words[i + 1])

c = "You are so fucking dumb"
l = c.split()
print(tokenize(l))
