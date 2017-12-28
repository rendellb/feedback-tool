SELECT create_timestamp, update_timestamp, feedback, queue, last_user, status_l2, status_l3, status_l4, assignee, uuid, level, response, inquisitor 

FROM submissions 

WHERE feedback IS NOT NULL 
AND verified = 1 

ORDER BY STR_TO_DATE(create_timestamp, '%Y-%m-%d %H:%M:%S') ASC