/*
   Saturday, October 24, 20204:40:57 PM
   User: SA
   Server: 192.168.50.8
   Database: stevendb
   Application: 
*/

/* To prevent any potential data loss issues, you should review this script in detail before running it outside the context of the database designer.*/
CREATE TABLE [dbo].[reliant_energy]
	(
	[Date] datetime2(7) NOT NULL,
	[Usage (kWh)] float(53) NULL,
	[Cost ($)] float(53) NULL,
	[Hi] int NULL,
	[Low] int NULL
	)  ON [PRIMARY]
GO
