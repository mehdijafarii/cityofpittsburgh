-- Return all the fields from 20 records 
SELECT * FROM flights
LIMIT 20;
-- This code is not that effecient because it returned all the colomns 
-- However it is a good step in initial data expolration especially with 20 Limit


-- Return all of the destination airports and the corresponding arrival time 
-- where the take off time was before 11AM (ignore timezones)  
SELECT DESTINATION_AIRPORT, ARRIVAL_TIME
FROM flights
WHERE DEPARTURE_TIME < 1100;


-- What is the longest flight time? 
SELECT MAX(AIR_TIME) AS longest_flight_time
FROM flights;

-- I think count first query is better but I thought that not what you guys are looking 
-- maybe you want to see if I can get distict value hence below is the code
SELECT 
	count(*) AS number_of_airlines
FROM airlines;
-- or
SELECT COUNT(DISTINCT AIRLINE) AS unique_airlines
FROM flights;


-- The specific number of flights that go to a given airport 
-- The average amount of time for each of those flights is in the air   
-- The correlation between the arrival delay and the theoretical time a flight should be in the air (AIR_TIME) 
-- The correlation between distance of the flight and the actual arrival time 
-- Order the output by the most frequent destination airports, limit to the top five results
SELECT 
    DESTINATION_AIRPORT,
    COUNT(*) AS flight_count,
    AVG(AIR_TIME) AS avg_air_time,

    -- Correlation between ARRIVAL_DELAY and AIR_TIME
    (AVG(ARRIVAL_DELAY * AIR_TIME) - AVG(ARRIVAL_DELAY) * AVG(AIR_TIME)) /
    (STDDEV_POP(ARRIVAL_DELAY) * STDDEV_POP(AIR_TIME)) AS corr_arr_delay_airtime,

    -- Correlation between DISTANCE and ARRIVAL_TIME
    (AVG(DISTANCE * ARRIVAL_TIME) - AVG(DISTANCE) * AVG(ARRIVAL_TIME)) /
    (STDDEV_POP(DISTANCE) * STDDEV_POP(ARRIVAL_TIME)) AS corr_dist_arr_time

FROM flights
WHERE 
    ARRIVAL_DELAY IS NOT NULL AND
    AIR_TIME IS NOT NULL AND
    DISTANCE IS NOT NULL AND
    ARRIVAL_TIME IS NOT NULL

GROUP BY DESTINATION_AIRPORT
ORDER BY flight_count DESC
LIMIT 5;


-- 1. Real-Time Writing Consideration
-- 
-- While this dataset is now historical, assuming near real-time data ingestion changes how we’d model it:
-- 	•	Efficient real-time write model requires:
-- 	•	Minimal locking and indexing overhead.
-- 	•	Optimized data structure for sequential writes. (A primary key (e.g., auto-increment or UUID),
-- 	•	A timestamp or date field (e.g., FLIGHT_DATE),
-- 	•	Minimal constraints.
-- )


-- 2. Would My Model Be Efficient for Real-Time Writing?
--
-- Current relational model (e.g., MySQL) may not be ideal for high-frequency writes, unless tuned. Here’s how I’d improve it:
-- Model Improvements:
-- 	•	Use partitioning (by YEAR, MONTH) to speed up queries and inserts.
-- 	•	Add indexes only on read-heavy fields (DESTINATION_AIRPORT, ARRIVAL_DELAY, AIRLINE), and avoid over-indexing.
-- 	•	Consider batch inserts for real-time pipelines.
-- 	•	Use a write-optimized staging table with minimal constraints, then move to analytical tables via scheduled ETL jobs.
-- 
-- Conclusion: With these optimizations, a relational model can be efficient enough, but for high-throughput ingestion (e.g., 1000+ writes/sec), 
-- other architectures may be better maybe even go by NoSQL databases such as Dynamodb.


-- 3. I would keep the data type as they are because YEAR, MONTH, DAY, and DAY_OF_WEEK are already broken out 
-- as separate columns for flexible time-based analysis (e.g., group by month, day of week).
-- 	•	DATETIME is ideal when you need full timestamps (like 2024-05-07 10:42:00), which is not the case here.
-- 	•	Storing just a year in a DATETIME wastes space and processing time. also I think there are other data pipline dependent
-- on this so if we change the source they have to change which is a workload for team
	
	