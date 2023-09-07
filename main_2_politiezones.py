import logging
import os

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from EMInfraAPI.EMInfraImporter import EMInfraImporter
from EMInfraAPI.RequestHandler import RequestHandler
from EMInfraAPI.RequesterFactory import RequesterFactory
from EMInfraAPI.ResourceEnum import ResourceEnum
from EMInfraAPI.SettingsManager import SettingsManager
from ORM.Classes import Agent, Omgeving, AgentOmgeving
from ORM.Base import Base

if __name__ == '__main__':
    engine = create_engine('sqlite:///test.db', echo=True)
    Base.metadata.create_all(engine)



