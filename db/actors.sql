CREATE TABLE public.actors (
	actorid uuid NOT NULL,
	actorurl varchar NULL,
	actorpageid varchar NOT NULL,
	actorpagecontent varchar NULL,
	CONSTRAINT actors_pk PRIMARY KEY (actorid)
);

-- Column comments

COMMENT ON COLUMN public.actors.actorurl IS 'This contains the URL to the IMFDB page of any given Actor';
COMMENT ON COLUMN public.actors.actorpageid IS 'The MediaWiki page ID associated with this actor on IMFDB';
COMMENT ON COLUMN public.actors.actorpagecontent IS 'The HTML data of the actor page';