drop database ott;
create database if not exists ott;
use ott;


CREATE TABLE `subscription` (
  `SubscriptionID` int NOT NULL,
  `Subscription_Name` varchar(255) DEFAULT NULL,
  `Price` float DEFAULT NULL,
  PRIMARY KEY (`SubscriptionID`)
);
CREATE TABLE `user` (
  `UserID` int NOT NULL AUTO_INCREMENT,
  `Username` varchar(255)  NOT NULL,
  `Password` varchar(255)  NOT NULL,
  `Email` varchar(255)  NOT NULL,
  `Name` varchar(255)  NOT NULL,
  `Subscription_ID` int  NOT NULL,
  `Role` enum('Admin','User') default 'User',
  PRIMARY KEY (`UserID`),
  KEY `Subscription_ID` (`Subscription_ID`),
  CONSTRAINT `user_ibfk_1` FOREIGN KEY (`Subscription_ID`) REFERENCES `subscription` (`SubscriptionID`)
);
CREATE TABLE `content` (
  `ContentID` int AUTO_INCREMENT,
  `Title` varchar(255) DEFAULT NULL,
  `Description` varchar(255) DEFAULT NULL,
  `Release_Date` date DEFAULT NULL,
  `Duration` int DEFAULT NULL,
  `Rating` float DEFAULT NULL,
  `ContentGenre` varchar(255) DEFAULT NULL,
  `image` varchar(255) DEFAULT NULL,
  `Video_Name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`ContentID`)
);

CREATE TABLE `review` (
  `ReviewID` int auto_increment,
  `UserID` int  NOT NULL,
  `ContentID` int  NOT NULL,
  `Rating` float  NOT NULL,
  `Comment` varchar(255)  NOT NULL,
  `Timestamp` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`ReviewID`),
  KEY `UserID` (`UserID`),
  KEY `ContentID` (`ContentID`),
  CONSTRAINT `review_ibfk_1` FOREIGN KEY (`UserID`) REFERENCES `user` (`UserID`),
  CONSTRAINT `review_ibfk_2` FOREIGN KEY (`ContentID`) REFERENCES `content` (`ContentID`) on delete cascade
);





-- Insert data
INSERT INTO `content` (`ContentID`, `Title`, `Description`, `Release_Date`, `Duration`, `Rating`, `ContentGenre`, `image`, `Video_Name`)
VALUES
  (1, 'The Shawshank Redemption', 'Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.', '1994-09-23', 142, 9.3, 'Drama', 'shawshank.jpg', 'shawshank.mp4'),
  (2, 'The Godfather', 'The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.', '1972-03-24', 175, 9.2, 'Crime', NULL, 'godfather.mp4'),
  (3, 'The Dark Knight', 'When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.', '2008-07-18', 152, 9, 'Action', NULL, 'dark_knight.mp4');

INSERT INTO `subscription` (`SubscriptionID`, `Subscription_Name`, `Price`)
VALUES
(0,'Admin',0),
  (1, 'Basic', 9.99),
  (2, 'Premium', 14.99);

INSERT INTO `user` (`UserID`, `Username`, `Password`, `Email`, `Name`, `Subscription_ID`,`Role`)
VALUES  (1, 'myself', 'password', 'myself@example.com', 'Myself', 0,'Admin')

DELIMITER //
CREATE TRIGGER calculate_average_rating
AFTER INSERT ON review
FOR EACH ROW
BEGIN
    DECLARE total_rating FLOAT;
    DECLARE total_reviews INT;
    DECLARE average_rating FLOAT;

    -- Calculate total rating and total reviews for the content
    SELECT SUM(Rating), COUNT(*) INTO total_rating, total_reviews
    FROM review
    WHERE ContentID = NEW.ContentID;

    -- Update the average rating in the content table
    IF total_reviews > 0 THEN
        SET average_rating = total_rating / total_reviews;

        UPDATE content
        SET Rating = average_rating
        WHERE ContentID = NEW.ContentID;
    END IF;
END;
//
DELIMITER ;
DELIMITER //
CREATE FUNCTION CalcTotalRevenue(p_subscription_id INT) 
RETURNS FLOAT DETERMINISTIC
BEGIN    
DECLARE total_revenue FLOAT;
-- Calculate total revenue for the specified subscription ID
SELECT SUM(s.Price) INTO total_revenue
FROM subscription s     
INNER JOIN user u ON s.SubscriptionID = u.Subscription_ID     
WHERE u.Subscription_ID = p_subscription_id;      
RETURN total_revenue;
END;
//
DELIMITER ;
--   (2, 'a', 'a', 'a@a.com', 'a', 'a', 'a', NULL),
--   (3, 'K', 'K', '1@gmail.com', 'b', NULL, NULL, 1),
--   (4, 'v', 'v', 'k@v.com', 'v', NULL, NULL, 1);

-- INSERT INTO `review` (`ReviewID`, `UserID`, `ContentID`, `Rating`, `Comment`, `Timestamp`)
-- VALUES
--   (1, 1, 1, 9, 'Great movie!', '2023-11-20 12:00:00'),
--   (2, 1, 2, 9.5, 'Classic film.', '2023-11-20 12:30:00'),
--   (3, 1, 3, 8.5, 'Amazing performance by Heath Ledger.', '2023-11-20 13:00:00');
