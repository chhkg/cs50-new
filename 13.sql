SELECT people.name
FROM people
WHERE people.id IN (
SELECT stars.person_id
FROM stars
WHERE stars.movie_id IN (
SELECT stars.movie_id
FROM (stars
INNER JOIN people ON stars.person_id = people.id)
WHERE stars.person_id = (SELECT people.id FROM people WHERE people.name = 'Kevin Bacon' AND people.birth = '1958')))
AND NOT people.id = (SELECT people.id FROM people WHERE people.name = 'Kevin Bacon' AND people.birth = '1958')
GROUP BY people.id;