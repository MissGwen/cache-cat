import redis

r = redis.Redis(
    host='localhost',
    port=6379,
    decode_responses=True
)

r.bf().reserve("bf1", 0.01, 1000)
print(r.bf().add("bf1", "user1"))
r.bf().madd("bf1", "user1", "user2", "user3")
print(r.bf().exists("bf1", "user2"))
print(r.bf().exists("bf1", "user3"))
r.bf().mexists("bf1", "user2", "user3")
info = r.bf().info("bf1")
print(info.__dict__)
r.bf().insert("my_filter", ["apple", "banana", "orange"])
print(r.bf().exists("my_filter", "appl1e"))
iterator = 0

chunks = []
iterator = 0

while True:
    iterator, data = r.bf().scandump("bf1", iterator)

    print(
        "iterator:",
        iterator,
        "data size:",
        len(data) if data else None,
    )

    if iterator == 0:
        break

    # 保存 SCANDUMP 返回的 iterator + data
    chunks.append((iterator, data))

# 2. Load 到一个新的 Bloom Filter
dst_key = "bf1_restored"

# 测试前确保目标 key 不存在
r.delete(dst_key)

for iterator, data in chunks:
    result = r.bf().loadchunk(dst_key, iterator, data)
    print(
        "loadchunk:",
        iterator,
        len(data),
        result,
    )

# 3. 验证恢复结果
print("original user1:", r.bf().exists("bf1", "user1"))
print("restored user1:", r.bf().exists(dst_key, "user1"))

print("original user2:", r.bf().exists("bf1", "user2"))
print("restored user2:", r.bf().exists(dst_key, "user2"))

print("original user3:", r.bf().exists("bf1", "user3"))
print("restored user3:", r.bf().exists(dst_key, "user3"))

# 4. 比较 info
print("original info:", r.bf().info("bf1").__dict__)
print("restored info:", r.bf().info(dst_key).__dict__)
