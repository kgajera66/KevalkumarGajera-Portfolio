DROP TABLE IF EXISTS netflix_records;

CREATE TABLE netflix_records 
	(
		show_id VARCHAR(6) PRIMARY KEY,
		type VARCHAR(10),
		title VARCHAR(150),
		director VARCHAR(208),
		casts VARCHAR(1000),
		country VARCHAR(150),
		date_added VARCHAR(50),
		release_year INT,
		rating VARCHAR(10),
		duration VARCHAR(15),
		listed_in VARCHAR(100),
		description VARCHAR(250)

	);

SELECT * FROM netflix_records
LIMIT 10;

-- 1. Top 10 directors who have directed the most content on Netflix
SELECT director, COUNT(*) AS content_count
FROM netflix_records
WHERE director IS NOT NULL
GROUP BY director
ORDER BY content_count DESC
LIMIT 10;

-- 2. Count content by country for the last 5 years
SELECT country, COUNT(*) AS content_count
FROM netflix_records
WHERE TO_DATE(date_added, 'Month DD, YYYY') >= (CURRENT_DATE - INTERVAL '5 years')
GROUP BY country
ORDER BY content_count DESC;

-- 3️⃣ Average movie duration by rating
-- Assumes duration is in the format '90 min'
SELECT rating,
       AVG(CAST(SPLIT_PART(duration, ' ', 1) AS INTEGER)) AS avg_duration
FROM netflix_records
WHERE type = 'Movie'
  AND duration ~ '^[0-9]+'
GROUP BY rating
ORDER BY avg_duration DESC;


-- 4️⃣ Most common genre combinations
SELECT listed_in, COUNT(*) AS count
FROM netflix_records
GROUP BY listed_in
ORDER BY count DESC
LIMIT 10;


-- 5️⃣ Movies with same title but different release years
SELECT title, COUNT(DISTINCT release_year) AS versions
FROM netflix_records
GROUP BY title
HAVING COUNT(DISTINCT release_year) > 1
ORDER BY versions DESC;


-- 6️⃣ Directors with most diverse content (most genres covered)
SELECT director, COUNT(DISTINCT listed_in) AS genre_count
FROM netflix_records
WHERE director IS NOT NULL
GROUP BY director
ORDER BY genre_count DESC
LIMIT 10;


-- 7️⃣ Top 5 countries with highest average content duration
-- Works for movies (duration like '90 min')
SELECT country,
       AVG(CAST(SPLIT_PART(duration, ' ', 1) AS INTEGER)) AS avg_duration
FROM netflix_records
WHERE duration ~ '^[0-9]+'
GROUP BY country
ORDER BY avg_duration DESC
LIMIT 5;


-- 8️⃣ Count content added per month in the last 2 years
SELECT TO_CHAR(TO_DATE(date_added, 'Month DD, YYYY'), 'YYYY-MM') AS month,
       COUNT(*) AS content_count
FROM netflix_records
WHERE TO_DATE(date_added, 'Month DD, YYYY') >= (CURRENT_DATE - INTERVAL '2 years')
GROUP BY month
ORDER BY month;


-- 9️⃣ Actors appearing in both Movies and TV Shows
SELECT casts
FROM netflix_records
WHERE casts IS NOT NULL
GROUP BY casts
HAVING SUM(CASE WHEN type='Movie' THEN 1 ELSE 0 END) > 0
   AND SUM(CASE WHEN type='TV Show' THEN 1 ELSE 0 END) > 0
ORDER BY casts;


-- 🔟 Identify trending genres in India in the last 5 years
SELECT listed_in AS genre,
       COUNT(*) AS content_count
FROM netflix_records
WHERE country ILIKE '%India%'
  AND TO_DATE(date_added, 'Month DD, YYYY') >= (CURRENT_DATE - INTERVAL '5 years')
GROUP BY listed_in
ORDER BY content_count DESC
LIMIT 10;