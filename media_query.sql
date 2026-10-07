-- Posts published in the second half of 2024, with the author attached.
SELECT
    users.username,
    users.email,
    posts.title,
    posts.published_at
FROM users
INNER JOIN posts ON users.user_id = posts.user_id
WHERE posts.published_at >= '2024-06-01'
ORDER BY posts.published_at;
