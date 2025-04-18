import math

def get_candidates(n):
    primes = [2, 3]
    for i in range(5, int(math.sqrt(n)) + 1):
        isPrime = True
        for p in primes:
            if i % p == 0:
                isPrime = False
                break;
        if isPrime:
            primes.append(i)

    return primes


print(get_candidates(1000))
