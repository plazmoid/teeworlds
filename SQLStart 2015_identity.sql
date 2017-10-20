USE master
/*ÎÁĞÀÙÅÍÈÅ Ê ÑÈÑÒÅÌÍÎÉ ÁÀÇÅ SQL ÑÅĞÂÅĞÀ
ÄËß ÑÎÇÄÀÍÈß ÏÎËÜÇÎÂÀÒÅËÜÑÊÎÉ ÁÀÇÛ ÄÀÍÍÛÕ*/
GO --ĞÀÇÄÅËÈÒÅËÜ ÁÀÒ×ÅÉ (BATH)

IF  EXISTS (
	SELECT name 
		FROM sys.databases 
		WHERE name = N'ÈÌß ÁÀÇÛ'
)
ALTER DATABASE [ÈÌß ÁÀÇÛ] set single_user with rollback immediate
GO
/* ÏĞÎÂÅĞßÅÌ, ÑÓÙÅÑÒÂÓÅÒ ËÈ ÍÀ ÑÅĞÂÅĞÅ ÁÀÇÀ ÄÀÍÍÛÕ
Ñ ÈÌÅÍÅÌ [ÈÌß ÁÀÇÛ], ÅÑËÈ ÄÀ, ÒÎ ÇÀÊĞÛÂÀÅÌ ÂÑÅ ÒÅÊÓÙÈÅ
 ÑÎÅÄÈÍÅÍÈß Ñ İÒÎÉ ÁÀÇÎÉ */

IF  EXISTS (
	SELECT name 
		FROM sys.databases 
		WHERE name = N'ÈÌß ÁÀÇÛ'
)
DROP DATABASE [ÈÌß ÁÀÇÛ]
GO
/* ÑÍÎÂÀ ÏĞÎÂÅĞßÅÌ, ÑÓÙÅÑÒÂÓÅÒ ËÈ ÍÀ ÑÅĞÂÅĞÅ ÁÀÇÀ ÄÀÍÍÛÕ
Ñ ÈÌÅÍÅÌ [ÈÌß ÁÀÇÛ], ÅÑËÈ ÄÀ, ÓÄÀËßÅÌ ÅÅ Ñ ÑÅĞÂÅĞÀ */

/* ÄÀÍÍÛÉ ÁËÎÊ ÍÅÎÁÕÎÄÈÌ ÄËß ÊÎĞĞÅÊÒÍÎÃÎ ÏÅĞÅÑÎÇÄÀÍÈß ÁÀÇÛ
ÄÀÍÍÛÕ Ñ ÈÌÅÍÅÌ [ÈÌß ÁÀÇÛ] ÏĞÈ ÍÅÎÁÕÎÄÈÌÎÑÒÈ */

CREATE DATABASE [ÈÌß ÁÀÇÛ]
GO
-- ÑÎÇÄÀÅÌ ÁÀÇÓ ÄÀÍÍÛÕ

USE [ÈÌß ÁÀÇÛ]
GO
/* ÏÅĞÅÕÎÄÈÌ Ê ÑÎÇÄÀÍÍÎÉ ÁÀÇÅ ÄÀÍÍÛÕ ÄËß ÏÎÑËÅÄÓŞÙÅÉ ĞÀÁÎÒÛ Ñ ÍÅÉ 
ÈËÈ Ñ İÒÈÕ ÊÎÌÀÍÄ ÏĞÎÄÎËÆÀÅÌ ĞÀÁÎÒÓ Ñ ÁÀÇÎÉ ÄÀÍÍÛÕ ÅÑËÈ ÎÍÀ
 ÓÆÅ ÑÓÙÅÑÒÂÓÅÒ ÍÀ ÑÅĞÂÅĞÅ */

IF EXISTS(
  SELECT *
    FROM sys.schemas
   WHERE name = N'Ôàìèëèÿ'
) 
 DROP SCHEMA Ôàìèëèÿ
GO
/*ÏĞÎÂÅĞßÅÌ, ÑÓÙÅÑÒÂÓÅÒ ËÈ Â ÁÀÇÅ ÄÀÍÍÛÕ
 [ÈÌß ÁÀÇÛ] ÑÕÅÌÀ Ñ ÈÌÅÍÅÌ Ôàìèëèÿ, ÅÑËÈ ÄÀ,
  ÒÎ ÏĞÅÄÂÀĞÈÒÅËÜÍÎ ÓÄÀËßÅÌ ÅÅ ÈÇ ÁÀÇÛ
  ÅÑËÈ ÂÛ ÓÀËßÅÒÅ ÂÑŞ ÁÀÇÓ ÖÅËÈÊÎÌ - İÒÀ ×ÀÑÒÜ ÑÊĞÈÏÒÀ ÍÅ ÍÓÆÍÀ */

CREATE SCHEMA Ôàìèëèÿ 
GO
/*ÑÎÇÄÀÅÌ Â ÁÀÇÅ ÄÀÍÍÛÕ
 [ÈÌß ÁÀÇÛ] ÑÕÅÌÓ Ñ ÈÌÅÍÅÌ Ôàìèëèÿ */

IF OBJECT_ID('[ÈÌß ÁÀÇÛ].Ôàìèëèÿ.ut_students', 'U') IS NOT NULL
  DROP TABLE  [ÈÌß ÁÀÇÛ].Ôàìèëèÿ.ut_students
GO

/*ÏĞÎÂÅĞßÅÌ, ÑÓÙÅÑÒÂÓÅÒ ËÈ Â ÁÀÇÅ ÄÀÍÍÛÕ
 [ÈÌß ÁÀÇÛ] È ÑÕÅÌÅ Ñ ÈÌÅÍÅÌ Ôàìèëèÿ ÒÀÁËÈÖÀ ut_students ÅÑËÈ ÄÀ, 
  ÒÎ ÏĞÅÄÂÀĞÈÒÅËÜÍÎ ÓÄÀËßÅÌ ÅÅ ÈÇ ÁÀÇÛ È ÑÕÅÌÛ.
  ÅÑËÈ ÂÛ ÓÀËßÅÒÅ ÂÑŞ ÁÀÇÓ ÖÅËÈÊÎÌ - İÒÀ ×ÀÑÒÜ ÑÊĞÈÏÒÀ ÍÅ ÍÓÆÍÀ */

CREATE TABLE [ÈÌß ÁÀÇÛ].Ôàìèëèÿ.ut_students
(
	NumberZach nvarchar(12) NOT NULL, 
	Family nvarchar(40) NULL, 
	Name nvarchar(40) NULL, 
    CONSTRAINT PK_NumberZach PRIMARY KEY (NumberZach) 
)
GO
/*ÑÎÇÄÀÅÌ Â ÁÀÇÅ ÄÀÍÍÛÕ [ÈÌß ÁÀÇÛ] Â ÑÕÅÌÅ Ñ ÈÌÅÍÅÌ
 Ôàìèëèÿ ÒÀÁËÈÖÓ ut_students Ñ ÒĞÅÌß ÒÅÊÑÒÎÂÛÌÈ ÏÎËßÌÈ 
 È ÏÅĞÂÈ×ÍÛÌ ÊËŞ×ÎÌ (PRIMARY KEY),
 ÃÄÅ PK_NumberZach - ÈÌß ÊËŞ×À, À NumberZach - ÈÌß ÊËŞ×ÅÂÎÃÎ ÏÎËß*/

ALTER TABLE [ÈÌß ÁÀÇÛ].Ôàìèëèÿ.ut_students ADD 
	NumberGroup tinyint null,
	Kurs char(1) null
	GO

ALTER TABLE [ÈÌß ÁÀÇÛ].Ôàìèëèÿ.ut_students ADD 
	Birthday date null
GO

ALTER TABLE [ÈÌß ÁÀÇÛ].Ôàìèëèÿ.ut_students 
ALTER COLUMN Birthday date  NOT NULL
GO

/*ÑÓÙÅÑÒÂÓŞÙÈÅ ÎÁÚÅÊÒÛ ÁÀÇÛ ÄÀÍÍÛÕ ÌÎÆÍÎ ÈÇÌÅÍßÒÜ Ñ ÏÎÌÎÙÜŞ
ÈÍÑÒĞÓÊÖÈÈ ALTER (ÈÌß ÎÁÚÅÊÒÀ) */


--DROP TABLE	[ÈÌß ÁÀÇÛ].Ôàìèëèÿ.ut_students
--GO

/*ÓÄÀËÅÍÈÅ ÎÁÚÅÊÒÀ ÒÀÁËÈÖÛ ÈÇ ÁÀÇÛ ÄÀÍÍÛÕ  */

CREATE TABLE [ÈÌß ÁÀÇÛ].Ôàìèëèÿ.ut_nameGroup
(
	NumberGroup tinyint IDENTITY(1,1) NOT NULL, 
	NameGroup nvarchar(40) NULL, 
	Kurs tinyint DEFAULT (3) NOT NULL, 
    CONSTRAINT PK_NumberGroup PRIMARY KEY (NumberGroup)
)
GO
/*ÑÎÇÄÀÅÌ Â ÁÀÇÅ ÄÀÍÍÛÕ [ÈÌß ÁÀÇÛ] Â ÑÕÅÌÅ Ñ ÈÌÅÍÅÌ
 Ôàìèëèÿ ÒÀÁËÈÖÓ ut_nameGroup Ñ  ÒÅÊÑÒÎÂÛÌ ÏÎËßÌ È ÄÂÓÌß ÖÅËÎ×ÈÑËÅÍÍÛÌÈ
 ÏÎËßÌÈ. ÎÄÍÎ ÏÎËÅ ÄÅËÀÅÌ ÈÄÅÍÒÈÔÈÊÀÒÎĞÎÌ, Â ÄĞÓÃÎÅ ÏÎËÅ ÂÍÎÑÈÌ ÇÍÀ×ÅÍÈÅ 
 ÏÎ ÓÌÎË×ÅÍÈŞ. ÑÎÇÄÀÅÌ ÏÅĞÂÈ×ÍÛÉ ÊËŞ× (PRIMARY KEY),
 ÃÄÅ PK_NumberGroup - ÈÌß ÊËŞ×À, À NumberGroup - ÈÌß ÊËŞ×ÅÂÎÃÎ ÏÎËß*/

ALTER TABLE [ÈÌß ÁÀÇÛ].Ôàìèëèÿ.ut_students ADD 
	CONSTRAINT FK_NameGroup FOREIGN KEY (NumberGroup) 
	REFERENCES [ÈÌß ÁÀÇÛ].Ôàìèëèÿ.ut_nameGroup(NumberGroup)
GO		
 /*ÑÎÇÄÀÅÌ Â ÒÀÁËÈÖÅ ut_students ÂÍÅØÍÈÉ ÊËŞ×  (FOREIGN KEY)
  Ñ ÈÌÅÍÅÌ FK_NameGroup, ÑÂßÇÛÂÀŞÙÈÉ ÏÎËÅ NumberGroup ÒÀÁËÈÖÛ ut_students
  Ñ ÏÎËÅÌ NumberGroup ÒÀÁËÈÖÛ ut_nameGroup. ÑÂßÇÜ ÌÍÎÃÈÅ-Ê-ÎÄÍÎÌÓ.
 ÂÍÅØÍÈÉ ÊËŞ× ÑÎÇÄÀÅÌ Ñ ÏÎÌÎÙÜŞ ÈÍÑÒĞÓÊÖÈÈ ALTER TABLE,
 ÏÎÑÊÎËÜÊÓ ÍÀĞÓØÅÍÀ Î×ÅĞÅÄÍÎÑÒÜ ÑÎÇÄÀÍÈß ÒÀÁËÈÖ*/

 ALTER TABLE [ÈÌß ÁÀÇÛ].Ôàìèëèÿ.ut_nameGroup ADD 
	CONSTRAINT CK_Kurs 
	CHECK (Kurs>0 and Kurs<=6)
GO	
/*ÓÑÒÀÍÀÂËÈÂÀÅÌ ÎÃĞÀÍÈ×ÅÍÈÅ (CHECK) Â ÒÀÁËÈÖÅ ut_nameGroup ÍÀ ÏÎËÅ Kurs.
 CK_Kurs - ÈÌß ÎÃĞÀÍÈ×ÅÍÈß*/

 INSERT INTO [ÈÌß ÁÀÇÛ].Ôàìèëèÿ.ut_nameGroup 
 (NameGroup)
 VALUES 
  (N'ÊÍ-301')
 ,(N'ÊÍ-303')
 ,(N'ÊÁ-301')	
GO	
/*ÂÍÎÑÈÌ ÄÀÍÍÛÅ Â ÒÀÁËÈÖÓ ut_nameGroup ÒÎËÜÊÎ Â ÎÄÍÎ ÏÎËÅ 
ÄÂÀ ÄĞÓÃÈÕ ÏÎËß ÇÀÏÎËÍßŞÒÑß ÀÂÒÎÌÀÒÈ×ÅÑÊÈ*/

SELECT * From [ÈÌß ÁÀÇÛ].Ôàìèëèÿ.ut_nameGroup 
--ÏĞÎÑÌÀÒĞÈÂÀÅÌ ÑÎÄÅĞÆÈÌÎÅ ÒÀÁËÈÖÛ ut_nameGroup


INSERT INTO [ÈÌß ÁÀÇÛ].Ôàìèëèÿ.ut_students 
  VALUES 
 ('095811',N'Ñåğãååâ',N'Ïåòğ',2,3,'19950924')
 , ('095812',N'Ïåòğîâ',N'Ñåğãåé',1,3,'19960924')

 /*ÂÍÎÑÈÌ ÄÀÍÍÛÅ Â ÒÀÁËÈÖÓ ut_students, 
 ÏÎÑÊÎËÜÊÓ ÇÀÏÎËÍßŞÒÑß ÂÑÅ ÏÎËß, ÏÈØÓÒÜÑß ÒÎËÜÊÎ ÄÀÍÍÛÅ
 Â ÏÎĞßÄÊÅ ÑËÅÄÎÂÀÍÈß ÏÎËÅÉ Â ÒÀÁËÈÖÅ.
 ÎÁĞÀÒÈÒÅ ÂÍÈÌÀÍÈÅ ÍÀ ÂÂÎÄ ÄÀÒÛ!!! */

SELECT * From [ÈÌß ÁÀÇÛ].Ôàìèëèÿ.ut_students
--ÏĞÎÑÌÀÒĞÈÂÀÅÌ ÑÎÄÅĞÆÈÌÎÅ ÒÀÁËÈÖÛ ut_students

DELETE FROM [ÈÌß ÁÀÇÛ].Ôàìèëèÿ.ut_students 
/*ÓÄÀËßÅÌ ÂÑÅ ÄÀÍÍÛÅ ÈÇ ÒÀÁËÈÖÛ  ut_students. 
ÑÀÌÀ ÒÀÁËÈÖÀ ÎÑÒÀÅÒÑß Â ÁÀÇÅ ÄÀÍÍÛÕ*/

	
UPDATE [ÈÌß ÁÀÇÛ].Ôàìèëèÿ.ut_nameGroup
SET Kurs = 7
/*ÏĞÎÂÅĞßÅÌ ĞÀÁÎÒÓ ÎÃĞÀÍÈ×ÅÍÈß (CHECK )
CK_Kurs Â ÒÀÁËÈÖÅ ut_nameGroup*/

--DELETE From [ÈÌß ÁÀÇÛ].Ôàìèëèÿ.ut_nameGroup
--GO
/*ÓÄÀËßÅÌ ÂÑÅ ÄÀÍÍÛÅ ÈÇ ÒÀÁËÈÖÛ  ut_nameGroup
ÑÀÌÀ ÒÀÁËÈÖÀ ÎÑÒÀÅÒÑß Â ÁÀÇÅ ÄÀÍÍÛÕ*/

 INSERT INTO [ÈÌß ÁÀÇÛ].Ôàìèëèÿ.ut_nameGroup 
 (NameGroup)
 VALUES 
  (N'ÊÍ-301')
 ,(N'ÊÍ-303')
 ,(N'ÊÁ-301')	
GO	
SELECT * From [ÈÌß ÁÀÇÛ].Ôàìèëèÿ.ut_nameGroup 
--ÏĞÎÑÌÀÒĞÈÂÀÅÌ ÑÎÄÅĞÆÈÌÎÅ ÒÀÁËÈÖÛ ut_nameGroup

--UPDATE [ÈÌß ÁÀÇÛ].Ôàìèëèÿ.ut_nameGroup
--SET NumberGroup = 1

--UPDATE [ÈÌß ÁÀÇÛ].Ôàìèëèÿ.ut_nameGroup
--SET NameGroup = 'kb1'

--DBCC CHECKIDENT ('[ÈÌß ÁÀÇÛ].Ôàìèëèÿ.ut_nameGroup', RESEED , 0)
INSERT INTO [ÈÌß ÁÀÇÛ].Ôàìèëèÿ.ut_nameGroup 
 (NameGroup)
 VALUES 
  (N'ÊÍ-301')
 ,(N'ÊÍ-303')
 ,(N'ÊÁ-301')	
GO	
SELECT * From [ÈÌß ÁÀÇÛ].Ôàìèëèÿ.ut_nameGroup 
--ÏĞÎÑÌÀÒĞÈÂÀÅÌ ÑÎÄÅĞÆÈÌÎÅ ÒÀÁËÈÖÛ ut_nameGroup
