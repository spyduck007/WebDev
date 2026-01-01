DROP TABLE IF EXISTS checkouts;
DROP TABLE IF EXISTS books;

CREATE TABLE books (
    book_id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    author_first TEXT NOT NULL,
    author_last TEXT NOT NULL,
    publication_year INTEGER NOT NULL
);

CREATE TABLE checkouts (
    checkout_id INTEGER PRIMARY KEY,
    book_id INTEGER NOT NULL,
    patron INTEGER NOT NULL,
    checkout_date TEXT NOT NULL,
    checkin_date TEXT NOT NULL,
    fines REAL NOT NULL,
    FOREIGN KEY (book_id) REFERENCES books(book_id)
);

INSERT INTO books (book_id, title, author_first, author_last, publication_year) VALUES
(1, 'Why Rocks are Awesome', 'Melissa', 'Anderson', 1990),
(2, 'How to pick up big rocks', 'Reginald Worthington', 'Farnsworth III', 1974),
(3, 'In Search of the World’s Most Interesting Rocks', 'Shaun', 'O''Malley', 2006),
(4, 'Hidden Secrets: The Story of Rocks', 'Liam Michael', 'Walker', 2014),
(5, 'North American Cloud Patterns, A Survey', 'Victoria', 'Collins', 2008),
(6, 'Once upon a cloud: Tales On the Density of Dreams and Boulders', 'George', 'Brown', 2017),
(7, 'The Magesty of Tectonic Plates', 'Anna Marie', 'Green', 1999),
(8, 'Geothermal Structures Beneath the Sea Floor', 'Jameson', 'Clark', 2008),
(9, 'Colliding Continents and the Rocks they Create', 'Olivia', 'Harrison', 1978),
(10, 'A Cloud Collector''s Guide to Grounded Thoughts', 'Katherine', 'LeBlanc', 2020),
(11, 'How Rain Makes Rocks Beautiful', 'Brian', 'Davis', 2011),
(12, 'Cloudy with a Chance of Pebbles', 'Jameson', 'Clark', 2023),
(13, 'Fog on the Fault Line: A Memoir in Stone and Sky', 'Fiona', 'Murray', 2005);

INSERT INTO checkouts (checkout_id, book_id, patron, checkout_date, checkin_date, fines) VALUES
(1, 1, 1005, '2024-07-15', '2024-08-10', 3.75),
(2, 1, 1010, '2024-10-14', '2024-11-04', 0),
(3, 13, 1929, '2025-01-12', '2025-02-10', 6),
(4, 3, 1005, '2025-04-24', '2025-05-08', 0),
(5, 8, 1010, '2020-05-16', '2026-06-02', 0),
(6, 11, 1003, '2021-04-11', '2021-05-11', 6.75),
(7, 8, 1755, '2023-05-20', '2023-06-07', 0),
(8, 4, 1209, '2024-08-25', '2024-09-18', 2.25),
(9, 2, 1003, '2021-04-11', '2021-04-27', 0),
(10, 2, 1003, '2022-06-04', '2022-06-24', 0),
(11, 2, 1003, '2023-11-09', '2023-11-28', 0),
(12, 2, 1003, '2025-03-15', '2025-04-12', 5.25);
