-- DDL

CREATE TABLE product (
	id		 BIGINT UNIQUE,
	version	 BIGINT UNIQUE,
	name		 VARCHAR(512) NOT NULL,
	price		 FLOAT(8) NOT NULL,
	stock		 INTEGER NOT NULL,
	description	 VARCHAR(512),
	seller_id BIGINT NOT NULL,
	PRIMARY KEY(id, version)
);

CREATE TABLE computer (
	cpu		 VARCHAR(512) NOT NULL,
	gpu		 VARCHAR(512),
	product_id	 BIGINT,
	product_version BIGINT,
	PRIMARY KEY(product_id, product_version)
);

CREATE TABLE "user" (
	id		 SERIAL,
	name	 VARCHAR(512) UNIQUE NOT NULL,
	first_name	 VARCHAR(512) NOT NULL,
	email	 VARCHAR(512) UNIQUE NOT NULL,
	tin		 VARCHAR(512),
	last_name	 VARCHAR(512) NOT NULL,
	phone_number	 VARCHAR(512) UNIQUE NOT NULL,
	password_hash VARCHAR(128) NOT NULL,
	house_no	 INTEGER NOT NULL,
	street_name	 VARCHAR(512) NOT NULL,
	city	 VARCHAR(512) NOT NULL,
	state	 VARCHAR(512) NOT NULL,
	zip_code	 VARCHAR(64) NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE television (
	size		 INTEGER NOT NULL,
	technology	 VARCHAR(512) NOT NULL,
	product_id	 BIGINT,
	product_version BIGINT,
	PRIMARY KEY(product_id, product_version)
);

CREATE TABLE smartphone (
	model		 VARCHAR(512) NOT NULL,
	operative_system VARCHAR(512) NOT NULL,
	product_id	 BIGINT,
	product_version BIGINT,
	PRIMARY KEY(product_id, product_version)
);

CREATE TABLE notification (
	id		 SERIAL,
	title	 VARCHAR(512) NOT NULL,
	description VARCHAR(512),
	PRIMARY KEY(id)
);

CREATE TABLE comment (
	id	 SERIAL,
	text	 VARCHAR(512) NOT NULL,
	parentid BIGINT,
	user_id		 BIGINT NOT NULL,
	product_id	 BIGINT NOT NULL,
	product_version	 BIGINT NOT NULL,
	notification_id	 BIGINT,
	PRIMARY KEY(notification_id)
);

CREATE TABLE item (
	quantity	 INTEGER NOT NULL,
	product_id	 BIGINT UNIQUE NOT NULL,
	product_version BIGINT UNIQUE NOT NULL,
	notification_id	 BIGINT,
	PRIMARY KEY(notification_id)
);

CREATE TABLE seller (
	company_name VARCHAR(512) NOT NULL,
	user_id	 BIGINT,
	PRIMARY KEY(user_id)
);

CREATE TABLE buyer (
	user_id BIGINT,
	PRIMARY KEY(user_id)
);

CREATE TABLE "order" (
	id		 SERIAL,
	order_timestamp TIMESTAMP NOT NULL,
	buyer_id	 BIGINT NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE classification (
	rating		 BIGINT,
	comment	 VARCHAR(512),
	buyer_id	 BIGINT,
	product_id	 BIGINT,
	product_version BIGINT,
	PRIMARY KEY(buyer_id, product_id, product_version)
);

CREATE TABLE admin (
	user_id BIGINT,
	PRIMARY KEY(user_id)
);

CREATE TABLE item_order (
	item_id BIGINT,
	order_id				 BIGINT NOT NULL,
	PRIMARY KEY(item_id)
);

-- Constraints

ALTER TABLE product ADD CONSTRAINT product_fk1 FOREIGN KEY (seller_id) REFERENCES seller(user_id);
ALTER TABLE computer ADD CONSTRAINT computer_fk2 FOREIGN KEY (product_id, product_version) REFERENCES product(id, version);
ALTER TABLE television ADD CONSTRAINT television_fk2 FOREIGN KEY (product_id, product_version) REFERENCES product(id, version);
ALTER TABLE comment ADD CONSTRAINT comment_fk1 FOREIGN KEY (user_id) REFERENCES "user"(id);
ALTER TABLE comment ADD CONSTRAINT comment_fk2 FOREIGN KEY (product_id, product_version) REFERENCES product(id, version);
ALTER TABLE comment ADD CONSTRAINT comment_fk4 FOREIGN KEY (notification_id) REFERENCES notification(id);
ALTER TABLE item ADD CONSTRAINT item_fk1 FOREIGN KEY (notification_id) REFERENCES notification(id);
ALTER TABLE seller ADD CONSTRAINT seller_fk1 FOREIGN KEY (user_id) REFERENCES "user"(id);
ALTER TABLE buyer ADD CONSTRAINT buyer_fk1 FOREIGN KEY (user_id) REFERENCES "user"(id);
ALTER TABLE "order" ADD CONSTRAINT order_fk1 FOREIGN KEY (buyer_id) REFERENCES buyer(user_id);
ALTER TABLE classification ADD CONSTRAINT classification_fk2 FOREIGN KEY (product_id, product_version) REFERENCES product(id, version);
ALTER TABLE classification ADD CONSTRAINT classification_fk4 FOREIGN KEY (buyer_id) REFERENCES buyer(user_id);
ALTER TABLE admin ADD CONSTRAINT admin_fk1 FOREIGN KEY (user_id) REFERENCES "user"(id);
ALTER TABLE item_order ADD CONSTRAINT item_order_fk1 FOREIGN KEY (item_id) REFERENCES item(notification_id);
ALTER TABLE item_order ADD CONSTRAINT item_order_fk2 FOREIGN KEY (order_id) REFERENCES "order"(id);

-- Indexes

-- FK indexes
CREATE UNIQUE INDEX IF NOT EXISTS ClassificationProductFK
ON classification(product_id, product_version);

CREATE UNIQUE INDEX IF NOT EXISTS ClassificationBuyerFK
ON classification(buyer_id);

CREATE UNIQUE INDEX IF NOT EXISTS CommentUserFK
ON comment(user_id);

CREATE UNIQUE INDEX IF NOT EXISTS CommentProductFK
ON comment(product_id, product_version);

CREATE UNIQUE INDEX IF NOT EXISTS CommentNotificationFK
ON comment(notification_id);

CREATE UNIQUE INDEX IF NOT EXISTS ItemProductFK
ON item(product_id, product_version);

CREATE UNIQUE INDEX IF NOT EXISTS ItemOrderOrderFK
ON item_order(order_id);

CREATE UNIQUE INDEX IF NOT EXISTS OrderBuyerFK
ON "order"(buyer_id);

CREATE UNIQUE INDEX IF NOT EXISTS ProductSellerFK
ON product(seller_id);

CREATE UNIQUE INDEX IF NOT EXISTS SmartphoneProductFK
ON smartphone(product_id, product_version);

CREATE UNIQUE INDEX IF NOT EXISTS TelevisionProductFK
ON television(product_id, product_version);

-- Other indexes

CREATE INDEX ClassificationRating ON classification(rating);

CREATE INDEX ComputerCPU ON computer(cpu);

CREATE INDEX ComputerGPU ON computer(gpu);

CREATE INDEX ProductName ON product(name);

CREATE INDEX ProductPrice ON product(price);

CREATE INDEX ProductType ON product(type);

CREATE INDEX SellerCompanyName ON seller(company_name);

CREATE INDEX SmartphoneModel ON smartphone(model);

CREATE INDEX SmartphoneOS ON smartphone(operative_system);

CREATE INDEX TelevisionSize ON television(size);

CREATE INDEX TelevisionSize ON television(technology);

CREATE INDEX UserName ON "user"(name);

CREATE UNIQUE INDEX UserEmail ON "user"(email);

CREATE UNIQUE INDEX UserTIN ON "user"(tin);

CREATE UNIQUE INDEX UserPhoneNumber ON "user"(phone_number);

-- Triggers


-- Stored Procedures




-- DML

-- password: hello
INSERT INTO "user"
(id, name, first_name, email, tin, last_name, phone_number, password_hash, house_no, street_name, city, state, zip_code)
VALUES
(0, 'admin', 'Admin', 'admin@digitalbubble.com', '000000000', 'Administrator', 
 '+351999999999', 
 '9b71d224bd62f3785d96d46ad3ea3d73319bfbc2890caadae2dff72519673ca72323c3d99ba5c11d7c7acc6e14b8c5da0c4663475c2e5c3adef46f73bcdec043',
 1, 'Street', 'City', 'State', '1000-100');
 
 INSERT INTO "admin"
 (id)
 VALUES (0)