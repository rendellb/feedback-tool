SELECT hs.create_timestamp, hs.update_timestamp, hs.feedback, hs.queue, hs.last_user, hs.assignee, hs.uuid, hs.level 

FROM submissions hs 
LEFT JOIN responses hr ON hr.feedback_uuid = hs.uuid 

WHERE hs.feedback IS NOT NULL 
AND hs.verified = 1 
AND (hr.response IS NULL OR hr.response = '') 
AND hs.claimed IS NULL