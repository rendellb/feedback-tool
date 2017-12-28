UPDATE responses 

SET update_timestamp = NOW(), reviewed = 1 

WHERE reviewed = 0 
AND create_timestamp + interval 2 day < NOW()