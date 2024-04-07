from requests import get, post, delete

# print(get('http://localhost:5000/api/news').json())
# print(get('http://localhost:5000/api/news/1').json())
# print(get('http://localhost:5000/api/news/100').json())
# print(get('http://localhost:5000/api/news/bed_riquest').json())
#
# print(post('http://localhost:5000/api/news', json={}).json())
# print(post('http://localhost:5000/api/news', json={'title': 'Zagolovok'}).json())
# print(post('http://localhost:5000/api/news', json={
#     'title': 'Zagolovok',
#     'content': 'Content news',
#     'user_id': 1,
#     'is_private': False}).json())


print(delete('http://localhost:5000/api/news/3').json())
print(delete('http://localhost:5000/api/news/100').json())