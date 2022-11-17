SHOW DATABASES;
USE attractions_db;
SHOW TABLES;

SELECT * FROM taipei_attractions;
DROP TABLE  taipei_attractions;

INSERT INTO member(name,username,password,follower_count)
VALUES(test,test,test,0);
SELECT member.name,message.content FROM message INNER JOIN member ON message.member_id=member.i

