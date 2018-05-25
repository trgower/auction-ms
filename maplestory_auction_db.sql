BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS `hot_auctions` (
	`id`	INTEGER NOT NULL,
	`auction_id`	INTEGER,
	PRIMARY KEY(`id`)
);
CREATE TABLE IF NOT EXISTS `messages` (
	`id`	INTEGER NOT NULL,
	`sender_id`	INTEGER,
	`message`	TEXT,
	`sent`	DATETIME,
	`recp_id`	INTEGER,
	PRIMARY KEY(`id`)
);
CREATE TABLE IF NOT EXISTS `conversations` (
	`id`	INTEGER NOT NULL,
	`user_id`	INTEGER,
	`conversant`	INTEGER,
	`created`	DATETIME,
	`last_msg`	DATETIME,
	`last_read`	DATETIME,
	PRIMARY KEY(`id`)
);
CREATE TABLE IF NOT EXISTS `alerts` (
	`id`	INTEGER NOT NULL,
	`user_id`	INTEGER,
	`category`	VARCHAR,
	`message`	VARCHAR,
	PRIMARY KEY(`id`)
);
CREATE TABLE IF NOT EXISTS `watchlists` (
	`id`	INTEGER NOT NULL,
	`watcher_id`	INTEGER,
	`auction_id`	INTEGER,
	`posted`	DATETIME,
	PRIMARY KEY(`id`)
);
CREATE TABLE IF NOT EXISTS `feedback` (
	`id`	INTEGER NOT NULL,
	`reviewer`	INTEGER,
	`reviewee`	INTEGER,
	`auction_id`	INTEGER,
	`score`	INTEGER,
	`message`	TEXT,
	`posted`	DATETIME,
	PRIMARY KEY(`id`)
);
CREATE TABLE IF NOT EXISTS `comments` (
	`id`	INTEGER NOT NULL,
	`commenter_id`	INTEGER,
	`auction_id`	INTEGER,
	`message`	TEXT,
	`posted`	DATETIME,
	PRIMARY KEY(`id`)
);
CREATE TABLE IF NOT EXISTS `bids` (
	`id`	INTEGER NOT NULL,
	`bidder_id`	INTEGER,
	`auction_id`	INTEGER,
	`amount`	INTEGER,
	`posted`	DATETIME,
	PRIMARY KEY(`id`)
);
CREATE TABLE IF NOT EXISTS `auctions` (
	`id`	INTEGER NOT NULL,
	`seller_id`	INTEGER,
	`item_id`	INTEGER,
	`starting_bid`	INTEGER,
	`bid`	INTEGER,
	`min_bid_inc`	INTEGER,
	`reserve`	INTEGER,
	`fm_channel`	INTEGER,
	`fm_door`	INTEGER,
	`length`	INTEGER,
	`posted`	DATETIME,
	`end`	DATETIME,
	`transaction_step`	INTEGER,
	`buyer_id`	INTEGER,
	`item_quality`	INTEGER,
	`sc_offered`	INTEGER,
	`watk`	INTEGER,
	`matk`	INTEGER,
	`int`	INTEGER,
	`str`	INTEGER,
	`luk`	INTEGER,
	`dex`	INTEGER,
	`eva`	INTEGER,
	`acc`	INTEGER,
	`wdef`	INTEGER,
	`mdef`	INTEGER,
	`hp`	INTEGER,
	`mp`	INTEGER,
	`speed`	INTEGER,
	`jump`	INTEGER,
	`slots`	INTEGER,
	`upgrades`	INTEGER,
	PRIMARY KEY(`id`)
);
CREATE TABLE IF NOT EXISTS `user` (
	`id`	INTEGER NOT NULL,
	`username`	VARCHAR ( 50 ) NOT NULL,
	`password`	VARCHAR ( 255 ) NOT NULL,
	`email`	VARCHAR ( 255 ) NOT NULL,
	`confirmed_at`	DATETIME,
	`is_active`	BOOLEAN NOT NULL,
	CHECK(is_activeIN(0,1)),
	PRIMARY KEY(`id`)
);
CREATE TABLE IF NOT EXISTS `projectiles` (
	`id`	INTEGER NOT NULL,
	`reqLevel`	INTEGER,
	`watk`	INTEGER,
	`slotMax`	INTEGER,
	`unitPrice`	FLOAT,
	`price`	INTEGER,
	PRIMARY KEY(`id`)
);
CREATE TABLE IF NOT EXISTS `scroll` (
	`id`	INTEGER NOT NULL,
	`success`	INTEGER,
	`cursed`	INTEGER,
	`watk`	INTEGER,
	`matk`	INTEGER,
	`int`	INTEGER,
	`str`	INTEGER,
	`luk`	INTEGER,
	`dex`	INTEGER,
	`eva`	INTEGER,
	`acc`	INTEGER,
	`wdef`	INTEGER,
	`mdef`	INTEGER,
	`hp`	INTEGER,
	`mp`	INTEGER,
	`speed`	INTEGER,
	`jump`	INTEGER,
	PRIMARY KEY(`id`)
);
CREATE TABLE IF NOT EXISTS `equipment` (
	`id`	INTEGER NOT NULL,
	`slot`	VARCHAR ( 16 ),
	`reqlevel`	INTEGER,
	`reqjob`	INTEGER,
	`reqstr`	INTEGER,
	`reqint`	INTEGER,
	`reqdex`	INTEGER,
	`reqluk`	INTEGER,
	`watk`	INTEGER,
	`matk`	INTEGER,
	`int`	INTEGER,
	`str`	INTEGER,
	`luk`	INTEGER,
	`dex`	INTEGER,
	`eva`	INTEGER,
	`acc`	INTEGER,
	`atkspeed`	INTEGER,
	`wdef`	INTEGER,
	`mdef`	INTEGER,
	`hp`	INTEGER,
	`mp`	INTEGER,
	`speed`	INTEGER,
	`jump`	INTEGER,
	`price`	INTEGER,
	`tuc`	INTEGER,
	PRIMARY KEY(`id`)
);
CREATE TABLE IF NOT EXISTS `strings` (
	`id`	INTEGER NOT NULL,
	`name`	VARCHAR ( 64 ),
	`desc`	TEXT,
	`type`	INTEGER,
	PRIMARY KEY(`id`)
);
CREATE TABLE IF NOT EXISTS `potions` (
	`id`	INTEGER NOT NULL,
	`time`	INTEGER,
	`watk`	INTEGER,
	`matk`	INTEGER,
	`eva`	INTEGER,
	`acc`	INTEGER,
	`wdef`	INTEGER,
	`mdef`	INTEGER,
	`hp`	INTEGER,
	`mp`	INTEGER,
	`speed`	INTEGER,
	`jump`	INTEGER,
	`price`	INTEGER,
	`curse`	INTEGER,
	`darkness`	INTEGER,
	`hpR`	INTEGER,
	`mpR`	INTEGER,
	`poison`	INTEGER,
	`seal`	INTEGER,
	`weakness`	INTEGER,
	PRIMARY KEY(`id`)
);
CREATE TABLE IF NOT EXISTS `migrate_version` (
	`repository_id`	VARCHAR ( 250 ) NOT NULL,
	`repository_path`	TEXT,
	`version`	INTEGER,
	PRIMARY KEY(`repository_id`)
);
COMMIT;
