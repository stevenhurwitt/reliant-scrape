CREATE TABLE `daily_use` (
  `Date` text,
  `Usage (kWh)` double DEFAULT NULL,
  `Cost ($)` double DEFAULT NULL,
  `Hi` bigint DEFAULT NULL,
  `Low` bigint DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci