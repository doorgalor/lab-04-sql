-- Rebuild the media schema from scratch so the script can be rerun safely.
DROP TABLE IF EXISTS posts;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    user_id INT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    joined_at DATETIME NOT NULL
);

CREATE TABLE posts (
    post_id INT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    body TEXT,
    published_at DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (user_id)
);

INSERT INTO users (user_id, username, email, joined_at) VALUES (1, 'ada', 'ada@example.com', '2023-01-12 09:15:00');
INSERT INTO users (user_id, username, email, joined_at) VALUES (2, 'ben', 'ben@example.com', '2023-02-03 14:22:00');
INSERT INTO users (user_id, username, email, joined_at) VALUES (3, 'cara', 'cara@example.com', '2023-03-18 11:05:00');
INSERT INTO users (user_id, username, email, joined_at) VALUES (4, 'diego', 'diego@example.com', '2023-04-09 16:40:00');
INSERT INTO users (user_id, username, email, joined_at) VALUES (5, 'elena', 'elena@example.com', '2023-05-21 08:55:00');
INSERT INTO users (user_id, username, email, joined_at) VALUES (6, 'farah', 'farah@example.com', '2023-06-30 13:10:00');
INSERT INTO users (user_id, username, email, joined_at) VALUES (7, 'gio', 'gio@example.com', '2023-07-14 10:25:00');
INSERT INTO users (user_id, username, email, joined_at) VALUES (8, 'hana', 'hana@example.com', '2023-08-02 17:45:00');
INSERT INTO users (user_id, username, email, joined_at) VALUES (9, 'ivan', 'ivan@example.com', '2023-09-19 12:00:00');
INSERT INTO users (user_id, username, email, joined_at) VALUES (10, 'jules', 'jules@example.com', '2023-10-27 15:30:00');

INSERT INTO posts (post_id, user_id, title, body, published_at) VALUES (1, 1, 'Welcome to the archive', 'First note on how this media library is organized.', '2024-01-05 09:00:00');
INSERT INTO posts (post_id, user_id, title, body, published_at) VALUES (2, 1, 'Indexing tips', 'A short guide to tagging recordings before upload.', '2024-02-11 10:30:00');
INSERT INTO posts (post_id, user_id, title, body, published_at) VALUES (3, 2, 'Field notes from March', 'Observations from the spring recording session.', '2024-03-02 14:15:00');
INSERT INTO posts (post_id, user_id, title, body, published_at) VALUES (4, 3, 'Why metadata matters', 'Titles and dates make later joins possible.', '2024-03-20 11:45:00');
INSERT INTO posts (post_id, user_id, title, body, published_at) VALUES (5, 4, 'Studio checklist', 'Microphones, levels, and a backup copy.', '2024-04-08 16:05:00');
INSERT INTO posts (post_id, user_id, title, body, published_at) VALUES (6, 5, 'Summer playlist draft', 'Ten tracks queued for the June release.', '2024-06-01 08:20:00');
INSERT INTO posts (post_id, user_id, title, body, published_at) VALUES (7, 6, 'Interview outline', 'Questions for the guest episode next week.', '2024-06-18 13:40:00');
INSERT INTO posts (post_id, user_id, title, body, published_at) VALUES (8, 7, 'Edit log', 'Cuts made after the first listen-through.', '2024-07-09 15:55:00');
INSERT INTO posts (post_id, user_id, title, body, published_at) VALUES (9, 8, 'Caption draft', 'Working captions for the lecture recording.', '2024-08-22 09:35:00');
INSERT INTO posts (post_id, user_id, title, body, published_at) VALUES (10, 9, 'Release notes', 'What changed between the rough cut and the final.', '2024-09-14 18:10:00');
INSERT INTO posts (post_id, user_id, title, body, published_at) VALUES (11, 10, 'Listener questions', 'Questions submitted after the last episode.', '2024-10-03 12:25:00');
INSERT INTO posts (post_id, user_id, title, body, published_at) VALUES (12, 2, 'Follow-up recording', 'A second take that replaces the March session.', '2024-11-12 17:00:00');
