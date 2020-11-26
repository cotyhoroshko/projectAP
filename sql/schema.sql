CREATE TABLE advertisements(
id INT AUTO_INCREMENT PRIMARY KEY,
modifier ENUM('public', 'local'),
summary VARCHAR (50),
author_id INT,
description TINYTEXT,
topic VARCHAR(15)
);

CREATE TABLE users(
id INT AUTO_INCREMENT PRIMARY KEY,
name VARCHAR(30),
email VARCHAR(30),
password_hash VARCHAR(512)
)