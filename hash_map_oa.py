# Name: Alex Schectman
# OSU Email: schectma@oregonstate.edu
# Course: CS261 - Data Structures
# Assignment: 6
# Due Date: 08/14/2024
# Description: Implementation of a hash map data structure that uses
#               open addressing to resolve collisions.

from a6_include import (DynamicArray, DynamicArrayException, HashEntry,
                        hash_function_1, hash_function_2)


class HashMap:
    def __init__(self, capacity: int, function) -> None:
        """
        Initialize new HashMap that uses
        quadratic probing for collision resolution
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        self._buckets = DynamicArray()

        # capacity must be a prime number
        self._capacity = self._next_prime(capacity)
        for _ in range(self._capacity):
            self._buckets.append(None)

        self._hash_function = function
        self._size = 0

    def __str__(self) -> str:
        """
        Override string method to provide more readable output
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        out = ''
        for i in range(self._buckets.length()):
            out += str(i) + ': ' + str(self._buckets[i]) + '\n'
        return out

    def _next_prime(self, capacity: int) -> int:
        """
        Increment from given number to find the closest prime number
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        if capacity % 2 == 0:
            capacity += 1

        while not self._is_prime(capacity):
            capacity += 2

        return capacity

    @staticmethod
    def _is_prime(capacity: int) -> bool:
        """
        Determine if given integer is a prime number and return boolean
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        if capacity == 2 or capacity == 3:
            return True

        if capacity == 1 or capacity % 2 == 0:
            return False

        factor = 3
        while factor ** 2 <= capacity:
            if capacity % factor == 0:
                return False
            factor += 2

        return True

    def get_size(self) -> int:
        """
        Return size of map
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        return self._size

    def get_capacity(self) -> int:
        """
        Return capacity of map
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        return self._capacity

    # ------------------------------------------------------------------ #

    def put(self, key: str, value: object) -> None:
        """
        Updates specified key/value pair in the hash map.
        Replaces value if key exists. Adds if key doesn't exist.
        """
        if self.table_load() >= 0.5:
            self.resize_table(self._capacity * 2)

        idx = self._hash_function(key) % self._capacity

        j = 0
        while idx < self._capacity:
            current = self._buckets.get_at_index(idx)
            if not current:
                self._buckets.set_at_index(idx, HashEntry(key, value))
                self._size += 1
                break
            if current and current.key == key:
                self._buckets.set_at_index(idx, HashEntry(key, value))
                break
            else:
                idx = self._quadratic_probe(idx, j)
                j += 1

    def resize_table(self, new_capacity: int) -> None:
        """
        Changes the capacity of the underlying table.
        """
        if new_capacity < self.get_size():
            return
        if not self._is_prime(new_capacity):
            new_capacity = self._next_prime(new_capacity)

        temp = DynamicArray()
        pos = 0
        while pos < new_capacity:
            temp.append(None)
            pos += 1

        pos = 0
        while pos < self._capacity:
            if self._buckets.get_at_index(pos):
                idx = self._hash_function(self._buckets.get_at_index(pos).key) % new_capacity
                temp.set_at_index(idx, HashEntry(self._buckets.get_at_index(pos).key, self._buckets.get_at_index(pos).value))
            pos += 1

        # Clear and expand original array, then transfer from temp
        self.clear()

        pos = self._capacity
        while pos < new_capacity:
            self._buckets.append(None)
            pos += 1
        self._capacity = new_capacity

        pos = 0
        while pos < self._capacity:
            if temp.get_at_index(pos):
                self._buckets.set_at_index(pos, temp.get_at_index(pos))
                self._size += 1
            pos += 1

    def table_load(self) -> float:
        """
        Returns current hash table load factor.
        """
        loadFactor = self.get_size() / self.get_capacity()
        return loadFactor

    def empty_buckets(self) -> int:
        """
        Returns quantity of empty buckets in hash table.
        """
        empty = 0
        pos = 0
        while pos < self._capacity:
            if not self._buckets.get_at_index(pos) or self._buckets.get_at_index(pos).is_tombstone:
                empty += 1
            pos += 1

        return empty

    def get(self, key: str) -> object:
        """
        Returns value associated with specified key.
        """
        idx = self._hash_function(key) % self._capacity

        j = 1
        while True:
            if self._buckets.get_at_index(idx) and self._buckets.get_at_index(idx).key == key:
                return self._buckets.get_at_index(idx)
            idx = self._quadratic_probe(idx, j)

    def contains_key(self, key: str) -> bool:
        """
        Returns True if specified key is in hash map.
        """
        # idx = self._hash_function(key) % self._capacity
        #
        # pos = 0
        #
        # while pos < self._capacity:
        #     if self._buckets.get_at_index(idx) and self._buckets.get_at_index(idx).key == key:
        #         return True
        #     idx = (idx + pos ** 2) % self._capacity

        if self.get(key):
            return True

        return False

    def remove(self, key: str) -> None:
        """
        Removes key and associated value from hash map.
        Remember to set tombstone value!
        """
        if not self.contains_key(key):
            return

        idx = self._hash_function(key) % self._capacity

        j = 1
        while True:
            current = self._buckets.get_at_index(idx)
            if current.key == key:
                self._buckets.set_at_index(idx, HashEntry(None, None))
                self._buckets.get_at_index(idx).is_tombstone = True
                self._size -= 1
                return
            idx = self._quadratic_probe(idx, j)
            j += 1

    def get_keys_and_values(self) -> DynamicArray:
        """
        Returns an unordered dynamic array where each index
        contains a tuple of a key/value pair stored in the hash map.
        """
        kvTuples = DynamicArray()

        pos = 0
        while pos < self._capacity:
            if self._buckets.get_at_index(pos):
                kvTuples.append((self._buckets.get_at_index(pos).key, self._buckets.get_at_index(pos).value))
            pos += 1

        return kvTuples

    def clear(self) -> None:
        """
        Clears all contents of hash map.
        """
        pos = 0
        while pos < self._capacity:
            if self._buckets.get_at_index(pos):
                self._buckets.set_at_index(pos, None)
            pos += 1
        self._size = 0

    def __iter__(self):
        """
        TODO: Write this implementation
        """
        pass

    def __next__(self):
        """
        TODO: Write this implementation
        """
        pass

    # --------------------------User-defined functions------------------------- #
    def _linear_probe(self, i, j):
        return i + j

    def _quadratic_probe(self, i, j):
        return i + j ** 2

    def _double_hash(self, i: int, j: int, h, k) -> int:
        return i + j * h(k)


# ------------------- BASIC TESTING ---------------------------------------- #

if __name__ == "__main__":

    print("\nPDF - put example 1")
    print("-------------------")
    m = HashMap(53, hash_function_1)
    for i in range(150):
        m.put('str' + str(i), i * 100)
        if i % 25 == 24:
            print(m.empty_buckets(), round(m.table_load(), 2), m.get_size(), m.get_capacity())

    # print("\nPDF - put example 2")
    # print("-------------------")
    # m = HashMap(41, hash_function_2)
    # for i in range(50):
    #     m.put('str' + str(i // 3), i * 100)
    #     if i % 10 == 9:
    #         print(m.empty_buckets(), round(m.table_load(), 2), m.get_size(), m.get_capacity())

    # print("\nPDF - resize example 1")
    # print("----------------------")
    # m = HashMap(20, hash_function_1)
    # m.put('key1', 10)
    # print(m.get_size(), m.get_capacity(), m.get('key1'), m.contains_key('key1'))
    # m.resize_table(30)
    # print(m.get_size(), m.get_capacity(), m.get('key1'), m.contains_key('key1'))
    #
    # print("\nPDF - resize example 2")
    # print("----------------------")
    # m = HashMap(75, hash_function_2)
    # keys = [i for i in range(25, 1000, 13)]
    # for key in keys:
    #     m.put(str(key), key * 42)
    # print(m.get_size(), m.get_capacity())
    #
    # for capacity in range(111, 1000, 117):
    #     m.resize_table(capacity)
    #
    #     if m.table_load() > 0.5:
    #         print(f"Check that the load factor is acceptable after the call to resize_table().\n"
    #               f"Your load factor is {round(m.table_load(), 2)} and should be less than or equal to 0.5")
    #
    #     m.put('some key', 'some value')
    #     result = m.contains_key('some key')
    #     m.remove('some key')
    #
    #     for key in keys:
    #         # all inserted keys must be present
    #         result &= m.contains_key(str(key))
    #         # NOT inserted keys must be absent
    #         result &= not m.contains_key(str(key + 1))
    #     print(capacity, result, m.get_size(), m.get_capacity(), round(m.table_load(), 2))
    #
    # print("\nPDF - table_load example 1")
    # print("--------------------------")
    # m = HashMap(101, hash_function_1)
    # print(round(m.table_load(), 2))
    # m.put('key1', 10)
    # print(round(m.table_load(), 2))
    # m.put('key2', 20)
    # print(round(m.table_load(), 2))
    # m.put('key1', 30)
    # print(round(m.table_load(), 2))
    #
    # print("\nPDF - table_load example 2")
    # print("--------------------------")
    # m = HashMap(53, hash_function_1)
    # for i in range(50):
    #     m.put('key' + str(i), i * 100)
    #     if i % 10 == 0:
    #         print(round(m.table_load(), 2), m.get_size(), m.get_capacity())
    #
    # print("\nPDF - empty_buckets example 1")
    # print("-----------------------------")
    # m = HashMap(101, hash_function_1)
    # print(m.empty_buckets(), m.get_size(), m.get_capacity())
    # m.put('key1', 10)
    # print(m.empty_buckets(), m.get_size(), m.get_capacity())
    # m.put('key2', 20)
    # print(m.empty_buckets(), m.get_size(), m.get_capacity())
    # m.put('key1', 30)
    # print(m.empty_buckets(), m.get_size(), m.get_capacity())
    # m.put('key4', 40)
    # print(m.empty_buckets(), m.get_size(), m.get_capacity())
    #
    # print("\nPDF - empty_buckets example 2")
    # print("-----------------------------")
    # m = HashMap(53, hash_function_1)
    # for i in range(150):
    #     m.put('key' + str(i), i * 100)
    #     if i % 30 == 0:
    #         print(m.empty_buckets(), m.get_size(), m.get_capacity())
    #
    # print("\nPDF - get example 1")
    # print("-------------------")
    # m = HashMap(31, hash_function_1)
    # print(m.get('key'))
    # m.put('key1', 10)
    # print(m.get('key1'))
    #
    # print("\nPDF - get example 2")
    # print("-------------------")
    # m = HashMap(151, hash_function_2)
    # for i in range(200, 300, 7):
    #     m.put(str(i), i * 10)
    # print(m.get_size(), m.get_capacity())
    # for i in range(200, 300, 21):
    #     print(i, m.get(str(i)), m.get(str(i)) == i * 10)
    #     print(i + 1, m.get(str(i + 1)), m.get(str(i + 1)) == (i + 1) * 10)
    #
    # print("\nPDF - contains_key example 1")
    # print("----------------------------")
    # m = HashMap(11, hash_function_1)
    # print(m.contains_key('key1'))
    # m.put('key1', 10)
    # m.put('key2', 20)
    # m.put('key3', 30)
    # print(m.contains_key('key1'))
    # print(m.contains_key('key4'))
    # print(m.contains_key('key2'))
    # print(m.contains_key('key3'))
    # m.remove('key3')
    # print(m.contains_key('key3'))
    #
    # print("\nPDF - contains_key example 2")
    # print("----------------------------")
    # m = HashMap(79, hash_function_2)
    # keys = [i for i in range(1, 1000, 20)]
    # for key in keys:
    #     m.put(str(key), key * 42)
    # print(m.get_size(), m.get_capacity())
    # result = True
    # for key in keys:
    #     # all inserted keys must be present
    #     result &= m.contains_key(str(key))
    #     # NOT inserted keys must be absent
    #     result &= not m.contains_key(str(key + 1))
    # print(result)
    #
    # print("\nPDF - remove example 1")
    # print("----------------------")
    # m = HashMap(53, hash_function_1)
    # print(m.get('key1'))
    # m.put('key1', 10)
    # print(m.get('key1'))
    # m.remove('key1')
    # print(m.get('key1'))
    # m.remove('key4')
    #
    # print("\nPDF - get_keys_and_values example 1")
    # print("------------------------")
    # m = HashMap(11, hash_function_2)
    # for i in range(1, 6):
    #     m.put(str(i), str(i * 10))
    # print(m.get_keys_and_values())
    #
    # m.resize_table(2)
    # print(m.get_keys_and_values())
    #
    # m.put('20', '200')
    # m.remove('1')
    # m.resize_table(12)
    # print(m.get_keys_and_values())
    #
    # print("\nPDF - clear example 1")
    # print("---------------------")
    # m = HashMap(101, hash_function_1)
    # print(m.get_size(), m.get_capacity())
    # m.put('key1', 10)
    # m.put('key2', 20)
    # m.put('key1', 30)
    # print(m.get_size(), m.get_capacity())
    # m.clear()
    # print(m.get_size(), m.get_capacity())
    #
    # print("\nPDF - clear example 2")
    # print("---------------------")
    # m = HashMap(53, hash_function_1)
    # print(m.get_size(), m.get_capacity())
    # m.put('key1', 10)
    # print(m.get_size(), m.get_capacity())
    # m.put('key2', 20)
    # print(m.get_size(), m.get_capacity())
    # m.resize_table(100)
    # print(m.get_size(), m.get_capacity())
    # m.clear()
    # print(m.get_size(), m.get_capacity())
    #
    # print("\nPDF - __iter__(), __next__() example 1")
    # print("---------------------")
    # m = HashMap(10, hash_function_1)
    # for i in range(5):
    #     m.put(str(i), str(i * 10))
    # print(m)
    # for item in m:
    #     print('K:', item.key, 'V:', item.value)
    #
    # print("\nPDF - __iter__(), __next__() example 2")
    # print("---------------------")
    # m = HashMap(10, hash_function_2)
    # for i in range(5):
    #     m.put(str(i), str(i * 24))
    # m.remove('0')
    # m.remove('4')
    # print(m)
    # for item in m:
    #     print('K:', item.key, 'V:', item.value)
