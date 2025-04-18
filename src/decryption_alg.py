from Crypto.Util.number import inverse, long_to_bytes
import math




# Public key components (small for demo)
n = 2534669  # modulus (p * q)
e = 65537    # public exponent
ciphertext = 587856  # some encrypted number

#generating candidate primes for factors
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

# Step 1: Factor n (brute force, since it's small)
def factor(n):
    prime_candidates = get_candidates(n)
    for p in prime_candidates:
        if n % p == 0:
            return p, n // p
        yield p, n//p
    raise ValueError("Failed to factor n")


def do_hack():

    for p, q in factor(n):
        print(f"Found factors: p = {p}, q = {q}")

    # Step 2: Compute φ(n)
    phi = (p - 1) * (q - 1)

    # Step 3: Compute private exponent d
    d = inverse(e, phi)
    print(f"Private exponent d = {d}")

    # Step 4: Decrypt the message
    plaintext_int = pow(ciphertext, d, n)
    plaintext = long_to_bytes(plaintext_int)
    print(f"Decrypted message: {plaintext}")
