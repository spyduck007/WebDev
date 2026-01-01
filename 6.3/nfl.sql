SELECT s.s_name, s.s_capacity
FROM teams t
JOIN stadiums s ON t.t_stadium = s.s_id
WHERE t.t_conference = 'NFC'
ORDER BY s.s_capacity DESC
LIMIT 1;



SELECT p.p_first, p.p_last, p.p_height
FROM players p
JOIN teams t ON p.p_team = t.t_id
WHERE p.p_position = 'QB'
AND t.t_conference = 'NFC'
ORDER BY p.p_height DESC
LIMIT 1;



SELECT p.p_first, p.p_last, p.p_height
FROM players p
JOIN teams t ON p.p_team = t.t_id
WHERE p.p_position = 'K'
AND t.t_conference = 'AFC'
AND t.t_division = 'South'
ORDER BY p.p_height ASC
LIMIT 1;



SELECT p.p_first, p.p_last
FROM players p
JOIN teams t ON p.p_team = t.t_id
WHERE p.p_position = 'RB'
AND t.t_id = (
    SELECT t_id
    FROM teams
    WHERE t_conference = 'NFC'
    AND t_division = 'North'
    ORDER BY t_founded ASC
    LIMIT 1
);



SELECT s.s_name, s.s_year
FROM stadiums s
LEFT JOIN teams t ON t.t_stadium = s.s_id
WHERE s.s_state = 'CA'
ORDER BY s.s_year ASC
LIMIT 1;
