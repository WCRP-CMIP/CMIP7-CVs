# CMIP7 CVs

This repository contains the source data for CMIP7 controlled vocabularies (CVs).

## Viewing the CVs

The CVs are currently evolving rapidly in support of CMIP7.
We hope to soon be able to "freeze" them,
i.e. forbid alterations to values in the CVs
and only allow new values to be added to the CVs.
However, this is not currently the case so when you view the CVs,
you will likely also want to specify which version of the CVs you are looking at
in order to avoid confusion.
It is for exactly this reason that,
<!-- 
REVIEWERS: note that this link is dead.
It will go live when this MR is merged into main
(i.e. after the esgvoc branches become the main branches)
-->
when raising an [issue with the CVs values](https://github.com/WCRP-CMIP/CMIP7-CVs/issues/new?template=cv-value.md),
we ask you to specify how you were looking at the CVs
and also specify the underlying version of the CVs (if possible).

To view the CVs as they are used within CMIP, you have a few options.

### esgvoc

This is the authoritative tool for accessing the CVs.
All other ways of accessing the CVs are simply different 'views' of what comes from esgvoc.
Any view of the CVs that differs from esgvoc is either
a) wrong
or b) based on a different commit/snapshot of the CVs from the one that you are viewing via esgvoc
(e.g. your esgvoc installation is configured to use the 'latest' version of the CMIP7 CVs,
but you are looking at a view of the CVs from another tool that is based on an earlier version).
Its full documentation can be found at
[https://esgf.github.io/esgf-vocab/]().

At the time of writing
(noting that esgvoc is also being developed rapidly,
so the following text may quickly become out of date),
the docs that are most likely to be useful are:

1. [installation](https://esgf.github.io/esgf-vocab/user/introduction.html#installation)
1. [retrieving and inspecting values](https://esgf.github.io/esgf-vocab/how_to/get.html)

For example, to inspect the value of the 
`historical` and `piControl` experiments for CMIP7 on a unix-based system,
you could do something like

```sh
# create a virtual environment
$ python3 -m venv venv
# activate it
$ source venv/bin/activate
# install esgvoc's latest version
$ pip install esgvoc
# get the latest release of the CMIP7 CVs
# (note that this will not have incorporated
# any changes which are still sitting in pull requests into this repository,
# i.e. anything you see here: https://github.com/WCRP-CMIP/CMIP7-CVs/pulls)
$ esgvoc use cmip7@latest
# get the value of interest to us, e.g. historical
$ esgvoc get cmip7:experiment:historical
# Note that the `get` command requires IDs (all lowercase),
# not the experiment name as used in CMIP (e.g. in filenames).
# So this works
$ esgvoc get cmip7:experiment:picontrol
# This does not
$ esgvoc get cmip7:experiment:piControl
```

If you want to look at lots of CVs, doing it via the command line may not be your best option.
Fortunately, esgvoc offers a full Python API.
See [their docs](https://esgf.github.io/esgf-vocab/).
If you want an example of working with esgvoc's Python API to create a derived product,
see [the script used for creating CMOR tables](https://github.com/WCRP-CMIP/cmip7-cmor-tables/tree/main/tables-cvs/generate-cmor-cvs-table.py).

### CMOR tables

A subset of the CVs are used with the [cmor](https://github.com/PCMDI/cmor)
tool.
The subset required are formatted for CMOR in
[this repository](https://github.com/WCRP-CMIP/cmip7-cmor-tables),
specifically in [this file](https://github.com/WCRP-CMIP/cmip7-cmor-tables/tree/main/tables-cvs/cmor-cvs.json).
Updates are currently happening quite rapidly,
so please also check the
[pull requests](https://github.com/WCRP-CMIP/cmip7-cmor-tables/pulls)
if you want to see changes that are in the process of being incorporated.

<!--
### JSON-LD represenation

Add if we have a version of this we're happy with.
-->

## Altering (i.e. writing) the CVs

The values that underpin the CVs are kept in two separate repositories:

1. https://github.com/WCRP-CMIP/CMIP7-CVs
1. https://github.com/WCRP-CMIP/WCRP-universe

The full reasons for this are beyond the scope of this repository.
In very short, this split allows the CVs community to maximise re-use of terms
while recognising that some projects use different terms to mean the same thing
(or the same term to mean different things)
so simply enforcing consistency across all projects was not an option.
This way of working allows us to meet this need,
but it does complicate altering the CVs
(or understanding where the CVs values you see come from).

In order to alter the CVs,
you will need to understand (at least to some degree)
both the repositories listed above
as well as the interaction between them.

We go through some examples here.
If you want to understand the underlying structure,
see the 'theory' header below.

### Theory

Note that this is an attempt to summarise how this system works.
However, it is likely to leave you with some questions because:

1. the system is evolving rapidly so this text may quickly become out of date
1. this text is short and not exhaustive
1. the system is custom, it is close to how JSON-LD works but it isn't JSON-LD,
   so you can't google answers.
   To get authoritative answers, you have to look at what the esgvoc code does
   (or ask an AI coding tool to explain, they seem to able to parse the logic quite well).

In very short, for CMIP7 CVs, the CMIP7 CVs repository
(https://github.com/WCRP-CMIP/WCRP-universe/)
is the source with the highest priority.
Values set in the CMIP7 CVs repository are never changed.
The universe CVs repository
(https://github.com/WCRP-CMIP/WCRP-universe)
is an information source which the CMIP7 CVs repository can re-use.

For example,
<!--
REVIEWERS: suggestions for checking that these links are live,
particularly as we rename `esgvoc` branches to `main`,
are welcome (do we do this manually, add CI to check links are live, something else?).
-->
the entry that describes the `1pctCO2` experiment is very thin,
see [https://github.com/WCRP-CMIP/CMIP7-CVs/tree/esgvoc/experiment/1pctco2.json]().
It is actually mostly relying on the 'universe' definition of `1pctco2`,
see [https://github.com/WCRP-CMIP/WCRP-universe/tree/esgvoc/experiment/1pctco2.json](),
and only augmenting the fields shown in
[https://github.com/WCRP-CMIP/CMIP7-CVs/tree/esgvoc/experiment/1pctco2.json]().

In order to determine which universe values are used as the basis for each CMIP7 CV entry,
you must look at the `000_context.jsonld` file in the directory in which the CV is defined.
Continuing with our `1pctCO2` example, we must look at the `000_context.jsonld` file
in the same directory as the `1pctco2.json` file, i.e.
[https://github.com/WCRP-CMIP/CMIP7-CVs/tree/esgvoc/experiment/000_context.jsonld]().
In this file, there is lots of information.
The key bits are:

1. the value of `["@context"]["@base"]`. This tells you which directory from the universe
   are combined with the CMIP7 CVs entry to create the 'full' CV entry.
   At the moment, you have to replace `"https://esgvoc.ipsl.fr/resource/universe/"`
   with `"https://github.com/WCRP-CMIP/CMIP7-CVs/tree/esgvoc/"`
   to get the right path, but otherwise it works.
   E.g. in [https://github.com/WCRP-CMIP/CMIP7-CVs/tree/esgvoc/experiment/000_context.json]()
   you see that `["@context"]["@base"]`  is equal to
   `"https://esgvoc.ipsl.fr/resource/universe/experiment/"`,
   so we know that we need to look in 
   `"https://github.com/WCRP-CMIP/WCRP-universe/tree/esgvoc/experiment"`
   for the 'matching' entries.
    - In our example, this match is quite straightforward
      as we just use experiments from the universe too.
      However, the two names don't have to match.
      For example, if we look at 
      [https://github.com/WCRP-CMIP/CMIP7-CVs/tree/esgvoc/source/000_context.jsonld](),
      we see that CMIP7 CVs sources
      ([https://github.com/WCRP-CMIP/CMIP7-CVs/tree/esgvoc/source]())
      are based on universe models
      ([https://github.com/WCRP-CMIP/WCRP-universe/tree/esgvoc/model]()),
      not universe sources
      ([https://github.com/WCRP-CMIP/WCRP-universe/tree/esgvoc/source]()).

- from there, look at the model (normally comes from universe, but can come from project CVs, be careful)
- then you should be able to see the structure and can mostly ignore 000_context.jsonld otherwise
- if things explode or you can't understand, raise a [blank issue](https://github.com/WCRP-CMIP/CMIP7-CVs/issues/new?template=BLANK_ISSUE),
  describe what happened and tag @ltroussellier and @glevava who can then help
