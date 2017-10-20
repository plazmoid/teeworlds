USE master
/*��������� � ��������� ���� SQL �������
��� �������� ���������������� ���� ������*/
GO --����������� ������ (BATH)

IF  EXISTS (
	SELECT name 
		FROM sys.databases 
		WHERE name = N'��� ����'
)
ALTER DATABASE [��� ����] set single_user with rollback immediate
GO
/* ���������, ���������� �� �� ������� ���� ������
� ������ [��� ����], ���� ��, �� ��������� ��� �������
 ���������� � ���� ����� */

IF  EXISTS (
	SELECT name 
		FROM sys.databases 
		WHERE name = N'��� ����'
)
DROP DATABASE [��� ����]
GO
/* ����� ���������, ���������� �� �� ������� ���� ������
� ������ [��� ����], ���� ��, ������� �� � ������� */

/* ������ ���� ��������� ��� ����������� ������������ ����
������ � ������ [��� ����] ��� ������������� */

CREATE DATABASE [��� ����]
GO
-- ������� ���� ������

USE [��� ����]
GO
/* ��������� � ��������� ���� ������ ��� ����������� ������ � ��� 
��� � ���� ������ ���������� ������ � ����� ������ ���� ���
 ��� ���������� �� ������� */

IF EXISTS(
  SELECT *
    FROM sys.schemas
   WHERE name = N'�������'
) 
 DROP SCHEMA �������
GO
/*���������, ���������� �� � ���� ������
 [��� ����] ����� � ������ �������, ���� ��,
  �� �������������� ������� �� �� ����
  ���� �� ������� ��� ���� ������� - ��� ����� ������� �� ����� */

CREATE SCHEMA ������� 
GO
/*������� � ���� ������
 [��� ����] ����� � ������ ������� */

IF OBJECT_ID('[��� ����].�������.ut_students', 'U') IS NOT NULL
  DROP TABLE  [��� ����].�������.ut_students
GO

/*���������, ���������� �� � ���� ������
 [��� ����] � ����� � ������ ������� ������� ut_students ���� ��, 
  �� �������������� ������� �� �� ���� � �����.
  ���� �� ������� ��� ���� ������� - ��� ����� ������� �� ����� */

CREATE TABLE [��� ����].�������.ut_students
(
	NumberZach nvarchar(12) NOT NULL, 
	Family nvarchar(40) NULL, 
	Name nvarchar(40) NULL, 
    CONSTRAINT PK_NumberZach PRIMARY KEY (NumberZach) 
)
GO
/*������� � ���� ������ [��� ����] � ����� � ������
 ������� ������� ut_students � ����� ���������� ������ 
 � ��������� ������ (PRIMARY KEY),
 ��� PK_NumberZach - ��� �����, � NumberZach - ��� ��������� ����*/

ALTER TABLE [��� ����].�������.ut_students ADD 
	NumberGroup tinyint null,
	Kurs char(1) null
	GO

ALTER TABLE [��� ����].�������.ut_students ADD 
	Birthday date null
GO

ALTER TABLE [��� ����].�������.ut_students 
ALTER COLUMN Birthday date  NOT NULL
GO

/*������������ ������� ���� ������ ����� �������� � �������
���������� ALTER (��� �������) */


--DROP TABLE	[��� ����].�������.ut_students
--GO

/*�������� ������� ������� �� ���� ������  */

CREATE TABLE [��� ����].�������.ut_nameGroup
(
	NumberGroup tinyint IDENTITY(1,1) NOT NULL, 
	NameGroup nvarchar(40) NULL, 
	Kurs tinyint DEFAULT (3) NOT NULL, 
    CONSTRAINT PK_NumberGroup PRIMARY KEY (NumberGroup)
)
GO
/*������� � ���� ������ [��� ����] � ����� � ������
 ������� ������� ut_nameGroup �  ��������� ����� � ����� ��������������
 ������. ���� ���� ������ ���������������, � ������ ���� ������ �������� 
 �� ���������. ������� ��������� ���� (PRIMARY KEY),
 ��� PK_NumberGroup - ��� �����, � NumberGroup - ��� ��������� ����*/

ALTER TABLE [��� ����].�������.ut_students ADD 
	CONSTRAINT FK_NameGroup FOREIGN KEY (NumberGroup) 
	REFERENCES [��� ����].�������.ut_nameGroup(NumberGroup)
GO		
 /*������� � ������� ut_students ������� ����  (FOREIGN KEY)
  � ������ FK_NameGroup, ����������� ���� NumberGroup ������� ut_students
  � ����� NumberGroup ������� ut_nameGroup. ����� ������-�-������.
 ������� ���� ������� � ������� ���������� ALTER TABLE,
 ��������� �������� ����������� �������� ������*/

 ALTER TABLE [��� ����].�������.ut_nameGroup ADD 
	CONSTRAINT CK_Kurs 
	CHECK (Kurs>0 and Kurs<=6)
GO	
/*������������� ����������� (CHECK) � ������� ut_nameGroup �� ���� Kurs.
 CK_Kurs - ��� �����������*/

 INSERT INTO [��� ����].�������.ut_nameGroup 
 (NameGroup)
 VALUES 
  (N'��-301')
 ,(N'��-303')
 ,(N'��-301')	
GO	
/*������ ������ � ������� ut_nameGroup ������ � ���� ���� 
��� ������ ���� ����������� �������������*/

SELECT * From [��� ����].�������.ut_nameGroup 
--������������� ���������� ������� ut_nameGroup


INSERT INTO [��� ����].�������.ut_students 
  VALUES 
 ('095811',N'�������',N'����',2,3,'19950924')
 , ('095812',N'������',N'������',1,3,'19960924')

 /*������ ������ � ������� ut_students, 
 ��������� ����������� ��� ����, �������� ������ ������
 � ������� ���������� ����� � �������.
 �������� �������� �� ���� ����!!! */

SELECT * From [��� ����].�������.ut_students
--������������� ���������� ������� ut_students

DELETE FROM [��� ����].�������.ut_students 
/*������� ��� ������ �� �������  ut_students. 
���� ������� �������� � ���� ������*/

	
UPDATE [��� ����].�������.ut_nameGroup
SET Kurs = 7
/*��������� ������ ����������� (CHECK )
CK_Kurs � ������� ut_nameGroup*/

--DELETE From [��� ����].�������.ut_nameGroup
--GO
/*������� ��� ������ �� �������  ut_nameGroup
���� ������� �������� � ���� ������*/

 INSERT INTO [��� ����].�������.ut_nameGroup 
 (NameGroup)
 VALUES 
  (N'��-301')
 ,(N'��-303')
 ,(N'��-301')	
GO	
SELECT * From [��� ����].�������.ut_nameGroup 
--������������� ���������� ������� ut_nameGroup

--UPDATE [��� ����].�������.ut_nameGroup
--SET NumberGroup = 1

--UPDATE [��� ����].�������.ut_nameGroup
--SET NameGroup = 'kb1'

--DBCC CHECKIDENT ('[��� ����].�������.ut_nameGroup', RESEED , 0)
INSERT INTO [��� ����].�������.ut_nameGroup 
 (NameGroup)
 VALUES 
  (N'��-301')
 ,(N'��-303')
 ,(N'��-301')	
GO	
SELECT * From [��� ����].�������.ut_nameGroup 
--������������� ���������� ������� ut_nameGroup
