import math
import hashlib

class BloomFilter:
    """
    In-memory Bloom Filter for high-speed duplicate detection.
    Useful for filtering duplicate telemetry event sequences before DB query.
    """
    def __init__(self, expected_elements: int = 1000000, false_positive_rate: float = 0.01):
        self.expected_elements = expected_elements
        self.false_positive_rate = false_positive_rate
        
        # Calculate bit array size (m) and number of hash functions (k)
        self.size = int(- (expected_elements * math.log(false_positive_rate)) / (math.log(2) ** 2))
        self.num_hashes = int((self.size / expected_elements) * math.log(2))
        
        # Bit array initialized to 0
        self.bit_array = [False] * self.size
        self.count = 0

    def _hashes(self, key: str):
        """Generates k hash values for key using double hashing algorithm."""
        h1 = int(hashlib.md5(key.encode('utf-8')).hexdigest(), 16)
        h2 = int(hashlib.sha256(key.encode('utf-8')).hexdigest(), 16)
        for i in range(self.num_hashes):
            yield (h1 + i * h2) % self.size

    def add(self, key: str):
        """Adds element to bloom filter."""
        for bit_index in self._hashes(key):
            self.bit_array[bit_index] = True
        self.count += 1

    def contains(self, key: str) -> bool:
        """Returns True if element is probably in the set, False if definitely not."""
        for bit_index in self._hashes(key):
            if not self.bit_array[bit_index]:
                return False
        return True

    def reset(self):
        """Clears the bloom filter."""
        self.bit_array = [False] * self.size
        self.count = 0
