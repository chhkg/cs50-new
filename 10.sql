SELECT people.name
FROM ((people
INNER JOIN directors ON directors.person_id = people.id)
INNER JOIN ratings ON ratings.movie_id = directors.movie_id)
WHERE ratings.rating >= 9.0
GROUP BY people.id;