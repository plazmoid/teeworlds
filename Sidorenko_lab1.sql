USE master
GO

ALTER DATABASE #Sidorenko set single_user with rollback immediate
GO

IF EXISTS (SELECT name FROM sys.databases WHERE name = N'#Sidorenko')
	DROP DATABASE #Sidorenko
GO

CREATE DATABASE #Sidorenko
GO

USE #Sidorenko
GO

CREATE SCHEMA Weather
GO

CREATE TABLE #Sidorenko.Weather.stations (
	station_id INT IDENTITY(1,1) NOT NULL,
	station_name VARCHAR(30) NOT NULL,
	CONSTRAINT PK_stID PRIMARY KEY (station_id)
);
GO

CREATE TABLE #Sidorenko.Weather.measurement_types (
	/*mea_t_id INT IDENTITY(1,1) NOT NULL,*/
	mea_type VARCHAR(20) NOT NULL,
	mea_ending VARCHAR(10) NOT NULL,
	CONSTRAINT PK_mea_tID PRIMARY KEY (mea_type)
);
GO

CREATE TABLE #Sidorenko.Weather.measurements (
	mea_id INT IDENTITY(1,1) NOT NULL,
	station_id INT NOT NULL,
	mea_type VARCHAR(20) NOT NULL,
	mea_val INT NOT NULL,
	mea_date DATE NOT NULL,
	CONSTRAINT PK_meaID PRIMARY KEY (mea_id),
	CONSTRAINT FK_meaID FOREIGN KEY (mea_type) REFERENCES #Sidorenko.Weather.measurement_types(mea_type),
	CONSTRAINT FK_stID FOREIGN KEY (station_id) REFERENCES #Sidorenko.Weather.stations(station_id)
);
GO

INSERT INTO #Sidorenko.Weather.stations
	(station_name) VALUES
	(N'Арктика-1'),
	(N'Аляска-2'),
	(N'Новая Земля-3')
GO

INSERT INTO #Sidorenko.Weather.measurement_types
	(mea_type, mea_ending) VALUES
	(N'Температура',	N'гр.'),
	(N'Давление',		N'мм'),
	(N'Влажность',		N'%')
GO

INSERT INTO #Sidorenko.Weather.measurements
	(station_id, mea_type, mea_val, mea_date) VALUES
	(1, N'Температура', 30, '20020613'),
	(2, N'Давление', 740, '20020613'),
	(2,	N'Влажность', 14, '20020613'),
	(3,	N'Температура', 25, '20020827'),
	(3,	N'Давление', 738, '20020827'),
	(2,	N'Влажность', 17, '20020827'),
	(1,	N'Температура', 32, '20020613'),
	(2,	N'Температура', 25, '20020613'),
	(2,	N'Давление', 30, '20020613'),
	(1,	N'Влажность', 20, '20020613')


SELECT Станция, Тип_измерений, AVG(Значение) as Среднее, ед_изм, Дата FROM
	(SELECT	stations.station_name AS Станция,
		measurements.mea_type AS Тип_измерений, 
		mea_val AS Значение,
		mea_ending AS ед_изм,
		mea_date AS Дата
		FROM (Weather.measurements INNER JOIN Weather.stations ON stations.station_id = measurements.station_id
		INNER JOIN Weather.measurement_types ON measurements.mea_type = measurement_types.mea_type)
	) AS result
	GROUP BY result.Станция, result.Тип_измерений, result.ед_изм, result.Дата
	ORDER BY result.Станция
	/*
SELECT stations.station_name AS Станция,
	measurements.mea_type AS Тип_измерений, 
	mea_val AS Значение,
	mea_ending AS ед_изм,
	mea_date AS Дата
	FROM (Weather.measurements INNER JOIN Weather.stations ON stations.station_id = measurements.station_id
	INNER JOIN Weather.measurement_types ON measurements.mea_type = measurement_types.mea_type)*/