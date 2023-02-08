--
-- PostgreSQL database dump
--

-- Dumped from database version 15.1
-- Dumped by pg_dump version 15.1

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: actors; Type: TABLE; Schema: public; Owner: imfdb
--

CREATE TABLE public.actors (
    actorid uuid DEFAULT gen_random_uuid() NOT NULL,
    actorurl character varying,
    actorpageid character varying NOT NULL,
    actorpagecontent character varying,
    actorname character varying NOT NULL
);


ALTER TABLE public.actors OWNER TO imfdb;

--
-- Name: COLUMN actors.actorpageid; Type: COMMENT; Schema: public; Owner: imfdb
--

COMMENT ON COLUMN public.actors.actorpageid IS 'The MediaWiki page ID associated with this actor on IMFDB';


--
-- Name: COLUMN actors.actorpagecontent; Type: COMMENT; Schema: public; Owner: imfdb
--

COMMENT ON COLUMN public.actors.actorpagecontent IS 'The HTML data of the actor page';


--
-- Name: COLUMN actors.actorname; Type: COMMENT; Schema: public; Owner: imfdb
--

COMMENT ON COLUMN public.actors.actorname IS 'Full name of the actor';


--
-- Name: actors actors_pk; Type: CONSTRAINT; Schema: public; Owner: imfdb
--

ALTER TABLE ONLY public.actors
    ADD CONSTRAINT actors_pk PRIMARY KEY (actorid);


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: pg_database_owner
--

GRANT ALL ON SCHEMA public TO imfdb;


--
-- PostgreSQL database dump complete
--

