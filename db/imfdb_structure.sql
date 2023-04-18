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
-- Name: actorimages; Type: TABLE; Schema: public; Owner: imfdb
--

CREATE TABLE public.actorimages (
    actorimageid uuid DEFAULT gen_random_uuid() NOT NULL,
    imageurl character varying NOT NULL,
    actorid uuid NOT NULL
);


ALTER TABLE public.actorimages OWNER TO imfdb;

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
-- Name: firearmimages; Type: TABLE; Schema: public; Owner: imfdb
--

CREATE TABLE public.firearmimages (
    firearmimageid uuid DEFAULT gen_random_uuid() NOT NULL,
    imageurl character varying NOT NULL,
    firearmid uuid NOT NULL
);


ALTER TABLE public.firearmimages OWNER TO imfdb;

--
-- Name: firearms; Type: TABLE; Schema: public; Owner: imfdb
--

CREATE TABLE public.firearms (
    firearmid uuid DEFAULT gen_random_uuid() NOT NULL,
    firearmurl character varying,
    parentfirearmid uuid,
    firearmpageid character varying NOT NULL,
    firearmpagecontent character varying,
    specificationid uuid,
    firearmtitle character varying NOT NULL,
    firearmversion character varying,
    isfamily boolean,
    isfictional boolean DEFAULT false
);


ALTER TABLE public.firearms OWNER TO imfdb;

--
-- Name: COLUMN firearms.firearmtitle; Type: COMMENT; Schema: public; Owner: imfdb
--

COMMENT ON COLUMN public.firearms.firearmtitle IS 'Page title / name';


--
-- Name: COLUMN firearms.firearmversion; Type: COMMENT; Schema: public; Owner: imfdb
--

COMMENT ON COLUMN public.firearms.firearmversion IS 'For example, ''Non-firing Replica'', ''Civilian Version'', ''Soviet Version''';


--
-- Name: COLUMN firearms.isfamily; Type: COMMENT; Schema: public; Owner: imfdb
--

COMMENT ON COLUMN public.firearms.isfamily IS 'This entry refers to a series or family';


--
-- Name: COLUMN firearms.isfictional; Type: COMMENT; Schema: public; Owner: imfdb
--

COMMENT ON COLUMN public.firearms.isfictional IS 'Entirely fictional or fake prop gun';


--
-- Name: movieimages; Type: TABLE; Schema: public; Owner: imfdb
--

CREATE TABLE public.movieimages (
    movieimageid uuid DEFAULT gen_random_uuid() NOT NULL,
    imageurl character varying NOT NULL,
    movieid uuid NOT NULL
);


ALTER TABLE public.movieimages OWNER TO imfdb;

--
-- Name: movies; Type: TABLE; Schema: public; Owner: imfdb
--

CREATE TABLE public.movies (
    movieid uuid DEFAULT gen_random_uuid() NOT NULL,
    movietitle character varying NOT NULL,
    movieurl character varying,
    moviepageid character varying NOT NULL,
    moviepagecontent character varying
);


ALTER TABLE public.movies OWNER TO imfdb;

--
-- Name: movies_actors_firearms; Type: TABLE; Schema: public; Owner: imfdb
--

CREATE TABLE public.movies_actors_firearms (
    movieid uuid NOT NULL,
    firearmid uuid NOT NULL,
    moviesactorsfirearmsid uuid DEFAULT gen_random_uuid() NOT NULL,
    "character" character varying,
    note character varying,
    year smallint,
    actorid uuid
);


ALTER TABLE public.movies_actors_firearms OWNER TO imfdb;

--
-- Name: COLUMN movies_actors_firearms."character"; Type: COMMENT; Schema: public; Owner: imfdb
--

COMMENT ON COLUMN public.movies_actors_firearms."character" IS 'Name of the role the actor played';


--
-- Name: COLUMN movies_actors_firearms.note; Type: COMMENT; Schema: public; Owner: imfdb
--

COMMENT ON COLUMN public.movies_actors_firearms.note IS 'Any additional information';


--
-- Name: COLUMN movies_actors_firearms.year; Type: COMMENT; Schema: public; Owner: imfdb
--

COMMENT ON COLUMN public.movies_actors_firearms.year IS 'Year of the appearance';


--
-- Name: redirects; Type: TABLE; Schema: public; Owner: imfdb
--

CREATE TABLE public.redirects (
    redirectid character varying DEFAULT gen_random_uuid() NOT NULL,
    totitle character varying NOT NULL,
    topageid character varying NOT NULL,
    fromtitle character varying NOT NULL,
    frompageid character varying NOT NULL
);


ALTER TABLE public.redirects OWNER TO imfdb;

--
-- Name: TABLE redirects; Type: COMMENT; Schema: public; Owner: imfdb
--

COMMENT ON TABLE public.redirects IS 'Keeps track of MediaWiki page redirects';


--
-- Name: specifications; Type: TABLE; Schema: public; Owner: imfdb
--

CREATE TABLE public.specifications (
    specificationid uuid DEFAULT gen_random_uuid() NOT NULL,
    firearmid uuid NOT NULL,
    type character varying,
    caliber character varying,
    capacity character varying,
    caliberlist character varying,
    capacitylist character varying,
    firemode character varying,
    productiontimeframe character varying
);


ALTER TABLE public.specifications OWNER TO imfdb;

--
-- Name: TABLE specifications; Type: COMMENT; Schema: public; Owner: imfdb
--

COMMENT ON TABLE public.specifications IS 'Firearm specifications';


--
-- Name: COLUMN specifications.firearmid; Type: COMMENT; Schema: public; Owner: imfdb
--

COMMENT ON COLUMN public.specifications.firearmid IS 'The UUID of the firearm this spec belongs to';


--
-- Name: COLUMN specifications.type; Type: COMMENT; Schema: public; Owner: imfdb
--

COMMENT ON COLUMN public.specifications.type IS 'Firearm type. For example: ''Revolver'', ''Battle Rifle'', ''Pistol''';


--
-- Name: COLUMN specifications.caliber; Type: COMMENT; Schema: public; Owner: imfdb
--

COMMENT ON COLUMN public.specifications.caliber IS 'Original caliber';


--
-- Name: COLUMN specifications.capacity; Type: COMMENT; Schema: public; Owner: imfdb
--

COMMENT ON COLUMN public.specifications.capacity IS 'Original capacity';


--
-- Name: COLUMN specifications.caliberlist; Type: COMMENT; Schema: public; Owner: imfdb
--

COMMENT ON COLUMN public.specifications.caliberlist IS 'List of compatible cartridge types';


--
-- Name: COLUMN specifications.capacitylist; Type: COMMENT; Schema: public; Owner: imfdb
--

COMMENT ON COLUMN public.specifications.capacitylist IS 'List of capacities for available magazines, clips, drums or chambers';


--
-- Name: COLUMN specifications.firemode; Type: COMMENT; Schema: public; Owner: imfdb
--

COMMENT ON COLUMN public.specifications.firemode IS 'List of available fire modes. For example: ''semi-automatic (double action)'', ''3-round burst''';


--
-- Name: tvseries; Type: TABLE; Schema: public; Owner: imfdb
--

CREATE TABLE public.tvseries (
    tvseriesid uuid DEFAULT gen_random_uuid() NOT NULL,
    tvseriestitle character varying NOT NULL,
    tvseriesurl character varying,
    tvseriespageid character varying NOT NULL,
    tvseriespagecontent character varying
);


ALTER TABLE public.tvseries OWNER TO imfdb;

--
-- Name: tvseries_actors_firearms; Type: TABLE; Schema: public; Owner: imfdb
--

CREATE TABLE public.tvseries_actors_firearms (
    tvseriesid uuid NOT NULL,
    firearmid uuid NOT NULL,
    tvseriesactorsfirearmsid uuid DEFAULT gen_random_uuid() NOT NULL,
    "character" character varying,
    note character varying,
    year character varying,
    actorid uuid NOT NULL
);


ALTER TABLE public.tvseries_actors_firearms OWNER TO imfdb;

--
-- Name: COLUMN tvseries_actors_firearms."character"; Type: COMMENT; Schema: public; Owner: imfdb
--

COMMENT ON COLUMN public.tvseries_actors_firearms."character" IS 'Name of the role the actor played';


--
-- Name: COLUMN tvseries_actors_firearms.note; Type: COMMENT; Schema: public; Owner: imfdb
--

COMMENT ON COLUMN public.tvseries_actors_firearms.note IS 'Any additional information';


--
-- Name: COLUMN tvseries_actors_firearms.year; Type: COMMENT; Schema: public; Owner: imfdb
--

COMMENT ON COLUMN public.tvseries_actors_firearms.year IS 'Year of the appearance';


--
-- Name: tvseriesimages; Type: TABLE; Schema: public; Owner: imfdb
--

CREATE TABLE public.tvseriesimages (
    tvseriesimageid uuid DEFAULT gen_random_uuid() NOT NULL,
    imageurl character varying NOT NULL,
    tvseriesid uuid NOT NULL
);


ALTER TABLE public.tvseriesimages OWNER TO imfdb;

--
-- Name: actors actors_pk; Type: CONSTRAINT; Schema: public; Owner: imfdb
--

ALTER TABLE ONLY public.actors
    ADD CONSTRAINT actors_pk PRIMARY KEY (actorid);


--
-- Name: firearmimages firearmimages_pk; Type: CONSTRAINT; Schema: public; Owner: imfdb
--

ALTER TABLE ONLY public.firearmimages
    ADD CONSTRAINT firearmimages_pk PRIMARY KEY (firearmimageid);


--
-- Name: firearms firearms_pk; Type: CONSTRAINT; Schema: public; Owner: imfdb
--

ALTER TABLE ONLY public.firearms
    ADD CONSTRAINT firearms_pk PRIMARY KEY (firearmid);


--
-- Name: actorimages images_pk; Type: CONSTRAINT; Schema: public; Owner: imfdb
--

ALTER TABLE ONLY public.actorimages
    ADD CONSTRAINT images_pk PRIMARY KEY (actorimageid);


--
-- Name: movieimages movieimages_pk; Type: CONSTRAINT; Schema: public; Owner: imfdb
--

ALTER TABLE ONLY public.movieimages
    ADD CONSTRAINT movieimages_pk PRIMARY KEY (movieimageid);


--
-- Name: movies_actors_firearms movies_actors_firearms_pk; Type: CONSTRAINT; Schema: public; Owner: imfdb
--

ALTER TABLE ONLY public.movies_actors_firearms
    ADD CONSTRAINT movies_actors_firearms_pk PRIMARY KEY (moviesactorsfirearmsid);


--
-- Name: movies movies_pk; Type: CONSTRAINT; Schema: public; Owner: imfdb
--

ALTER TABLE ONLY public.movies
    ADD CONSTRAINT movies_pk PRIMARY KEY (movieid);


--
-- Name: redirects redirects_pk; Type: CONSTRAINT; Schema: public; Owner: imfdb
--

ALTER TABLE ONLY public.redirects
    ADD CONSTRAINT redirects_pk PRIMARY KEY (redirectid);


--
-- Name: specifications specifications_pk; Type: CONSTRAINT; Schema: public; Owner: imfdb
--

ALTER TABLE ONLY public.specifications
    ADD CONSTRAINT specifications_pk PRIMARY KEY (specificationid);


--
-- Name: tvseries_actors_firearms tvseries_actors_firearms_pk; Type: CONSTRAINT; Schema: public; Owner: imfdb
--

ALTER TABLE ONLY public.tvseries_actors_firearms
    ADD CONSTRAINT tvseries_actors_firearms_pk PRIMARY KEY (tvseriesactorsfirearmsid);


--
-- Name: tvseries tvseries_pk; Type: CONSTRAINT; Schema: public; Owner: imfdb
--

ALTER TABLE ONLY public.tvseries
    ADD CONSTRAINT tvseries_pk PRIMARY KEY (tvseriesid);


--
-- Name: tvseriesimages tvseriesimages_pk; Type: CONSTRAINT; Schema: public; Owner: imfdb
--

ALTER TABLE ONLY public.tvseriesimages
    ADD CONSTRAINT tvseriesimages_pk PRIMARY KEY (tvseriesimageid);


--
-- Name: firearmimages firearmimages_fk; Type: FK CONSTRAINT; Schema: public; Owner: imfdb
--

ALTER TABLE ONLY public.firearmimages
    ADD CONSTRAINT firearmimages_fk FOREIGN KEY (firearmid) REFERENCES public.firearms(firearmid);


--
-- Name: firearms firearms_fk; Type: FK CONSTRAINT; Schema: public; Owner: imfdb
--

ALTER TABLE ONLY public.firearms
    ADD CONSTRAINT firearms_fk FOREIGN KEY (parentfirearmid) REFERENCES public.firearms(firearmid) ON UPDATE SET NULL ON DELETE CASCADE;


--
-- Name: firearms firearms_spec_fk; Type: FK CONSTRAINT; Schema: public; Owner: imfdb
--

ALTER TABLE ONLY public.firearms
    ADD CONSTRAINT firearms_spec_fk FOREIGN KEY (specificationid) REFERENCES public.specifications(specificationid) ON UPDATE SET NULL ON DELETE CASCADE;


--
-- Name: actorimages images_fk; Type: FK CONSTRAINT; Schema: public; Owner: imfdb
--

ALTER TABLE ONLY public.actorimages
    ADD CONSTRAINT images_fk FOREIGN KEY (actorid) REFERENCES public.actors(actorid);


--
-- Name: movieimages movieimages_fk; Type: FK CONSTRAINT; Schema: public; Owner: imfdb
--

ALTER TABLE ONLY public.movieimages
    ADD CONSTRAINT movieimages_fk FOREIGN KEY (movieid) REFERENCES public.movies(movieid);


--
-- Name: movies_actors_firearms movies_actors_firearms_fk; Type: FK CONSTRAINT; Schema: public; Owner: imfdb
--

ALTER TABLE ONLY public.movies_actors_firearms
    ADD CONSTRAINT movies_actors_firearms_fk FOREIGN KEY (actorid) REFERENCES public.actors(actorid);


--
-- Name: movies_actors_firearms movies_actors_firearms_fk_1; Type: FK CONSTRAINT; Schema: public; Owner: imfdb
--

ALTER TABLE ONLY public.movies_actors_firearms
    ADD CONSTRAINT movies_actors_firearms_fk_1 FOREIGN KEY (movieid) REFERENCES public.movies(movieid);


--
-- Name: movies_actors_firearms movies_actors_firearms_fk_2; Type: FK CONSTRAINT; Schema: public; Owner: imfdb
--

ALTER TABLE ONLY public.movies_actors_firearms
    ADD CONSTRAINT movies_actors_firearms_fk_2 FOREIGN KEY (firearmid) REFERENCES public.firearms(firearmid);


--
-- Name: specifications specifications_fk; Type: FK CONSTRAINT; Schema: public; Owner: imfdb
--

ALTER TABLE ONLY public.specifications
    ADD CONSTRAINT specifications_fk FOREIGN KEY (firearmid) REFERENCES public.firearms(firearmid) ON UPDATE SET NULL ON DELETE CASCADE;


--
-- Name: tvseries_actors_firearms tvseries_actors_firearms_fk; Type: FK CONSTRAINT; Schema: public; Owner: imfdb
--

ALTER TABLE ONLY public.tvseries_actors_firearms
    ADD CONSTRAINT tvseries_actors_firearms_fk FOREIGN KEY (actorid) REFERENCES public.actors(actorid);


--
-- Name: tvseries_actors_firearms tvseries_actors_firearms_fk_1; Type: FK CONSTRAINT; Schema: public; Owner: imfdb
--

ALTER TABLE ONLY public.tvseries_actors_firearms
    ADD CONSTRAINT tvseries_actors_firearms_fk_1 FOREIGN KEY (tvseriesid) REFERENCES public.tvseries(tvseriesid);


--
-- Name: tvseries_actors_firearms tvseries_actors_firearms_fk_2; Type: FK CONSTRAINT; Schema: public; Owner: imfdb
--

ALTER TABLE ONLY public.tvseries_actors_firearms
    ADD CONSTRAINT tvseries_actors_firearms_fk_2 FOREIGN KEY (firearmid) REFERENCES public.firearms(firearmid);


--
-- Name: tvseriesimages tvseriesimages_fk; Type: FK CONSTRAINT; Schema: public; Owner: imfdb
--

ALTER TABLE ONLY public.tvseriesimages
    ADD CONSTRAINT tvseriesimages_fk FOREIGN KEY (tvseriesid) REFERENCES public.tvseries(tvseriesid);


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: pg_database_owner
--

GRANT ALL ON SCHEMA public TO imfdb;


--
-- PostgreSQL database dump complete
--

