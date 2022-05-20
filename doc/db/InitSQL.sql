-- DDL


CREATE TABLE IF NOT EXISTS public.admin
(
    user_id bigint NOT NULL,
    CONSTRAINT admin_pkey PRIMARY KEY (user_id)
);

CREATE TABLE IF NOT EXISTS public.buyer
(
    user_id bigint NOT NULL,
    CONSTRAINT buyer_pkey PRIMARY KEY (user_id)
);

CREATE TABLE IF NOT EXISTS public.classification
(
    rating bigint,
    comment character varying(512) COLLATE pg_catalog."default",
    buyer_id bigint NOT NULL,
    product_id bigint NOT NULL
);

CREATE TABLE IF NOT EXISTS public.comment
(
    id integer NOT NULL DEFAULT nextval('comment_id_seq'::regclass),
    text character varying(512) COLLATE pg_catalog."default" NOT NULL,
    parent_id bigint,
    user_id bigint NOT NULL,
    product_id bigint NOT NULL
);

CREATE TABLE IF NOT EXISTS public.computer
(
    cpu character varying(512) COLLATE pg_catalog."default" NOT NULL,
    gpu character varying(512) COLLATE pg_catalog."default",
    product_id bigint NOT NULL,
    product_version bigint
);

CREATE TABLE IF NOT EXISTS public.item
(
    quantity integer NOT NULL,
    product_id bigint NOT NULL,
    order_id bigint NOT NULL,
    CONSTRAINT item_product_id_key UNIQUE (product_id)
);

CREATE TABLE IF NOT EXISTS public.notification
(
    id integer NOT NULL DEFAULT nextval('notification_id_seq'::regclass),
    title character varying(512) COLLATE pg_catalog."default" NOT NULL,
    description character varying(512) COLLATE pg_catalog."default",
    user_id bigint,
    CONSTRAINT notification_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public."order"
(
    id integer NOT NULL DEFAULT nextval('order_id_seq'::regclass),
    order_timestamp timestamp without time zone NOT NULL,
    buyer_id bigint NOT NULL,
    is_complete boolean NOT NULL,
    CONSTRAINT order_pk1 PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.product
(
    id bigint NOT NULL,
    version bigint NOT NULL,
    name character varying(512) COLLATE pg_catalog."default" NOT NULL,
    price real NOT NULL,
    stock integer NOT NULL,
    description character varying(512) COLLATE pg_catalog."default",
    seller_id bigint NOT NULL,
    category character varying(256) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT product_pkey PRIMARY KEY (id, version),
    CONSTRAINT product_id_version_key UNIQUE (id, version)
);

CREATE TABLE IF NOT EXISTS public.seller
(
    company_name character varying(512) COLLATE pg_catalog."default" NOT NULL,
    user_id bigint NOT NULL,
    CONSTRAINT seller_pkey PRIMARY KEY (user_id)
);

CREATE TABLE IF NOT EXISTS public.smartphone
(
    model character varying(512) COLLATE pg_catalog."default" NOT NULL,
    operative_system character varying(512) COLLATE pg_catalog."default" NOT NULL,
    product_id bigint NOT NULL,
    product_version bigint NOT NULL
);

CREATE TABLE IF NOT EXISTS public.television
(
    size integer NOT NULL,
    technology character varying(512) COLLATE pg_catalog."default" NOT NULL,
    product_id bigint NOT NULL,
    product_version bigint NOT NULL
);

CREATE TABLE IF NOT EXISTS public."user"
(
    id integer NOT NULL DEFAULT nextval('user_id_seq'::regclass),
    user_name character varying(512) COLLATE pg_catalog."default" NOT NULL,
    first_name character varying(512) COLLATE pg_catalog."default" NOT NULL,
    email character varying(512) COLLATE pg_catalog."default" NOT NULL,
    tin character varying(512) COLLATE pg_catalog."default",
    last_name character varying(512) COLLATE pg_catalog."default" NOT NULL,
    phone_number character varying(512) COLLATE pg_catalog."default" NOT NULL,
    password_hash character varying(128) COLLATE pg_catalog."default" NOT NULL,
    house_no integer NOT NULL,
    street_name character varying(512) COLLATE pg_catalog."default" NOT NULL,
    city character varying(512) COLLATE pg_catalog."default" NOT NULL,
    state character varying(512) COLLATE pg_catalog."default" NOT NULL,
    zip_code character varying(64) COLLATE pg_catalog."default" NOT NULL,
    role integer NOT NULL,
    CONSTRAINT user_pkey PRIMARY KEY (id),
    CONSTRAINT user_email_key UNIQUE (email),
    CONSTRAINT user_name_key UNIQUE (user_name),
    CONSTRAINT user_phone_number_key UNIQUE (phone_number)
);

ALTER TABLE IF EXISTS public.buyer
    ADD CONSTRAINT buyer_fk1 FOREIGN KEY (user_id)
    REFERENCES public."user" (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;
CREATE INDEX IF NOT EXISTS buyer_pkey
    ON public.buyer(user_id);


ALTER TABLE IF EXISTS public.comment
    ADD CONSTRAINT comment_fk1 FOREIGN KEY (user_id)
    REFERENCES public."user" (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;
CREATE INDEX IF NOT EXISTS commentuserfk
    ON public.comment(user_id);


ALTER TABLE IF EXISTS public.computer
    ADD CONSTRAINT computer_fk1 FOREIGN KEY (product_version, product_id)
    REFERENCES public.product (version, id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;
CREATE INDEX IF NOT EXISTS fki_computer_fk1
    ON public.computer(product_version, product_id);


ALTER TABLE IF EXISTS public.notification
    ADD CONSTRAINT notification_fk1 FOREIGN KEY (user_id)
    REFERENCES public."user" (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;


ALTER TABLE IF EXISTS public.product
    ADD CONSTRAINT product_fk1 FOREIGN KEY (seller_id)
    REFERENCES public.seller (user_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;


ALTER TABLE IF EXISTS public.seller
    ADD CONSTRAINT seller_fk1 FOREIGN KEY (user_id)
    REFERENCES public."user" (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;
CREATE INDEX IF NOT EXISTS seller_pkey
    ON public.seller(user_id);


ALTER TABLE IF EXISTS public.smartphone
    ADD CONSTRAINT smartphone_fk1 FOREIGN KEY (product_version, product_id)
    REFERENCES public.product (version, id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;
CREATE INDEX IF NOT EXISTS fki_smartphone_fk1
    ON public.smartphone(product_version, product_id);


ALTER TABLE IF EXISTS public.television
    ADD CONSTRAINT television_fk1 FOREIGN KEY (product_version, product_id)
    REFERENCES public.product (version, id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;
CREATE INDEX IF NOT EXISTS fki_television_fk1
    ON public.television(product_version, product_id);

END;

-- Stored Procedures/Functions

CREATE OR REPLACE FUNCTION OnInsertOrder() RETURNS TRIGGER
LANGUAGE PLPGSQL
AS $$
DECLARE
	seller_id_ BIGINT;
	buyer_name VARCHAR;
	product_name VARCHAR;
	order_items CURSOR FOR
	SELECT product_id, quantity
	FROM item
	WHERE order_id = new.id;
BEGIN
	SELECT user_name
	FROM "user"
	WHERE id = NEW.buyer_id
	INTO buyer_name;

	FOR product IN order_items LOOP
		SELECT name, seller_id
		FROM product
		WHERE id = product.product_id
		INTO product_name, seller_id_;
		
		INSERT INTO notification
		(title, description, user_id)
		VALUES
		(FORMAT('Sold %s', product_name),
		FORMAT('%s units of product %s were bought by %s', product.quantity, product_name, buyer_name),
		seller_id_);
	END LOOP;
	
	RETURN NEW;
END;
$$

CREATE OR REPLACE FUNCTION OnInsertClassification() RETURNS TRIGGER
LANGUAGE PLPGSQL
AS $$
DECLARE
	seller_id_ BIGINT;
	product_name VARCHAR;
	buyer_name VARCHAR;
BEGIN
	SELECT user_name
	FROM "user"
	WHERE id = NEW.buyer_id
	INTO buyer_name;

	SELECT name, seller_id
	FROM product
	WHERE id = NEW.product_id
	INTO product_name, seller_id_;
	
	INSERT INTO notification
	(title, description, user_id)
	VALUES
	(FORMAT('%s was rated %s', product_name, NEW.rating),
	FORMAT('Product %s was rated %s by %s', product_name, NEW.rating, buyer_name),
	seller_id_);
	
	RETURN NEW;
END;
$$
-- Triggers

CREATE OR REPLACE TRIGGER OnInsertOrder
AFTER UPDATE ON "order"
FOR EACH ROW
WHEN (NEW.is_complete = '1')
EXECUTE FUNCTION OnInsertOrder()

CREATE OR REPLACE TRIGGER OnInsertClassification
AFTER INSERT ON classification
FOR EACH ROW
EXECUTE FUNCTION OnInsertClassification()

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