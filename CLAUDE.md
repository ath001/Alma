# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project state

This repository is currently an empty scaffold. The only code present is [main.py](main.py), a placeholder entry point (`python main.py` prints a greeting). No backend, frontend, dependency manifests, build tooling, linters, or tests have been set up yet.

## What this project is meant to become

[project.txt](project.txt) contains the product/tech assignment this repo is meant to fulfill. Read it before starting substantial work. Summary:

- A "lead" intake app: a public form (first name, last name, email, resume/CV) for prospects.
- On submission, emails are sent to both the prospect and an attorney inside the company.
- An internal, auth-guarded UI lists leads with all submitted details.
- Each lead has a state: starts `PENDING`, transitions to `REACHED_OUT` when an attorney manually marks it after reaching out.
- Required stack: **FastAPI** for the API, **Next.js** for the web app, a persistence layer, and an email service integration.
- Code should be structured like a production-level repo (not a toy layout) — expect a proper split between the FastAPI backend and the Next.js frontend as those are added.

Since none of this exists yet, treat architectural decisions (repo layout, DB choice, email provider, auth approach) as open — check with the user before committing to one if it isn't already specified elsewhere in the conversation.

## Changelog

Whenever you make a commit that changes code, add an entry to [CHANGELOG.md](CHANGELOG.md) in the same commit describing what changed and why.

## Conversation log

Keep [CONVERSATION_LOG.md](CONVERSATION_LOG.md) up to date: at the end of a session (or after a meaningful chunk of work), append a brief dated summary of what was asked and what was done. It's a summary log, not a full transcript — keep entries short.
