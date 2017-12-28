SELECT create_timestamp, update_timestamp, feedback, queue, last_user, status_l2, status_l3, status_l4, assignee, uuid, level 

FROM submissions 

WHERE uuid = '" + str(uuid) + "' 
AND feedback IS NOT NULL 
AND verified = 1