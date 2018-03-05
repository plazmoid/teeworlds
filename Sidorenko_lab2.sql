USE master
GO

IF EXISTS (SELECT name FROM sys.databases WHERE name = N'Sidorenko') BEGIN
	ALTER DATABASE Sidorenko SET SINGLE_USER WITH ROLLBACK IMMEDIATE
	DROP DATABASE Sidorenko
END
GO

CREATE DATABASE Sidorenko
GO

USE Sidorenko
GO

CREATE SCHEMA CarsList
GO

CREATE TABLE Sidorenko.CarsList.regions (
	region_id INT NOT NULL,
	region_name NVARCHAR(50) NOT NULL
	CONSTRAINT REG_PK_ID PRIMARY KEY (region_id)
)
GO

CREATE TABLE Sidorenko.CarsList.cartype (
	ctype_id SMALLINT IDENTITY(0,1),
	ctype_name NVARCHAR(30) NOT NULL,
	CONSTRAINT CTYP_PK_ID PRIMARY KEY (ctype_id)
)
GO

CREATE TABLE Sidorenko.CarsList.posts (
	post_id INT IDENTITY(0,1),
	post_name NVARCHAR(30) NOT NULL,
	CONSTRAINT PST_PK_ID PRIMARY KEY (post_id)
)
GO

CREATE TABLE Sidorenko.CarsList.cars (
	car_number NVARCHAR(9),
	car_region INT NOT NULL,
	car_dir_current BIT DEFAULT 0, -- 0 - ������, 1 - ������
	car_last_post INT NOT NULL,
	car_type SMALLINT DEFAULT 0,
	CONSTRAINT CRS_PK_NUM PRIMARY KEY (car_number),
	CONSTRAINT CRS_FK_REG FOREIGN KEY (car_region) REFERENCES CarsList.regions(region_id),
	CONSTRAINT CRS_FK_POST FOREIGN KEY (car_last_post) REFERENCES CarsList.posts(post_id),
	CONSTRAINT CRS_FK_TYP FOREIGN KEY (car_type) REFERENCES CarsList.cartype(ctype_id)
)
GO

CREATE TABLE Sidorenko.CarsList.mainlist (
	car_full_number NVARCHAR(9),
	post INT NOT NULL,
	car_dir BIT NOT NULL, -- 0 - ������, 1 - ������
	check_time DATETIME DEFAULT GETDATE(),
	CONSTRAINT ML_FK_NUM FOREIGN KEY (car_full_number) REFERENCES CarsList.cars(car_number),
	CONSTRAINT ML_FK_POST FOREIGN KEY (post) REFERENCES CarsList.posts(post_id),
	CONSTRAINT ML_CHK_NUMFORMAT CHECK (mainlist.car_full_number LIKE '[������������ABEKMHOPCTYX][0-9][0-9][0-9][������������ABEKMHOPCTYX][������������ABEKMHOPCTYX][0-9][0-9]'
	OR mainlist.car_full_number LIKE '[������������ABEKMHOPCTYX][0-9][0-9][0-9][������������ABEKMHOPCTYX][������������ABEKMHOPCTYX][127][0-9][0-9]')
)
GO

CREATE FUNCTION CarsList.getRegion(@num NVARCHAR(10))
RETURNS INT AS BEGIN
	SET @num = SUBSTRING(@num, 7, LEN(@num)-6)
	RETURN (SELECT CAST(@num AS INT));;
END
GO

CREATE FUNCTION CarsList.getCarType(@old_dir BIT, @new_dir BIT, @old_post INT, @new_post INT, @auto_region INT)
RETURNS SMALLINT AS BEGIN
	DECLARE @current_region INT = 66;
	IF @new_dir < @old_dir BEGIN
		IF @auto_region = @current_region
			RETURN 1;
	END
	ELSE BEGIN
		IF @old_post = @new_post
			RETURN 3;
		ELSE
			IF @auto_region <> @current_region
				RETURN 2;
	END
	RETURN 0;
END;
GO

CREATE TRIGGER CarsList.distr_trigger ON Sidorenko.CarsList.mainlist
INSTEAD OF INSERT
AS
BEGIN
	DECLARE @number NVARCHAR(10);
	DECLARE @new_dir BIT, @curr_dir BIT;
	DECLARE @new_post INT, @curr_post INT, @i INT = 0;
	DECLARE dir_cursor CURSOR LOCAL FOR SELECT car_full_number, post, car_dir FROM INSERTED; -- ������ �� ����������� �������
	OPEN dir_cursor;
	WHILE @i < (SELECT COUNT(*) FROM INSERTED) BEGIN
		FETCH NEXT FROM dir_cursor INTO @number, @new_post, @new_dir;
		SET @curr_dir = (SELECT car_dir_current FROM Sidorenko.CarsList.cars WHERE car_number = @number)
		SET @curr_post = (SELECT car_last_post FROM Sidorenko.CarsList.cars WHERE car_number = @number)
		--PRINT(@number + ' ' + CAST(@i AS CHAR(2)));
		IF @curr_dir IS NOT NULL BEGIN -- ���� ����� ����� ��� ���� � ����
			IF @curr_dir <> @new_dir -- � ����������� �������� �������������� ����������
				UPDATE Sidorenko.CarsList.cars
				SET cars.car_dir_current = @new_dir,
					cars.car_type = CarsList.getCarType(@curr_dir, @new_dir, @curr_post, @new_post, CarsList.getRegion(@number))
				WHERE cars.car_number = @number; -- �� ��������� ���
			ELSE BEGIN
				PRINT(N'���������� �� ����� ��� ���� ������ ������� ��� ������� �� ������');
				--+ ' ' + CAST(@curr_dir AS CHAR(1)) + ' ' + CAST(@new_dir AS CHAR(1)));
				--PRINT(@number);
				ROLLBACK TRANSACTION;
				RETURN;
			END;
		END
		ELSE BEGIN -- ����� ��������� ����� � ����
			BEGIN TRY
				--PRINT('INS: ' + @number + ' ' + CAST(@i AS CHAR(2)))
				INSERT INTO Sidorenko.CarsList.cars (car_number, car_region, car_dir_current, car_last_post)
					VALUES(@number, CarsList.getRegion(@number), @new_dir, @new_post);
			END TRY
			BEGIN CATCH
				PRINT(N'�������� ��� ������ � ' + @number);
				ROLLBACK TRANSACTION;
				RETURN;
			END CATCH;
		END;
		INSERT INTO Sidorenko.CarsList.mainlist (car_full_number, post, car_dir) VALUES (@number, @new_post, @new_dir);
		SET @i += 1;
	END
	CLOSE dir_cursor;
	DEALLOCATE dir_cursor;
END
GO

INSERT INTO Sidorenko.CarsList.regions
	(region_id, region_name) VALUES
    (13, N'����. ��������'),
	(23, N'������������� ����'),       
    (50, N'���������� ���.'),
	(66, N'������������ ���.'),    
    (74, N'����������� ���.'),
	(77, N'������')   
GO

INSERT INTO Sidorenko.CarsList.cartype VALUES
	(N'������'),
	(N'�������'),
	(N'����������'),
	(N'�����������')
GO

INSERT INTO Sidorenko.CarsList.posts VALUES
	(N'������-18'),
	(N'�����-�'),
	(N'����-5'),
	(N'�101')
GO

INSERT INTO Sidorenko.CarsList.mainlist 
	(car_full_number, post, car_dir) VALUES -- 0 - ������, 1 - ������
	(N'�654��23', 0, 1),
	(N'B125YX66', 3, 1),
	(N'H731BT50', 1, 0),
	(N'�005��77', 1, 0),
	(N'�005��77', 2, 1),
	(N'H731BT50', 1, 1),
	(N'B125YX66', 3, 0)
GO

CREATE VIEW allRecordingsView AS 
	SELECT
		car_full_number AS �����,
		posts.post_name AS ����,
		CASE WHEN car_dir = 1 THEN N'��' WHEN car_dir = 0 THEN N'�' END AS �����������,
		check_time AS �����
		FROM (Sidorenko.CarsList.mainlist JOIN Sidorenko.CarsList.posts ON mainlist.post = posts.post_id)
GO

CREATE VIEW carsView AS
	SELECT
		car_number AS �����,
		car_region AS ������,
		CASE WHEN car_dir_current = 1 THEN N'��' WHEN car_dir_current = 0 THEN N'�' END AS �����������,
		posts.post_name AS ���������_����,
		cartype.ctype_name AS ���
		FROM (Sidorenko.CarsList.cars JOIN Sidorenko.CarsList.posts ON cars.car_last_post = posts.post_id
		JOIN Sidorenko.CarsList.cartype ON cars.car_type = cartype.ctype_id)
GO

SELECT * FROM allRecordingsView
SELECT * FROM carsView