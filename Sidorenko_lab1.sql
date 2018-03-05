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
	(N'�������-1'),
	(N'������-2'),
	(N'����� �����-3')
GO

INSERT INTO #Sidorenko.Weather.measurement_types
	(mea_type, mea_ending) VALUES
	(N'�����������',	N'��.'),
	(N'��������',		N'��'),
	(N'���������',		N'%')
GO

INSERT INTO #Sidorenko.Weather.measurements
	(station_id, mea_type, mea_val, mea_date) VALUES
	(1, N'�����������', 30, '20020613'),
	(2, N'��������', 740, '20020613'),
	(2,	N'���������', 14, '20020613'),
	(3,	N'�����������', 25, '20020827'),
	(3,	N'��������', 738, '20020827'),
	(2,	N'���������', 17, '20020827'),
	(1,	N'�����������', 32, '20020613'),
	(2,	N'�����������', 25, '20020613'),
	(2,	N'��������', 30, '20020613'),
	(1,	N'���������', 20, '20020613')


SELECT �������, ���_���������, AVG(��������) as �������, ��_���, ���� FROM
	(SELECT	stations.station_name AS �������,
		measurements.mea_type AS ���_���������, 
		mea_val AS ��������,
		mea_ending AS ��_���,
		mea_date AS ����
		FROM (Weather.measurements INNER JOIN Weather.stations ON stations.station_id = measurements.station_id
		INNER JOIN Weather.measurement_types ON measurements.mea_type = measurement_types.mea_type)
	) AS result
	GROUP BY result.�������, result.���_���������, result.��_���, result.����
	ORDER BY result.�������
	/*
SELECT stations.station_name AS �������,
	measurements.mea_type AS ���_���������, 
	mea_val AS ��������,
	mea_ending AS ��_���,
	mea_date AS ����
	FROM (Weather.measurements INNER JOIN Weather.stations ON stations.station_id = measurements.station_id
	INNER JOIN Weather.measurement_types ON measurements.mea_type = measurement_types.mea_type)*/