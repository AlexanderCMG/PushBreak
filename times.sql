SELECT
    participant_id,
    MIN(session_start_time) AS first_session_start,
    MAX(session_end_time) AS last_session_end
FROM
    "Experiments"
WHERE
    is_alternate = TRUE
GROUP BY
    participant_id
ORDER BY
    participant_id;
