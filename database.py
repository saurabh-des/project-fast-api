from fastapi import FastAPI, HTTPException, Path, Query, Depends
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Literal
from datetime import datetime
from sqlalchemy import (
    create_engine, Column, BigInteger, String, Integer,
    Enum, DateTime
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import enum

DATABASE_URL = "mysql+mysqlclient://root:password@localhost:3306/mydatabase"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()



