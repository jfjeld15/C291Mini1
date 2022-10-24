# I am too lazy to install sql on my desktop or use the lab machines, this creates a db
import sqlite3

conn = sqlite3.connect('testdata.db')
c = conn.cursor()
# PASTE SQL FILE BELOW:
c.executescript("""
-- CMPUT 291 - Fall 2022 (Davood Rafiei)

drop table if exists perform;
drop table if exists artists;
drop table if exists plinclude;
drop table if exists playlists;
drop table if exists listen;
drop table if exists sessions;
drop table if exists songs;
drop table if exists users;

PRAGMA foreign_keys = ON;

create table users (
  uid		char(4),
  name		text,
  pwd		text,
  primary key (uid)
);
create table songs (
  sid		int,
  title		text,
  duration	int,
  primary key (sid)
);
create table sessions (
  uid		char(4),
  sno		int,
  start 	date,
  end 		date,
  primary key (uid,sno),
  foreign key (uid) references users
	on delete cascade
);
create table listen (
  uid		char(4),
  sno		int,
  sid		int,
  cnt		real,
  primary key (uid,sno,sid),
  foreign key (uid,sno) references sessions,
  foreign key (sid) references songs
);
create table playlists (
  pid		int,
  title		text,
  uid		char(4),
  primary key (pid),
  foreign key (uid) references users
);
create table plinclude (
  pid		int,
  sid		int,
  sorder	int,
  primary key (pid,sid),
  foreign key (pid) references playlists,
  foreign key (sid) references songs
);
create table artists (
  aid		char(4),
  name		text,
  nationality	text,
  pwd		text,
  primary key (aid)
);
create table perform (
  aid		char(4),
  sid		int,
  primary key (aid,sid),
  foreign key (aid) references artists,
  foreign key (sid) references songs
);
INSERT INTO users VALUES ('u1', 'Jonathan Fjeld', 'secretPassword');
INSERT INTO users VALUES ('u2', 'Ying Wan', 'secretPassword2');
INSERT INTO users VALUES ('u3', 'Crystal Zhang', 'secretPassword3');

insert into songs values (1, 'Waka Waka(This Time For Africa)', 202);
insert into songs values (2, 'Applause', 212);
insert into songs values (3, 'Demons', 177);
insert into songs values (4, 'Counting Stars', 259);
insert into songs values (5, 'Wavin flag', 220);
insert into songs values (6, 'Just Give Me a Reason', 242);
insert into songs values (7, 'Stronger(What Doesn`t Kill You)', 222);
insert into songs values (8, 'We Are Young', 233);
insert into songs values (9, 'Moves Like Jagger', 201);
insert into songs values (10, 'GANGNAM STYLE', 210);

insert into sessions values ('u1', 1, '2022-09-27', '2022-09-28');
insert into sessions values ('u2', 1, '2022-09-25', '2022-09-27');
insert into sessions values ('u3', 1, '2022-09-24', '2022-09-25');
insert into sessions values ('u1', 2, '2022-10-24', '2022-10-25');
insert into sessions values ('u2', 2, '2022-10-23', '2022-10-27');
insert into sessions values ('u3', 2, '2022-10-22', '2022-10-24');

insert into listen values ('u1', 1, 1, 1.2);
insert into listen values ('u2', 1, 2, 2.0);
insert into listen values ('u3', 1, 3, 33);
insert into listen values ('u3', 1, 4, 20);
insert into listen values ('u3', 1, 7, 16);
insert into listen values ('u1', 2, 4, 14);
insert into listen values ('u2', 2, 5, 22);
insert into listen values ('u3', 2, 6, 21);

insert into playlists values (1, 'Fun Songs', 'u1');
insert into playlists values (2, 'Relaxing Music', 'u2');
insert into playlists values (3, 'Relaxing Music', 'u3');
insert into playlists values (4, '2010s', 'u1');

insert into plinclude values (1, 1, 1);
insert into plinclude values (1, 3, 3);
insert into plinclude values (1, 9, 2);
insert into plinclude values (2, 8, 1);
insert into plinclude values (2, 5, 2);
insert into plinclude values (2, 4, 3);
insert into plinclude values (3, 5, 1);
insert into plinclude values (3, 4, 2);
insert into plinclude values (3, 3, 3);
insert into plinclude values (4, 6, 1);
insert into plinclude values (4, 2, 2);
insert into plinclude values (4, 3, 3);

-- PASSWORDS HERE
insert into artists values ('a1', 'Lady Gaga', 'United States', 'pokerFACE1');
insert into artists values ('a2', 'OneRepublic', 'United States', 'star_counters');
insert into artists values ('u3', 'Imagine Dragons', 'United States', 'lmao');
insert into artists values ('a4', 'PSY', 'South Korea', 'oppaGangnamStyle');

insert into perform values ('a1', 1);
insert into perform values ('a1', 2);
insert into perform values ('a2', 4);
insert into perform values ('u3', 3);
insert into perform values ('a4', 10);
""")
conn.commit()