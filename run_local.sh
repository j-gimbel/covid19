#!/bin/sh
export SQLALCHEMY_DATABASE_URL=sqlite:///./database.db
uvicorn app.main:app
