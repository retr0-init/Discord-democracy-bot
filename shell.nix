{ pkgs ? import <nixpkgs> {} }:
  pkgs.mkShell {
    # nativeBuildInputs is usually what you want -- tools you need to run
    nativeBuildInputs = with pkgs.buildPackages; [
    	python311
	python311Packages.discordpy
#	python311Packages.psycopg2
	python311Packages.numpy
#	postgresql
#	python311Packages.aiomysql
#	python311Packages.pymysql
#	python311Packages.mysql-connector
	python311Packages.sqlalchemy
	python311Packages.aiosqlite
#	mysql
	python311Packages.feedparser
    ];
}
